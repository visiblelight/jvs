import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.tick import TickLog, TickTask


# ── 周期计算 ──

def compute_period_key(frequency: str, dt: date) -> str:
    """根据频率和日期计算 period_key"""
    if frequency == "daily":
        return dt.isoformat()  # 2026-04-06
    elif frequency == "weekly":
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"  # 2026-W15
    elif frequency == "monthly":
        return dt.strftime("%Y-%m")  # 2026-04
    raise ValueError(f"Unknown frequency: {frequency}")


def _prev_period_key(frequency: str, period_key: str) -> str:
    """计算上一个周期的 period_key"""
    if frequency == "daily":
        d = date.fromisoformat(period_key)
        return (d - timedelta(days=1)).isoformat()
    elif frequency == "weekly":
        year, week = period_key.split("-W")
        d = date.fromisocalendar(int(year), int(week), 1)
        prev = d - timedelta(weeks=1)
        iso = prev.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    elif frequency == "monthly":
        year, month = period_key.split("-")
        y, m = int(year), int(month)
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        return f"{y:04d}-{m:02d}"
    raise ValueError(f"Unknown frequency: {frequency}")


def compute_streak(db: Session, task_id: int, frequency: str, current_period: str, include_current: bool = True) -> int:
    """计算连续打卡周期数。include_current=True 时，如果当前周期已打卡则计入。"""
    streak = 0
    pk = current_period

    if include_current:
        log = db.query(TickLog).filter(TickLog.task_id == task_id, TickLog.period_key == pk).first()
        if log:
            streak += 1
            pk = _prev_period_key(frequency, pk)
        else:
            return 0

    while True:
        log = db.query(TickLog).filter(TickLog.task_id == task_id, TickLog.period_key == pk).first()
        if log:
            streak += 1
            pk = _prev_period_key(frequency, pk)
        else:
            break

    return streak


def compute_points(points_rule: list[dict], streak: int) -> int:
    """根据阶梯积分规则和当前连续天数计算本次得分"""
    if not points_rule or streak <= 0:
        return 0
    sorted_rule = sorted(points_rule, key=lambda r: r["streak"])
    result = sorted_rule[-1]["points"]  # 默认最高档
    for r in sorted_rule:
        if streak <= r["streak"]:
            result = r["points"]
            break
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
    for k, v in kwargs.items():
        if v is None:
            continue
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


def enrich_task_out(db: Session, task: TickTask) -> dict:
    """将 TickTask ORM 对象转换为含统计字段的 dict"""
    today = datetime.now(timezone.utc).date()
    current_pk = compute_period_key(task.frequency, today)

    total_ticks = db.query(func.count(TickLog.id)).filter(TickLog.task_id == task.id).scalar() or 0
    total_points = db.query(func.coalesce(func.sum(TickLog.points_earned), 0)).filter(TickLog.task_id == task.id).scalar()
    ticked = db.query(TickLog).filter(TickLog.task_id == task.id, TickLog.period_key == current_pk).first()
    streak = compute_streak(db, task.id, task.frequency, current_pk, include_current=True)

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
        "ticked_this_period": ticked is not None,
    }


# ── 打卡 / 撤销 ──

def do_tick(
    db: Session,
    task: TickTask,
    user_id: int,
    quality: Optional[int] = None,
    note: Optional[str] = None,
) -> tuple[TickLog, int, int]:
    """执行打卡。返回 (log, current_streak, total_points)"""
    today = datetime.now(timezone.utc).date()
    pk = compute_period_key(task.frequency, today)

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
        ticked_at=datetime.now(timezone.utc),
        period_key=pk,
        quality=quality,
        note=note,
        points_earned=points,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

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
    today = datetime.now(timezone.utc).date()
    current_pk = compute_period_key(task.frequency, today)

    if period_key >= current_pk:
        raise ValueError("补打卡只能针对过去的周期")

    existing = db.query(TickLog).filter(TickLog.task_id == task.id, TickLog.period_key == period_key).first()
    if existing:
        raise ValueError("该周期已有打卡记录")

    log = TickLog(
        user_id=user_id,
        task_id=task.id,
        ticked_at=datetime.now(timezone.utc),
        period_key=period_key,
        note=note,
        quality=quality,
        points_earned=0,
        is_makeup=True,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def undo_tick(db: Session, task: TickTask) -> None:
    """撤销当前周期的打卡"""
    today = datetime.now(timezone.utc).date()
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
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[TickLog]:
    q = db.query(TickLog).filter(TickLog.user_id == user_id)
    if start_date:
        q = q.filter(func.date(TickLog.ticked_at) >= start_date)
    if end_date:
        q = q.filter(func.date(TickLog.ticked_at) <= end_date)
    return q.order_by(TickLog.ticked_at.asc()).all()
