from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 打卡任务 ──

class TickTaskCreate(BaseModel):
    title: str
    short_name: str = ""
    description: Optional[str] = None
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    frequency_config: dict = Field(default_factory=dict)
    start_date: date
    end_date: Optional[date] = None
    enable_quality: bool = False
    enable_points: bool = False
    points_rule: list[dict] = Field(default_factory=list)


class TickTaskUpdate(BaseModel):
    title: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")
    frequency_config: Optional[dict] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    enable_quality: Optional[bool] = None
    enable_points: Optional[bool] = None
    points_rule: Optional[list[dict]] = None
    is_archived: Optional[bool] = None


class TickTaskOut(BaseModel):
    id: int
    title: str
    short_name: str = ""
    description: Optional[str]
    frequency: str
    frequency_config: dict
    start_date: date
    end_date: Optional[date]
    enable_quality: bool
    enable_points: bool
    points_rule: list[dict]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    # 动态统计字段（由 service 填充）
    total_ticks: int = 0
    current_streak: int = 0
    total_points: int = 0
    ticked_this_period: bool = False

    model_config = {"from_attributes": True}


class TickTaskListOut(BaseModel):
    items: list[TickTaskOut]
    total: int


# ── 打卡日志 ──

class TickLogCreate(BaseModel):
    quality: Optional[int] = Field(default=None, ge=1, le=5)
    note: Optional[str] = None


class TickLogOut(BaseModel):
    id: int
    task_id: int
    ticked_at: datetime
    period_key: str
    quality: Optional[int]
    note: Optional[str]
    points_earned: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TickResult(BaseModel):
    """打卡操作的返回结果"""
    log: TickLogOut
    current_streak: int
    total_points: int


class TickLogListOut(BaseModel):
    items: list[TickLogOut]
    total: int
