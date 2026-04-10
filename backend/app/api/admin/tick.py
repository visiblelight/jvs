from datetime import datetime, timezone, date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_module
from app.models.tick import TickTask
from app.models.user import User
from app.schemas.tick import (
    MakeupTickCreate,
    TickLogCreate,
    TickLogListOut,
    TickLogOut,
    TickResult,
    TickTaskCreate,
    TickTaskListOut,
    TickTaskOut,
    TickTaskUpdate,
)
from app.services import tick as tick_svc

router = APIRouter(
    prefix="/tick",
    tags=["admin-tick"],
    dependencies=[Depends(require_module("tick"))],
)


def _get_own_task(db: Session, task_id: int, user_id: int) -> TickTask:
    task = db.query(TickTask).filter(TickTask.id == task_id, TickTask.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="打卡任务不存在")
    return task


@router.get("/tasks", response_model=TickTaskListOut)
def list_tasks(
    is_archived: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = tick_svc.get_tasks(db, current_user.id, is_archived=is_archived)
    items = [tick_svc.enrich_task_out(db, t) for t in tasks]
    return TickTaskListOut(items=items, total=len(items))


@router.post("/tasks", response_model=TickTaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TickTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = tick_svc.create_task(db, current_user.id, **body.model_dump())
    return tick_svc.enrich_task_out(db, task)


@router.get("/tasks/{task_id}", response_model=TickTaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    return tick_svc.enrich_task_out(db, task)


@router.put("/tasks/{task_id}", response_model=TickTaskOut)
def update_task(
    task_id: int,
    body: TickTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    tick_svc.update_task(db, task, **body.model_dump(exclude_unset=True))
    return tick_svc.enrich_task_out(db, task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    tick_svc.delete_task(db, task)


@router.post("/tasks/{task_id}/tick", response_model=TickResult)
def do_tick(
    task_id: int,
    body: TickLogCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    if task.is_archived:
        raise HTTPException(status_code=400, detail="任务已归档，无法打卡")
    today = datetime.now(timezone.utc).date()
    if today < task.start_date:
        raise HTTPException(status_code=400, detail="任务尚未开始")
    if task.end_date and today > task.end_date:
        raise HTTPException(status_code=400, detail="任务已结束")

    quality = body.quality if body else None
    note = body.note if body else None

    try:
        log, streak, total_points = tick_svc.do_tick(db, task, current_user.id, quality=quality, note=note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TickResult(
        log=TickLogOut.model_validate(log),
        current_streak=streak,
        total_points=total_points,
    )


@router.post("/tasks/{task_id}/makeup", response_model=TickLogOut, status_code=status.HTTP_201_CREATED)
def makeup_tick(
    task_id: int,
    body: MakeupTickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    if task.is_archived:
        raise HTTPException(status_code=400, detail="任务已归档，无法补打卡")
    try:
        log = tick_svc.makeup_tick(db, task, current_user.id, body.period_key, note=body.note, quality=body.quality)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TickLogOut.model_validate(log)


@router.delete("/tasks/{task_id}/tick", status_code=status.HTTP_204_NO_CONTENT)
def undo_tick(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_own_task(db, task_id, current_user.id)
    try:
        tick_svc.undo_tick(db, task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}/logs", response_model=TickLogListOut)
def list_logs(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = _get_own_task(db, task_id, current_user.id)
    items, total = tick_svc.get_logs(db, task_id, current_user.id, page=page, page_size=page_size)
    return TickLogListOut(items=items, total=total)


@router.get("/logs", response_model=TickLogListOut)
def list_all_logs(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = tick_svc.get_all_logs(db, current_user.id, start_date=start_date, end_date=end_date)
    return TickLogListOut(items=items, total=len(items))


from app.models.tick import TickLog
@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(TickLog).filter(TickLog.id == log_id, TickLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
