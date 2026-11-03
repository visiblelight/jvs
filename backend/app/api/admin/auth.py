import os
from pathlib import Path

from app.services.images import read_image, write_image

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password, hash_password
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChange, TokenResponse, UserInfo
from app.services.auth import authenticate

AVATARS_DIR = "uploads/avatars"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

router = APIRouter(prefix="/auth", tags=["admin-auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo(
        business_timezone=settings.BUSINESS_TIMEZONE,
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        modules=[m.module_key for m in current_user.modules],
    )


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contents, ext = await read_image(file, MAX_AVATAR_SIZE)
    old_avatar = current_user.avatar
    target = write_image(AVATARS_DIR, contents, ext, prefix=f"{current_user.id}.")
    try:
        current_user.avatar = target.name
        db.commit()
    except Exception:
        db.rollback()
        target.unlink(missing_ok=True)
        raise
    if old_avatar and Path(old_avatar).name == old_avatar:
        try:
            (Path(AVATARS_DIR) / old_avatar).unlink(missing_ok=True)
        except OSError:
            pass  # A cleanup failure must not undo a successful avatar update.
    return {"avatar": target.name}


@router.delete("/avatar", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.avatar and Path(current_user.avatar).name == current_user.avatar:
        path = os.path.join(AVATARS_DIR, current_user.avatar)
        if os.path.exists(path):
            os.remove(path)
        current_user.avatar = None
        db.commit()
