from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.datetime import UTCDateTime, business_today
from app.models.user import User
from app.models.todo import TodoItem
from tests.test_migrations import migration_url, run_alembic


def test_timestamp_output_and_form_roundtrip(client, auth_headers):
    payload = {'title':'time','scheduled_at':'2026-11-03T13:00:00+08:00'}
    item=client.post('/api/admin/todo/items',headers=auth_headers,json=payload).json()
    assert item['scheduled_at'] == '2026-11-03T05:00:00Z'
    assert item['created_at'].endswith('Z')
    assert abs((datetime.now(timezone.utc)-datetime.fromisoformat(item['created_at'])).total_seconds()) < 10
    for _ in range(2):
        item=client.put(f"/api/admin/todo/items/{item['id']}",headers=auth_headers,json={'scheduled_at':item['scheduled_at']}).json()
        assert item['scheduled_at']=='2026-11-03T05:00:00Z'
    comment=client.post(f"/api/admin/todo/items/{item['id']}/comments",headers=auth_headers,json={'content':'time'}).json()
    assert comment['created_at'].endswith('Z')
    assert comment['updated_at'] == comment['created_at']
    assert client.get('/api/admin/auth/me',headers=auth_headers).json()['created_at'].endswith('Z')


def test_naive_http_dates_rejected_and_calendar_boundary(client, auth_headers):
    base='/api/admin/todo/items'
    assert client.post(base,headers=auth_headers,json={'title':'bad','due_date':'2026-11-03T13:00:00'}).status_code == 422
    assert client.post('/api/admin/news/articles',headers=auth_headers,json={'title':'bad','content':'x','published_at':'2026-11-03T13:00:00'}).status_code == 422
    for stamp in ['2026-11-03T23:59:59+08:00','2026-11-04T00:00:00+08:00','2026-11-04T00:30:00+08:00','2026-11-05T00:00:00+08:00']:
        assert client.post(base,headers=auth_headers,json={'title':stamp,'scheduled_at':stamp}).status_code==201
    params={'start':'2026-11-04T00:00:00+08:00','end':'2026-11-05T00:00:00+08:00'}
    r=client.get(base+'/calendar',headers=auth_headers,params=params)
    assert r.status_code == 200 and r.json()['total'] == 2
    params['start']='2026-11-04T00:00:00'
    assert client.get(base+'/calendar',headers=auth_headers,params=params).status_code==422


def test_shanghai_business_midnight():
    assert str(business_today(datetime(2026,11,3,15,59,59,tzinfo=timezone.utc)))=='2026-11-03'
    assert str(business_today(datetime(2026,11,3,16,tzinfo=timezone.utc)))=='2026-11-04'


def test_database_roundtrip_independent_of_session_timezone(migration_url):
    run_alembic(migration_url,'upgrade','head')
    engine=create_engine(migration_url)
    with Session(engine) as db:
        for zone in (['UTC','Asia/Shanghai','America/New_York'] if engine.dialect.name=='postgresql' else ['UTC']):
            if engine.dialect.name=='postgresql':
                db.execute(text('SET TIME ZONE :zone'), {'zone':zone})
            user=User(username=zone,hashed_password='unused')
            db.add(user);db.flush()
            instant=datetime(2026,11,3,13,tzinfo=timezone(timedelta(hours=8)))
            item=TodoItem(user_id=user.id,title=zone,scheduled_at=instant)
            db.add(item);db.commit();db.refresh(item)
            assert item.scheduled_at == datetime(2026,11,3,5,tzinfo=timezone.utc)
            raw=db.execute(text('SELECT scheduled_at FROM todo_items WHERE id=:id'),{'id':item.id}).scalar()
            assert str(raw).startswith('2026-11-03 05:00:00')
    engine.dispose()
