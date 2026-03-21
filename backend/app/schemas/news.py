from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 分类 ──

class NewsCategoryCreate(BaseModel):
    name: str
    sort_order: int = 0


class NewsCategoryUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None


class NewsCategoryOut(BaseModel):
    id: int
    name: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── 来源 ──

class NewsSourceCreate(BaseModel):
    name: str


class NewsSourceUpdate(BaseModel):
    name: Optional[str] = None


class NewsSourceOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── 文章 ──

class NewsArticleCreate(BaseModel):
    title: str = Field(..., max_length=300)
    summary: Optional[str] = Field(None, max_length=200)
    content: str
    source_url: Optional[str] = Field(None, max_length=500)
    source_id: Optional[int] = None
    author: Optional[str] = Field(None, max_length=100)
    published_at: Optional[datetime] = None
    category_id: Optional[int] = None


class NewsArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=500)
    source_id: Optional[int] = None
    author: Optional[str] = Field(None, max_length=100)
    published_at: Optional[datetime] = None
    category_id: Optional[int] = None


class NewsArticleOut(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    source_url: Optional[str]
    source_id: Optional[int]
    author: Optional[str]
    published_at: Optional[datetime]
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    category: Optional[NewsCategoryOut] = None
    source: Optional[NewsSourceOut] = None

    model_config = {"from_attributes": True}


class NewsArticleListOut(BaseModel):
    items: list[NewsArticleOut]
    total: int


# ── 开放 API ──

class OpenNewsArticleCreate(BaseModel):
    title: str = Field(..., max_length=300)
    summary: Optional[str] = Field(None, max_length=200)
    content: str
    source_url: Optional[str] = Field(None, max_length=500)
    source_name: Optional[str] = Field(None, max_length=100)
    author: Optional[str] = Field(None, max_length=100)
    published_at: Optional[datetime] = None
    category_name: Optional[str] = Field(None, max_length=100)
