import json

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.access_key import AccessKey
from app.models.user import User

AVAILABLE_SCOPES = {
    "news:create": "提交新闻文章",
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_scope(scope: str):
    """依赖工厂：返回一个 FastAPI 依赖，校验 Access Key 是否持有指定 scope。"""

    def _dependency(
        x_access_key: str = Header(..., alias="X-Access-Key"),
        db: Session = Depends(get_db),
    ) -> User:
        ak = db.query(AccessKey).filter(
            AccessKey.key == x_access_key, AccessKey.is_active == True
        ).first()
        if ak is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 Access Key")

        user = db.query(User).filter(User.id == ak.user_id).first()
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户不存在或已被禁用")

        key_scopes = json.loads(ak.scopes) if ak.scopes else []
        if scope not in key_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"该 Access Key 没有 '{scope}' 权限",
            )

        return user

    return _dependency
