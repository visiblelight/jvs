from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    is_active: bool = True
    is_superuser: bool = False
    modules: list[str] = []


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserModulesUpdate(BaseModel):
    modules: list[str]


class UserListItem(BaseModel):
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    avatar: Optional[str] = None
    created_at: datetime
    module_count: int = 0

    model_config = {"from_attributes": True}


class UserDetail(BaseModel):
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    avatar: Optional[str] = None
    created_at: datetime
    modules: list[str] = []

    model_config = {"from_attributes": True}


class ModuleItem(BaseModel):
    key: str
    label: str
    sort_order: int
