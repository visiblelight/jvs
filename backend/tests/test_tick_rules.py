from datetime import date, datetime, timezone
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tick import TickTask, TickLog
from app.services import tick
from app.services.tick_periods import period_bounds
from scripts.migrate_tick_timezone import build_report, apply_report, snapshot
from tests.test_migrations import migration_url, run_alembic


@pytest.fixture
def frozen_now(monkeypatch):
    now = [datetime(2026, 11, 3, 16, 30, tzinfo=timezone.utc)]
    monkeypatch.setattr(tick, 'utc_now', lambda: now[0])
    return now


def task_url(client, headers, **kwargs):
    r=client.post('/api/admin/tick/tasks',headers=headers,json={'title':'rules','frequency':'daily','start_date':'2026-01-01',**kwargs})
    assert r.status_code==201, r.text
    return f"/api/admin/tick/tasks/{r.json()['id']}"


@pytest.mark.parametrize('key', ['0invalid','2026-02-30','2026-04','2026-1-01','2026-11-04','2026-11-05','2025-12-31'])
def test_invalid_makeup_periods(client, auth_headers, frozen_now, key):
    url=task_url(client,auth_headers)
    assert client.post(url+'/makeup',headers=auth_headers,json={'period_key':key}).status_code==400


def test_business_midnight_makeup_streak_and_historical_calendar(client, auth_headers, frozen_now):
    url=task_url(client,auth_headers,enable_points=True,points_rule=[{'streak':1,'points':1},{'streak':2,'points':5}])
    # Shanghai Nov 4, but still Nov 3 UTC.
    r=client.post(url+'/tick',headers=auth_headers,json={})
    assert r.json()['log']['period_key']=='2026-11-04'
    assert r.json()['log']['ticked_at'].endswith('Z')
    assert client.delete(url+'/tick',headers=auth_headers).status_code==204
    makeup=client.post(url+'/makeup',headers=auth_headers,json={'period_key':'2026-11-03'}).json()
    assert makeup['is_makeup'] and makeup['points_earned']==0
    assert client.post(url+'/tick',headers=auth_headers,json={}).json()['log']['points_earned']==5
    historical=client.post(url+'/makeup',headers=auth_headers,json={'period_key':'2026-03-01'}).json()
    params={'start_date':'2026-03-01','end_date':'2026-03-31','date_basis':'calendar'}
    logs=client.get('/api/admin/tick/logs',headers=auth_headers,params=params).json()['items']
    assert historical['id'] in [l['id'] for l in logs]
    params['date_basis']='submitted'
    assert client.get('/api/admin/tick/logs',headers=auth_headers,params=params).json()['items']==[]
    frozen_now[0]=datetime(2026,11,4,16,tzinfo=timezone.utc)
    assert client.get(url,headers=auth_headers).json()['ticked_this_period'] is False
    assert client.get(url,headers=auth_headers).json()['current_streak']==2


@pytest.mark.parametrize('frequency,key,start,end', [('weekly','2026-W01','2026-01-01','2026-01-02'),('monthly','2026-02','2026-02-15','2026-02-16')])
def test_partial_period_and_ended_task(client, auth_headers, frozen_now, frequency,key,start,end):
    url=task_url(client,auth_headers,frequency=frequency,start_date=start,end_date=end)
    assert client.post(url+'/makeup',headers=auth_headers,json={'period_key':key}).status_code==201
    assert client.post(url+'/makeup',headers=auth_headers,json={'period_key':key}).status_code==400
    assert client.put(url,headers=auth_headers,json={'frequency':'daily'}).status_code==400
    r=client.put(url,headers=auth_headers,json={'end_date':None,'description':None})
    assert r.status_code==200 and r.json()['end_date'] is None


def test_task_validation(client, auth_headers):
    base={'title':'x','frequency':'daily','start_date':'2026-01-01'}
    for extra in [{'end_date':'2025-12-31'},{'points_rule':[{}]},{'points_rule':[{'streak':1,'points':-1}]},{'points_rule':[{'streak':2,'points':2}]},{'short_name':'x'*11}]:
        assert client.post('/api/admin/tick/tasks',headers=auth_headers,json={**base,**extra}).status_code==422
    url=task_url(client,auth_headers)
    assert client.put(url,headers=auth_headers,json={'frequency':None}).status_code==422
    assert client.put(url,headers=auth_headers,json={'end_date':'2025-12-31'}).status_code==422


def test_period_calendar_boundaries():
    assert period_bounds('weekly','2026-W01')==(date(2025,12,29),date(2026,1,4))
    assert period_bounds('monthly','2024-02')==(date(2024,2,1),date(2024,2,29))
    for freq,key in [('weekly','2025-W53'),('monthly','2026-13'),('daily','2026-02-29')]:
        with pytest.raises(ValueError): period_bounds(freq,key)


def test_points_use_reached_threshold_not_future_tier():
    rules = [{'streak': 1, 'points': 1}, {'streak': 7, 'points': 10}]
    assert tick.compute_points(rules, 6) == 1
    assert tick.compute_points(rules, 7) == 10
    assert tick.compute_points(rules, 30) == 10


def seed_history(engine, collision=False):
    with Session(engine) as db:
        user=User(username='history',hashed_password='unused');db.add(user);db.flush()
        task=TickTask(user_id=user.id,title='history',frequency='daily',start_date=date(2026,1,1));db.add(task);db.flush()
        for day in [3,4]:
            db.add(TickLog(user_id=user.id,task_id=task.id,period_key=f'2026-11-{day:02d}',
                           ticked_at=datetime(2026,11,day,16,30,tzinfo=timezone.utc),
                           is_makeup=collision and day==4,points_earned=7))
        db.commit()


def test_historical_mapping_apply_restore_and_stale_guard(migration_url):
    run_alembic(migration_url,'upgrade','head')
    engine=create_engine(migration_url)
    seed_history(engine)
    with Session(engine) as db:
        report=build_report(db)
    assert not report['issues'] and len(report['changes'])==2
    with Session(engine) as db:
        assert apply_report(db,report)==2
    with Session(engine) as db:
        assert all(l.points_earned==7 for l in db.query(TickLog))
        assert {l.period_key for l in db.query(TickLog)}=={'2026-11-04','2026-11-05'}
    with Session(engine) as db:
        assert apply_report(db,report,restore=True)==2
    with Session(engine) as db:
        assert snapshot(db)[2]==report['snapshot']
    changed=json.loads(json.dumps(report));changed['changes'][0]['new']='2026-12-01'
    with Session(engine) as db, pytest.raises(ValueError,match='过期'):
        apply_report(db,changed)
    engine.dispose()


def test_historical_collision_never_overwrites(migration_url):
    run_alembic(migration_url,'upgrade','head')
    engine=create_engine(migration_url)
    seed_history(engine,collision=True)
    with Session(engine) as db:
        report=build_report(db)
        assert any(i['reason']=='collision' for i in report['issues'])
    with Session(engine) as db, pytest.raises(ValueError,match='冲突'):
        apply_report(db,report)
    with Session(engine) as db:
        assert snapshot(db)[2]==report['snapshot']
    engine.dispose()


def test_concurrent_duplicate_is_business_error(migration_url):
    if not migration_url.startswith('postgresql'):
        pytest.skip('Concurrent transaction test requires PostgreSQL')
    run_alembic(migration_url,'upgrade','head')
    engine=create_engine(migration_url)
    with Session(engine) as db:
        user=User(username='concurrent',hashed_password='unused');db.add(user);db.flush()
        task=TickTask(user_id=user.id,title='concurrent',frequency='daily',start_date=date(2020,1,1));db.add(task);db.commit()
        task_id,user_id=task.id,user.id
    barrier=Barrier(2)
    def before_insert(conn,cursor,statement,parameters,context,executemany):
        if statement.startswith('INSERT INTO tick_logs'):
            barrier.wait(timeout=10)
    event.listen(engine,'before_cursor_execute',before_insert)
    def submit():
        with Session(engine) as db:
            try:
                tick.do_tick(db,db.get(TickTask,task_id),user_id)
                return 'ok'
            except ValueError as exc:
                assert '已打卡' in str(exc)
                return 'duplicate'
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(lambda _:submit(),range(2)))==['duplicate','ok']
        with Session(engine) as db:
            assert db.query(TickLog).count()==1
    finally:
        event.remove(engine,'before_cursor_execute',before_insert)
        engine.dispose()
