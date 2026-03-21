"""创建初始管理员账号。

用法:
    cd backend
    python -m scripts.init_admin
"""

import sys
from pathlib import Path

# 确保 backend/ 在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("管理员账号已存在，跳过创建。")
            return

        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        print("初始管理员账号创建成功：admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
