"""
测试基础设施：内存 SQLite 库 + TestClient + 常用 fixture
每个测试函数都在独立的事务中运行，结束后回滚，互不干扰。
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.deps import get_db
import app.core.scopes as scopes_module
from app.core.modules import MODULES
from app.core.security import create_access_token, hash_password
from app.models.user import User, UserModule
# 导入所有模型，确保 Base.metadata 包含全部表
import app.models.todo       # noqa: F401
import app.models.news       # noqa: F401
import app.models.access_key # noqa: F401
import app.models.tick       # noqa: F401
from main import app


def _grant_all_modules(db, user_id):
    for m in MODULES:
        db.add(UserModule(user_id=user_id, module_key=m["key"]))
    db.commit()

# ── 测试数据库（内存 SQLite，仅用于测试） ──────────────────────────────────────

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """整个测试会话只建一次表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """每个测试函数获得一个独立连接，测试结束后回滚"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """将 TestClient 的 DB 替换为测试 DB"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[scopes_module.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── 用户 / Token fixture ───────────────────────────────────────────────────────

@pytest.fixture()
def test_user(db):
    """创建测试用户 A（拥有全部板块权限）"""
    user = User(
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _grant_all_modules(db, user.id)
    return user


@pytest.fixture()
def other_user(db):
    """创建测试用户 B（拥有全部板块权限），用于验证数据隔离"""
    user = User(
        username="otheruser",
        hashed_password=hash_password("otherpass123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _grant_all_modules(db, user.id)
    return user


@pytest.fixture()
def superuser(db):
    """创建超级管理员"""
    user = User(
        username="super",
        hashed_password=hash_password("superpass123"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def superuser_headers(superuser):
    token = create_access_token(str(superuser.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_no_modules(db):
    """创建无任何板块权限的用户"""
    user = User(
        username="nomodule",
        hashed_password=hash_password("pass1234"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def user_no_modules_headers(user_no_modules):
    token = create_access_token(str(user_no_modules.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_todo_only(db):
    """创建仅有 todo 板块权限的用户"""
    user = User(
        username="todoonly",
        hashed_password=hash_password("pass1234"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(UserModule(user_id=user.id, module_key="todo"))
    db.commit()
    return user


@pytest.fixture()
def user_todo_only_headers(user_todo_only):
    token = create_access_token(str(user_todo_only.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(test_user):
    """返回用户 A 的 Bearer Token 请求头"""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def other_auth_headers(other_user):
    """返回用户 B 的 Bearer Token 请求头"""
    token = create_access_token(str(other_user.id))
    return {"Authorization": f"Bearer {token}"}
