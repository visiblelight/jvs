from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    business_timezone: str
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    avatar: str | None = None
    created_at: datetime | None = None
    modules: list[str] = []

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=36)
    user_id: int | None = Field(default=None, gt=0)
