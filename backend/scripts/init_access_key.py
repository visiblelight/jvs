"""为 admin 用户生成初始 Access Key"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.core.scopes import AVAILABLE_SCOPES
from app.models.user import User
from app.models.access_key import AccessKey

db = SessionLocal()

admin = db.query(User).filter(User.username == "admin").first()
if not admin:
    print("admin 用户不存在，请先创建")
    sys.exit(1)

existing = db.query(AccessKey).filter(AccessKey.user_id == admin.id).first()
if existing:
    print(f"admin 用户已有 Access Key: {existing.key}")
else:
    all_scopes = list(AVAILABLE_SCOPES.keys())
    ak = AccessKey(user_id=admin.id, name="default", scopes=json.dumps(all_scopes))
    db.add(ak)
    db.commit()
    db.refresh(ak)
    print(f"已为 admin 用户生成 Access Key: {ak.key}")
    print(f"权限: {all_scopes}")

db.close()
