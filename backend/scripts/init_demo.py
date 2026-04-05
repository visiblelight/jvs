"""创建 demo 演示账号。

用法:
    cd backend
    python -m scripts.init_demo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.modules import MODULES
from app.core.security import hash_password
from app.models.user import User, UserModule


def main():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "demo").first()
        if existing:
            print("demo 账号已存在，跳过创建。")
            return

        demo = User(
            username="demo",
            hashed_password=hash_password("demo123456"),
            is_active=True,
            is_superuser=False,
        )
        db.add(demo)
        db.flush()
        for m in MODULES:
            db.add(UserModule(user_id=demo.id, module_key=m["key"]))
        db.commit()
        print("demo 账号创建成功：demo / demo123456（已授予全部板块权限）")
    finally:
        db.close()


if __name__ == "__main__":
    main()
