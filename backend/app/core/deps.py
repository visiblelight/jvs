from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import ALGORITHM
from app.models.access_key import AccessKey
from app.models.user import User, UserModule
from app.models.auth_session import AuthSession
from app.services.sessions import active

security_scheme = HTTPBearer()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db=Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM],
                             options={"require_exp": True, "require_sub": True})
        user_id = int(payload["sub"])
        if user_id <= 0:
            raise ValueError()
    except (JWTError, ValueError, TypeError, KeyError):
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or payload.get("ver", 0) != user.token_version:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")
    sid = payload.get("sid")
    if sid is not None:
        session = db.get(AuthSession, sid) if isinstance(sid, str) else None
        if not session or session.user_id != user.id or not active(session):
            raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    return user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅超级管理员可访问",
        )
    return current_user


def require_module(module_key: str):
    """依赖工厂：要求当前用户拥有指定板块权限。超管直通。"""

    def _dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_superuser:
            return current_user
        has = (
            db.query(UserModule)
            .filter(
                UserModule.user_id == current_user.id,
                UserModule.module_key == module_key,
            )
            .first()
        )
        if not has:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有 '{module_key}' 板块权限",
            )
        return current_user

    return _dependency


def verify_access_key(
    x_access_key: str = Header(..., alias="X-Access-Key"),
    db=Depends(get_db),
) -> User:
    ak = db.query(AccessKey).filter(AccessKey.key == x_access_key, AccessKey.is_active == True).first()
    if ak is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 Access Key")
    user = db.query(User).filter(User.id == ak.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户不存在或已被禁用")
    return user
