from fastapi import HTTPException


def owned(db, model, object_id, user_id, label="关联对象"):
    if object_id is None:
        return None
    value = db.query(model).filter(model.id == object_id, model.user_id == user_id).first()
    if value is None:
        raise HTTPException(status_code=404, detail=f"{label}不存在")
    return value


def owned_many(db, model, ids, user_id, label="关联对象"):
    ids = set(ids)
    values = db.query(model).filter(model.id.in_(ids), model.user_id == user_id).all() if ids else []
    if len(values) != len(ids):
        raise HTTPException(status_code=404, detail=f"{label}不存在")
    return values
