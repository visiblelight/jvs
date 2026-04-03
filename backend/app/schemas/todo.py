from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 分类 ──

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryItem(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class CategoryOut(CategoryItem):
    children: list["CategoryOut"] = []


# ── 标签 ──

class TagCreate(BaseModel):
    name: str
    color: str = "#1890ff"


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagOut(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


# ── 事项 ──

class TodoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    importance: int = Field(default=3, ge=1, le=5)
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    tag_ids: list[int] = []


class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    importance: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[str] = None
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    tag_ids: Optional[list[int]] = None


class TodoStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|paused|completed|archived)$")


class TodoItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    importance: int
    status: str
    category_id: Optional[int]
    category_name: Optional[str] = None
    due_date: Optional[datetime]
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]
    is_deleted: bool
    deleted_at: Optional[datetime]
    purged_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []

    model_config = {"from_attributes": True}


class TodoItemListOut(BaseModel):
    items: list[TodoItemOut]
    total: int
