import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class AccessKeyCreate(BaseModel):
    name: str
    scopes: list[str] = []


class AccessKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    scopes: Optional[list[str]] = None


class AccessKeyOut(BaseModel):
    id: int
    name: str
    key: str
    scopes: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("scopes", mode="before")
    @classmethod
    def parse_scopes(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class ScopeItem(BaseModel):
    scope: str
    label: str
