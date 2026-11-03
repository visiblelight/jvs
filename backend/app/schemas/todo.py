from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator, AwareDatetime


from app.schemas.common import UpdateModel


# ── 分类 ──

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(UpdateModel):
    non_nullable = ['name', 'sort_order']
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


class TagUpdate(UpdateModel):
    non_nullable = ['color', 'name']
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
    due_date: Optional[AwareDatetime] = None
    scheduled_at: Optional[AwareDatetime] = None
    tag_ids: list[int] = []


TodoStatus = Literal["pending", "paused", "completed", "archived"]


class TodoItemUpdate(UpdateModel):
    non_nullable = ['importance', 'priority', 'status', 'tag_ids', 'title']
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    importance: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[TodoStatus] = None
    category_id: Optional[int] = None
    due_date: Optional[AwareDatetime] = None
    scheduled_at: Optional[AwareDatetime] = None
    tag_ids: Optional[list[int]] = None


class TodoStatusUpdate(BaseModel):
    status: TodoStatus


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
    comment_count: int = 0

    model_config = {"from_attributes": True}


    @model_validator(mode="before")
    @classmethod
    def hide_foreign_relations(cls, value):
        if not hasattr(value, "user_id"):
            return value
        data = {name: getattr(value, name, None) for name in cls.model_fields}
        if value.category is not None and value.category.user_id != value.user_id:
            data["category_id"] = None
            data["category_name"] = None
        data["tags"] = [tag for tag in value.tags if tag.user_id == value.user_id]
        return data


class TodoItemListOut(BaseModel):
    items: list[TodoItemOut]
    total: int


# ── 评论 ──

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
