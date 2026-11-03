import json
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from collections import defaultdict
from typing import Optional

from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.core.config import settings
from app.core.datetime import utc_now, business_today
from app.services.tick_periods import compute_period_key, period_bounds, previous_period, streak_from_keys, check_task_period
from sqlalchemy.orm import Session

from app.models.tick import TickLog, TickTask


# ── 周期计算 ──

_prev_period_key = previous_period


def compute_streak(db: Session, task_id: int, frequency: str, current_period: str, include_current: bool = True) -> int:
    keys = {key for (key,) in db.query(TickLog.period_key).filter(TickLog.task_id == task_id)}
    start = current_period if include_current else previous_period(frequency, current_period)
    return streak_from_keys(keys, frequency, start)


def compute_points(points_rule: list[dict], streak: int) -> int:
    """根据阶梯积分规则和当前连续天数计算本次得分"""
    if not points_rule or streak <= 0:
        return 0
    result = 0
    for rule in sorted(points_rule, key=lambda r: r["streak"]):
        if rule["streak"] > streak:
            break
        result = rule["points"]
    return result


def _parse_json_field(value: str) -> list | dict:
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


# ── 任务 CRUD ──

def get_tasks(
    db: Session,
    user_id: int,
    is_archived: Optional[bool] = None,
) -> list[TickTask]:
    q = db.query(TickTask).filter(TickTask.user_id == user_id)
    if is_archived is not None:
        q = q.filter(TickTask.is_archived == is_archived)
    return q.order_by(TickTask.created_at.desc()).all()


def create_task(db: Session, user_id: int, **kwargs) -> TickTask:
    frequency_config = kwargs.pop("frequency_config", {})
    points_rule = kwargs.pop("points_rule", [])
    task = TickTask(
        user_id=user_id,
        frequency_config=json.dumps(frequency_config),
        points_rule=json.dumps(points_rule),
        **kwargs,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: TickTask, **kwargs) -> TickTask:
    start = kwargs.get("start_date", task.start_date)
    end = kwargs.get("end_date", task.end_date)
    if end is not None and end < start:
        raise HTTPException(status_code=422, detail="结束日期不能早于开始日期")
    if kwargs.get("frequency", task.frequency) != task.frequency and db.query(TickLog.id).filter(TickLog.task_id == task.id).first():
        raise HTTPException(status_code=400, detail="已有打卡记录的任务不能修改频率，请创建新任务")
    for k, v in kwargs.items():
        if k == "frequency_config":
            setattr(task, k, json.dumps(v))
        elif k == "points_rule":
            setattr(task, k, json.dumps(v))
        else:
            setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: TickTask) -> None:
    db.delete(task)
    db.commit()


def enrich_tasks_out(db, tasks, now=None):
    now = now or utc_now()
    grouped = defaultdict(list)
    if tasks:
        for row in db.query(TickLog.task_id, TickLog.period_key, TickLog.points_earned).filter(TickLog.task_id.in_([t.id for t in tasks])):
            grouped[row.task_id].append(row)
    return [enrich_task_out(db, task, rows=grouped[task.id], now=now) for task in tasks]


def enrich_task_out(db: Session, task: TickTask, rows=None, now=None) -> dict:
    today = business_today(now or utc_now())
    current_pk = compute_period_key(task.frequency, today)
    if rows is None:
        rows = db.query(TickLog.period_key, TickLog.points_earned).filter(TickLog.task_id == task.id).all()
    keys = {row.period_key for row in rows}
    total_ticks = len(rows)
    total_points = sum(row.points_earned for row in rows)
    ticked = current_pk in keys
    start = current_pk if ticked else previous_period(task.frequency, current_pk)
    streak = streak_from_keys(keys, task.frequency, start)

    return {
        "id": task.id,
        "title": task.title,
        "short_name": task.short_name,
        "description": task.description,
        "frequency": task.frequency,
        "frequency_config": _parse_json_field(task.frequency_config),
        "start_date": task.start_date,
        "end_date": task.end_date,
        "enable_quality": task.enable_quality,
        "enable_points": task.enable_points,
        "points_rule": _parse_json_field(task.points_rule),
        "is_archived": task.is_archived,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "total_ticks": total_ticks,
        "current_streak": streak,
        "total_points": total_points,
        "ticked_this_period": ticked,
    }


def _save_log(db, log):
    db.add(log)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "uq_tick_log_task_period" or "UNIQUE constraint failed: tick_logs.task_id, tick_logs.period_key" in str(exc.orig):
            raise ValueError("当前周期已打卡") from exc
        raise
    db.refresh(log)


# ── 打卡 / 撤销 ──

def do_tick(
    db: Session,
    task: TickTask,
    user_id: int,
    quality: Optional[int] = None,
    note: Optional[str] = None,
) -> tuple[TickLog, int, int]:
    """执行打卡。返回 (log, current_streak, total_points)"""
    now = utc_now()
    today = business_today(now)
    pk = compute_period_key(task.frequency, today)
    if task.is_archived:
        raise ValueError("任务已归档，无法打卡")
    if today < task.start_date:
        raise ValueError("任务尚未开始")
    if task.end_date and today > task.end_date:
        raise ValueError("任务已结束")

    # 检查是否已打卡
    existing = db.query(TickLog).filter(TickLog.task_id == task.id, TickLog.period_key == pk).first()
    if existing:
        raise ValueError("当前周期已打卡")

    # 计算 streak：上一个周期往前的连续次数 + 1（本次）
    prev_pk = _prev_period_key(task.frequency, pk)
    prev_streak = compute_streak(db, task.id, task.frequency, prev_pk, include_current=True)
    new_streak = prev_streak + 1

    # 计算积分
    points = 0
    if task.enable_points:
        rules = _parse_json_field(task.points_rule)
        points = compute_points(rules, new_streak)

    log = TickLog(
        user_id=user_id,
        task_id=task.id,
        ticked_at=now,
        period_key=pk,
        quality=quality,
        note=note,
        points_earned=points,
    )
    _save_log(db, log)

    total_points = db.query(func.coalesce(func.sum(TickLog.points_earned), 0)).filter(TickLog.task_id == task.id).scalar()

    return log, new_streak, total_points


def makeup_tick(
    db: Session,
    task: TickTask,
    user_id: int,
    period_key: str,
    note: Optional[str] = None,
    quality: Optional[int] = None,
) -> TickLog:
    """补打卡：写入历史周期，得 0 分，标记 is_makeup=True"""
    now = utc_now()
    today = business_today(now)
    current_pk = compute_period_key(task.frequency, today)

    if task.is_archived:
        raise ValueError("任务已归档，无法补打卡")
    start, _ = check_task_period(task, period_key)
    current_start, _ = period_bounds(task.frequency, current_pk)
    if start >= current_start:
        raise ValueError("补打卡只能针对过去的周期")

    existing = db.query(TickLog).filter(TickLog.task_id == task.id, TickLog.period_key == period_key).first()
    if existing:
        raise ValueError("该周期已有打卡记录")

    log = TickLog(
        user_id=user_id,
        task_id=task.id,
        ticked_at=now,
        period_key=period_key,
        note=note,
        quality=quality,
        points_earned=0,
        is_makeup=True,
    )
    _save_log(db, log)
    return log


def undo_tick(db: Session, task: TickTask) -> None:
    """撤销当前周期的打卡"""
    now = utc_now()
    today = business_today(now)
    pk = compute_period_key(task.frequency, today)
    log = db.query(TickLog).filter(TickLog.task_id == task.id, TickLog.period_key == pk).first()
    if not log:
        raise ValueError("当前周期未打卡")
    db.delete(log)
    db.commit()


# ── 日志查询 ──

def get_logs(
    db: Session,
    task_id: int,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[TickLog], int]:
    q = db.query(TickLog).filter(TickLog.task_id == task_id, TickLog.user_id == user_id)
    total = q.count()
    items = q.order_by(TickLog.ticked_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_all_logs(
    db: Session, user_id: int, start_date: Optional[date] = None,
    end_date: Optional[date] = None, date_basis: str = "submitted",
) -> list[TickLog]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="结束日期不能早于开始日期")
    q = db.query(TickLog).join(TickTask).filter(TickLog.user_id == user_id, TickTask.user_id == user_id)
    if date_basis == "calendar":
        # Period overlap includes late makeups AND weekly/monthly logs needed
        # to calculate completion markers outside their actual submission day.
        conditions = []
        for frequency in ("daily", "weekly", "monthly"):
            parts = [TickTask.frequency == frequency]
            if start_date:
                parts.append(TickLog.period_key >= compute_period_key(frequency, start_date))
            if end_date:
                parts.append(TickLog.period_key <= compute_period_key(frequency, end_date))
            conditions.append(and_(*parts))
        q = q.filter(or_(*conditions))
    else:
        zone = ZoneInfo(settings.BUSINESS_TIMEZONE)
        if start_date:
            q = q.filter(TickLog.ticked_at >= datetime.combine(start_date, time.min, zone))
        if end_date:
            if end_date < date.max:
                q = q.filter(TickLog.ticked_at < datetime.combine(end_date + timedelta(days=1), time.min, zone))
    return q.order_by(TickLog.ticked_at.asc()).all()
