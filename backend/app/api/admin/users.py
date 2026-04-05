from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_superuser
from app.core.modules import MODULE_KEYS, get_modules_sorted
from app.core.security import hash_password
from app.models.user import User, UserModule
from app.schemas.user import (
    ModuleItem,
    UserCreate,
    UserDetail,
    UserListItem,
    UserModulesUpdate,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["admin-users"])


def _to_detail(user: User) -> UserDetail:
    return UserDetail(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        avatar=user.avatar,
        created_at=user.created_at,
        modules=[m.module_key for m in user.modules],
    )


def _to_list_item(user: User) -> UserListItem:
    return UserListItem(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        avatar=user.avatar,
        created_at=user.created_at,
        module_count=len(user.modules),
    )


def _count_active_superusers(db: Session, exclude_user_id: int | None = None) -> int:
    q = db.query(User).filter(User.is_superuser == True, User.is_active == True)
    if exclude_user_id is not None:
        q = q.filter(User.id != exclude_user_id)
    return q.count()


@router.get("", response_model=list[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    users = db.query(User).order_by(User.id).all()
    return [_to_list_item(u) for u in users]


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    for m in body.modules:
        if m not in MODULE_KEYS:
            raise HTTPException(status_code=400, detail=f"无效的模块 key: {m}")

    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        is_active=body.is_active,
        is_superuser=body.is_superuser,
    )
    db.add(user)
    db.flush()
    if not body.is_superuser:
        for key in body.modules:
            db.add(UserModule(user_id=user.id, module_key=key))
    db.commit()
    db.refresh(user)
    return _to_detail(user)


@router.get("/{user_id}", response_model=UserDetail)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _to_detail(user)


@router.put("/{user_id}", response_model=UserDetail)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    data = body.model_dump(exclude_unset=True)

    # 保护：用户名唯一
    if "username" in data and data["username"] != user.username:
        if db.query(User).filter(User.username == data["username"]).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = data["username"]

    # 保护：不能修改自己的 is_superuser
    if "is_superuser" in data:
        if user.id == current_user.id and data["is_superuser"] != user.is_superuser:
            raise HTTPException(status_code=400, detail="不能修改自己的超管权限")
        # 如果取消某用户的超管，需确保还有其他活跃超管
        if user.is_superuser and not data["is_superuser"]:
            if _count_active_superusers(db, exclude_user_id=user.id) == 0:
                raise HTTPException(status_code=400, detail="至少需保留一个活跃的超级管理员")
        user.is_superuser = data["is_superuser"]
        # 切为超管后清空其 module 记录（超管直通不需要）
        if user.is_superuser:
            db.query(UserModule).filter(UserModule.user_id == user.id).delete()

    # 保护：is_active 规则
    if "is_active" in data:
        if user.id == current_user.id and data["is_active"] is False:
            raise HTTPException(status_code=400, detail="不能禁用自己")
        if user.is_superuser and user.is_active and data["is_active"] is False:
            if _count_active_superusers(db, exclude_user_id=user.id) == 0:
                raise HTTPException(status_code=400, detail="至少需保留一个活跃的超级管理员")
        user.is_active = data["is_active"]

    # 密码
    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data["password"])

    db.commit()
    db.refresh(user)
    return _to_detail(user)


@router.put("/{user_id}/modules", response_model=UserDetail)
def set_user_modules(
    user_id: int,
    body: UserModulesUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_superuser:
        raise HTTPException(status_code=400, detail="超级管理员无需配置板块权限")

    for m in body.modules:
        if m not in MODULE_KEYS:
            raise HTTPException(status_code=400, detail=f"无效的模块 key: {m}")

    # 覆盖式：删除旧的，插入新的
    db.query(UserModule).filter(UserModule.user_id == user.id).delete()
    for key in set(body.modules):
        db.add(UserModule(user_id=user.id, module_key=key))
    db.commit()
    db.refresh(user)
    return _to_detail(user)


# ── 模块列表（登录即可查看，用于构建 UI） ──

modules_router = APIRouter(prefix="/modules", tags=["admin-modules"])


@modules_router.get("", response_model=list[ModuleItem])
def list_modules(_: User = Depends(get_current_user)):
    return [ModuleItem(**m) for m in get_modules_sorted()]
