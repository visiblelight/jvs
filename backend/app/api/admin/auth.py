import os
from pathlib import Path

from app.services.images import read_image, write_image

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Request, Response
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, hash_password
from app.services import sessions
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChange, TokenResponse, UserInfo, RefreshRequest
from app.services.auth import authenticate

AVATARS_DIR = "uploads/avatars"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

router = APIRouter(prefix="/auth", tags=["admin-auth"])


def check_origin(request: Request):
    origin = request.headers.get("origin")
    allowed = {value.strip().rstrip("/") for value in settings.CORS_ORIGINS.split(",") if value.strip() != "*"}
    if origin is not None and origin not in allowed:
        raise HTTPException(status_code=403, detail="不允许的请求来源")


def check_session_request(request: Request):
    check_origin(request)
    if request.headers.get("x-jvs-session") != "1":
        raise HTTPException(status_code=403, detail="缺少会话请求标记")


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_session_request(request)
    try:
        user, session, raw = sessions.refresh_session(db, request.cookies.get(sessions.COOKIE_NAME),
                                                     body.session_id, body.user_id)
    except sessions.SessionFailure as error:
        return JSONResponse({"detail": error.detail}, status_code=error.status, headers={"Cache-Control": "no-store"})
    sessions.set_cookie(response, raw, session)
    return TokenResponse(access_token=sessions.access_token(user, session))


@router.post("/logout", status_code=204)
def logout(body: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    check_session_request(request)
    try:
        sessions.logout_session(db, request.cookies.get(sessions.COOKIE_NAME), body.session_id)
    except sessions.SessionFailure as error:
        return JSONResponse({"detail": error.detail}, status_code=error.status, headers={"Cache-Control": "no-store"})
    response = Response(status_code=204)
    sessions.clear_cookie(response)
    return response


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_origin(request)
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
    session, raw = sessions.create_session(db, user, request.cookies.get(sessions.COOKIE_NAME))
    sessions.set_cookie(response, raw, session)
    return TokenResponse(access_token=sessions.access_token(user, session))


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
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user = db.query(User).filter(User.id == current_user.id).populate_existing().with_for_update().one()
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    current_user.hashed_password = hash_password(body.new_password)
    sessions.revoke_user_sessions(db, current_user)
    db.commit()
    sessions.clear_cookie(response)


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
