import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.scopes import AVAILABLE_SCOPES
from app.models.access_key import AccessKey
from app.models.user import User
from app.schemas.access_key import AccessKeyCreate, AccessKeyOut, AccessKeyUpdate, ScopeItem

router = APIRouter(prefix="/access-keys", tags=["admin-access-keys"])


@router.get("/scopes", response_model=list[ScopeItem])
def list_scopes():
    return [ScopeItem(scope=k, label=v) for k, v in AVAILABLE_SCOPES.items()]


@router.get("", response_model=list[AccessKeyOut])
def list_access_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(AccessKey).filter(AccessKey.user_id == current_user.id).order_by(AccessKey.id).all()


@router.post("", response_model=AccessKeyOut, status_code=status.HTTP_201_CREATED)
def create_access_key(
    body: AccessKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for s in body.scopes:
        if s not in AVAILABLE_SCOPES:
            raise HTTPException(status_code=400, detail=f"无效的权限: {s}")
    ak = AccessKey(user_id=current_user.id, name=body.name, scopes=json.dumps(body.scopes))
    db.add(ak)
    db.commit()
    db.refresh(ak)
    return ak


@router.put("/{key_id}", response_model=AccessKeyOut)
def update_access_key(
    key_id: int,
    body: AccessKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ak = db.query(AccessKey).filter(AccessKey.id == key_id, AccessKey.user_id == current_user.id).first()
    if not ak:
        raise HTTPException(status_code=404, detail="Access Key 不存在")
    data = body.model_dump(exclude_unset=True)
    if "scopes" in data and data["scopes"] is not None:
        for s in data["scopes"]:
            if s not in AVAILABLE_SCOPES:
                raise HTTPException(status_code=400, detail=f"无效的权限: {s}")
        ak.scopes = json.dumps(data.pop("scopes"))
    for k, v in data.items():
        if v is not None:
            setattr(ak, k, v)
    db.commit()
    db.refresh(ak)
    return ak


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_access_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ak = db.query(AccessKey).filter(AccessKey.id == key_id, AccessKey.user_id == current_user.id).first()
    if not ak:
        raise HTTPException(status_code=404, detail="Access Key 不存在")
    db.delete(ak)
    db.commit()
