"""Preview/apply/restore reviewed tick-period mappings. Does not alter timestamps or points.

python -m scripts.migrate_tick_timezone > /safe/location/tick-report.json
python -m scripts.migrate_tick_timezone --apply /safe/location/tick-report.json
python -m scripts.migrate_tick_timezone --restore /safe/location/tick-report.json

Stop tick writes and back up the database before applying/restoring a report.
The report contains a full ID/period/time/points snapshot to reject stale plans.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.datetime import as_utc
from app.models.tick import TickTask, TickLog
from app.services.tick_periods import compute_period_key, check_task_period


def snapshot(db):
    tasks = db.query(TickTask).order_by(TickTask.id).all()
    logs = db.query(TickLog).order_by(TickLog.id).all()
    task_rows = [dict(id=t.id, user_id=t.user_id, frequency=t.frequency,
                      start_date=t.start_date.isoformat(), end_date=t.end_date.isoformat() if t.end_date else None)
                 for t in tasks]
    log_rows = [dict(id=l.id, task_id=l.task_id, user_id=l.user_id, period_key=l.period_key,
                     ticked_at=as_utc(l.ticked_at).isoformat(), points_earned=l.points_earned, is_makeup=l.is_makeup)
                for l in logs]
    return tasks, logs, dict(tasks=task_rows, logs=log_rows)


def build_report(db, timezone='Asia/Shanghai'):
    zone = ZoneInfo(timezone)
    tasks, logs, state = snapshot(db)
    task_map = {t.id:t for t in tasks}
    changes, issues = [], []
    occupied = defaultdict(list)
    for log in logs:
        task = task_map.get(log.task_id)
        if task is None or task.user_id != log.user_id:
            issues.append(dict(id=log.id, reason='invalid_task_owner'))
            continue
        new_key = log.period_key if log.is_makeup else compute_period_key(task.frequency, as_utc(log.ticked_at).astimezone(zone).date())
        try:
            check_task_period(task, new_key)
        except ValueError as exc:
            issues.append(dict(id=log.id, reason=str(exc)))
        occupied[(task.id,new_key)].append(log.id)
        if new_key != log.period_key:
            changes.append(dict(id=log.id, task_id=task.id, old=log.period_key, new=new_key))
    for (task_id,key), ids in occupied.items():
        if len(ids)>1:
            issues.append(dict(task_id=task_id, period_key=key, ids=ids, reason='collision'))
    return dict(version=1, timezone=timezone, snapshot=state, changes=changes, issues=issues)


def apply_report(db, report, restore=False):
    if report.get('version') != 1 or report.get('issues'):
        raise ValueError('报告版本无效或存在待处理冲突；未修改数据')
    # The CLI supplies a fresh session; locks cover validation and all updates.
    if db.bind.dialect.name == 'postgresql':
        db.execute(text('LOCK TABLE tick_tasks, tick_logs IN SHARE ROW EXCLUSIVE MODE'))
    elif db.bind.dialect.name == 'sqlite':
        db.execute(text('BEGIN IMMEDIATE'))
    if not restore:
        if build_report(db, report['timezone']) != report:
            raise ValueError('报告已过期或映射被修改；请重新预演')
    else:
        _, _, current = snapshot(db)
        expected = json.loads(json.dumps(report['snapshot']))
        mappings = {c['id']:c for c in report['changes']}
        for row in expected['logs']:
            if row['id'] in mappings:
                row['period_key'] = mappings[row['id']]['new']
        if current != expected:
            raise ValueError('切换后数据已变化，不能直接恢复旧映射')
    try:
        # Vacate all affected keys first: adjacent days can shift into each other.
        for change in report['changes']:
            db.execute(text('UPDATE tick_logs SET period_key=:key WHERE id=:id'),
                       dict(key='~'+format(change['id'], 'x'), id=change['id']))
        for change in report['changes']:
            db.execute(text('UPDATE tick_logs SET period_key=:key WHERE id=:id'),
                       dict(key=change['old'] if restore else change['new'], id=change['id']))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return len(report['changes'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timezone', default='Asia/Shanghai')
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--apply', type=Path)
    group.add_argument('--restore', type=Path)
    args=parser.parse_args()
    with SessionLocal() as db:
        if args.apply or args.restore:
            report=json.loads((args.apply or args.restore).read_text())
            count=apply_report(db,report,restore=bool(args.restore))
            print(json.dumps({'updated':count}))
        else:
            print(json.dumps(build_report(db,args.timezone),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
