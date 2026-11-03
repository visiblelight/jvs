from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


from app.schemas.common import UpdateModel


class TickValidation(BaseModel):
    @field_validator("points_rule", check_fields=False)
    @classmethod
    def validate_points(cls, value):
        if value is None:
            return value
        seen = set()
        for rule in value:
            if set(rule) != {"streak", "points"}:
                raise ValueError("积分规则必须包含 streak 和 points")
            if type(rule["streak"]) is not int or not 1 <= rule["streak"] <= 1000000:
                raise ValueError("streak 必须是正整数")
            if type(rule["points"]) is not int or not 0 <= rule["points"] <= 1000000:
                raise ValueError("points 必须是非负整数且不超过 1000000")
            if rule["streak"] in seen:
                raise ValueError("积分阶梯不能重复")
            seen.add(rule["streak"])
        if value and 1 not in seen:
            raise ValueError("积分规则必须从连续 1 次开始")
        return sorted(value, key=lambda r: r["streak"])

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("结束日期不能早于开始日期")
        return self


# ── 打卡任务 ──

class TickTaskCreate(TickValidation):
    title: str = Field(min_length=1, max_length=200)
    short_name: str = Field(default="", max_length=10)
    description: Optional[str] = None
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    frequency_config: dict = Field(default_factory=dict)
    start_date: date
    end_date: Optional[date] = None
    enable_quality: bool = False
    enable_points: bool = False
    points_rule: list[dict] = Field(default_factory=list)


class TickTaskUpdate(UpdateModel, TickValidation):
    non_nullable = {"title", "short_name", "frequency", "frequency_config", "start_date", "enable_quality", "enable_points", "points_rule", "is_archived"}
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    short_name: Optional[str] = Field(default=None, max_length=10)
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
    created_at: datetime | None
    updated_at: datetime | None
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


class MakeupTickCreate(BaseModel):
    period_key: str
    note: Optional[str] = None
    quality: Optional[int] = Field(default=None, ge=1, le=5)


class TickLogOut(BaseModel):
    id: int
    task_id: int
    ticked_at: datetime
    period_key: str
    quality: Optional[int]
    note: Optional[str]
    points_earned: int
    is_makeup: bool = False
    created_at: datetime | None

    model_config = {"from_attributes": True}


class TickResult(BaseModel):
    """打卡操作的返回结果"""
    log: TickLogOut
    current_streak: int
    total_points: int


class TickLogListOut(BaseModel):
    items: list[TickLogOut]
    total: int
