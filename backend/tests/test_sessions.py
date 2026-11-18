from datetime import timedelta
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token, hash_password
from app.core.datetime import utc_now
from app.models.auth_session import AuthSession
from app.models.user import User
from app.services import sessions

HEADERS = {"X-JVS-Session": "1", "Origin": "http://localhost:3001"}


@pytest.fixture(autouse=True)
def session_settings(monkeypatch):
    monkeypatch.setattr(settings, "REFRESH_COOKIE_SECURE", False)
    monkeypatch.setattr(settings, "REFRESH_COOKIE_SAMESITE", "lax")
    monkeypatch.setattr(settings, "CORS_ORIGINS", "http://localhost:3001,http://localhost:3002")


def login(client, username="testuser", password="testpass123"):
    response = client.post("/api/admin/auth/login", json={"username": username, "password": password}, headers=HEADERS)
    assert response.status_code == 200
    return response.json()["access_token"], client.cookies.get(sessions.COOKIE_NAME), response


def claims(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def legacy_token(user_id):
    return jwt.encode({"sub": str(user_id), "exp": utc_now() + timedelta(minutes=10)},
                      settings.SECRET_KEY, algorithm=ALGORITHM)


def refresh(client, token=None, cookie=None, headers=None):
    data = claims(token) if token else {}
    body = {"session_id": data.get("sid"), "user_id": int(data["sub"]) if data.get("sub") else None}
    request_headers = dict(HEADERS if headers is None else headers)
    if cookie is not None:
        request_headers["Cookie"] = f"{sessions.COOKIE_NAME}={cookie}"
    return client.post("/api/admin/auth/refresh", json=body, headers=request_headers)


def authorized(client, token):
    return client.get("/api/admin/auth/me", headers={"Authorization": f"Bearer {token}"})


def test_login_persists_hash_only_and_secure_cookie(client, test_user, db, monkeypatch):
    monkeypatch.setattr(settings, "REFRESH_COOKIE_SECURE", True)
    token, raw, response = login(client)
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie
    assert "Path=/api/admin/auth" in cookie and "Domain=" not in cookie
    assert response.headers["cache-control"] == "no-store"
    payload = claims(token)
    row = db.get(AuthSession, payload["sid"])
    assert row.token_hash == sessions.digest(raw) and raw not in row.token_hash
    assert "refresh_token" not in response.json()
    assert row.user_id == test_user.id
    assert row.absolute_expires_at - row.created_at == timedelta(days=90)
    assert row.idle_expires_at - row.created_at == timedelta(days=30)


def test_expired_access_refreshes_without_password(client, test_user):
    token, _, _ = login(client)
    payload = claims(token)
    expired = create_access_token(str(test_user.id), timedelta(seconds=-10), session_id=payload["sid"])
    assert authorized(client, expired).status_code == 401
    response = refresh(client, token)
    assert response.status_code == 200
    assert authorized(client, response.json()["access_token"]).status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_rotation_grace_is_idempotent_then_replay_revokes(client, test_user, db, monkeypatch):
    token, original, _ = login(client)
    start = utc_now()
    monkeypatch.setattr(sessions, "utc_now", lambda: start)
    first = refresh(client, token, original)
    assert first.status_code == 200
    rotated = client.cookies.get(sessions.COOKIE_NAME)
    assert rotated != original
    assert refresh(client, token, original).status_code == 200
    assert client.cookies.get(sessions.COOKIE_NAME) == rotated
    assert refresh(client, token, rotated).status_code == 200
    assert client.cookies.get(sessions.COOKIE_NAME) == rotated
    monkeypatch.setattr(sessions, "utc_now", lambda: start + timedelta(seconds=31))
    rejected = refresh(client, token, original)
    assert rejected.status_code == 401 and "set-cookie" not in rejected.headers
    assert authorized(client, first.json()["access_token"]).status_code == 401
    assert refresh(client, token, rotated).status_code == 401


def test_random_wrong_secret_does_not_revoke_session(client, test_user):
    token, original, _ = login(client)
    wrong = original.split(".")[0] + "." + "x" * 43
    assert refresh(client, token, wrong).status_code == 401
    assert authorized(client, token).status_code == 200
    assert refresh(client, token, original).status_code == 200


@pytest.mark.parametrize("field", ["idle_expires_at", "absolute_expires_at"])
def test_expired_sessions_cannot_refresh_or_access(client, test_user, db, field):
    token, raw, _ = login(client)
    row = db.get(AuthSession, claims(token)["sid"])
    setattr(row, field, utc_now() - timedelta(seconds=1))
    db.commit()
    assert refresh(client, token, raw).status_code == 401
    assert authorized(client, token).status_code == 401


def test_idle_renewal_never_extends_absolute_limit(client, test_user, db, monkeypatch):
    token, raw, _ = login(client)
    row = db.get(AuthSession, claims(token)["sid"])
    start, absolute = row.created_at, row.absolute_expires_at
    for days in (20, 40, 60, 80, 89):
        monkeypatch.setattr(sessions, "utc_now", lambda days=days: start + timedelta(days=days))
        assert refresh(client).status_code == 200
        db.refresh(row)
        assert row.absolute_expires_at == absolute
        assert row.idle_expires_at <= absolute
    monkeypatch.setattr(sessions, "utc_now", lambda: absolute)
    assert refresh(client).status_code == 401


def test_logout_revokes_access_and_refresh_and_is_idempotent(client, test_user):
    token, raw, _ = login(client)
    body = {"session_id": claims(token)["sid"]}
    response = client.post("/api/admin/auth/logout", json=body, headers=HEADERS)
    assert response.status_code == 204 and "Max-Age=0" in response.headers["set-cookie"]
    assert authorized(client, token).status_code == 401
    assert refresh(client, cookie=raw).status_code == 401
    assert client.post("/api/admin/auth/logout", json=body, headers=HEADERS).status_code == 204


def test_password_change_revokes_all_devices_and_legacy_jwt(client, test_user):
    legacy = legacy_token(test_user.id)
    first, first_cookie, _ = login(client)
    client.cookies.clear()  # another device; keep first session alive
    second, second_cookie, _ = login(client)
    assert authorized(client, first).status_code == 200
    response = client.put("/api/admin/auth/password", json={"old_password": "testpass123", "new_password": "changed-pass"},
                          headers={"Authorization": f"Bearer {second}"})
    assert response.status_code == 204
    for token in (first, second, legacy):
        assert authorized(client, token).status_code == 401
    for raw in (first_cookie, second_cookie):
        assert refresh(client, cookie=raw).status_code == 401
    new_token, _, _ = login(client, password="changed-pass")
    assert claims(new_token)["ver"] == 1 and authorized(client, new_token).status_code == 200


@pytest.mark.parametrize("change", [{"password": "reset-pass"}, {"is_active": False}])
def test_admin_reset_and_disable_revoke_sessions(client, test_user, superuser_headers, change):
    token, raw, _ = login(client)
    response = client.put(f"/api/admin/users/{test_user.id}", json=change, headers=superuser_headers)
    assert response.status_code == 200
    if "is_active" in change:
        assert client.put(f"/api/admin/users/{test_user.id}", json={"is_active": True}, headers=superuser_headers).status_code == 200
    assert authorized(client, token).status_code == 401
    assert refresh(client, cookie=raw).status_code == 401


def test_account_switch_rejects_stale_refresh_without_clearing_new_cookie(client, test_user, other_user):
    old_token, old_raw, _ = login(client)
    new_token, new_raw, _ = login(client, "otheruser", "otherpass123")
    assert authorized(client, old_token).status_code == 401
    response = refresh(client, old_token)
    assert response.status_code == 409 and "set-cookie" not in response.headers
    assert client.cookies.get(sessions.COOKIE_NAME) == new_raw
    assert authorized(client, new_token).status_code == 200
    response = client.post("/api/admin/auth/logout", json={"session_id": claims(old_token)["sid"]}, headers=HEADERS)
    assert response.status_code == 409 and "set-cookie" not in response.headers
    assert refresh(client, new_token).status_code == 200


@pytest.mark.parametrize("headers", [{}, {"Origin": "http://localhost:3001"},
                                    {"X-JVS-Session": "1", "Origin": "https://evil.invalid"},
                                    {"X-JVS-Session": "1", "Origin": "null"}])
def test_csrf_guards_do_not_mutate_sessions(client, test_user, headers):
    token, raw, _ = login(client)
    assert refresh(client, headers=headers).status_code == 403
    assert client.post("/api/admin/auth/logout", json={}, headers=headers).status_code == 403
    assert authorized(client, token).status_code == 200


def test_legacy_jwt_and_missing_cookie_do_not_create_long_lived_session(client, test_user, db):
    legacy = legacy_token(test_user.id)
    assert authorized(client, legacy).status_code == 200
    response = refresh(client)
    assert response.status_code == 401 and response.headers["cache-control"] == "no-store"
    assert db.query(AuthSession).count() == 0


def test_login_rejects_foreign_origin_and_wrong_password_is_not_cached(client, test_user):
    body = {"username": "testuser", "password": "testpass123"}
    response = client.post("/api/admin/auth/login", json=body, headers={"Origin": "https://evil.invalid"})
    assert response.status_code == 403 and "set-cookie" not in response.headers
    response = client.post("/api/admin/auth/login", json={**body, "password": "wrong"})
    assert response.status_code == 401 and response.headers["cache-control"] == "no-store"


def test_real_postgresql_concurrent_refreshes_converge():
    url = os.getenv("TEST_DATABASE_URL", "")
    if not url.startswith("postgresql"):
        pytest.skip("Row lock concurrency is verified with the PostgreSQL test database")
    assert url.rsplit("/", 1)[-1].endswith("_test")
    engine = create_engine(url)
    with Session(engine) as db:
        user = User(username="session-race-" + uuid.uuid4().hex[:12], hashed_password=hash_password("test-only"), is_active=True)
        db.add(user); db.commit()
        uid = user.id
        session, raw = sessions.create_session(db, user)
        sid = session.id
    barrier = Barrier(2)
    def run():
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return sessions.refresh_session(db, raw, sid, uid)[2]
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        assert results[0] == results[1] and results[0] != raw
        with Session(engine) as db:
            assert sessions.active(db.get(AuthSession, sid))
    finally:
        with Session(engine) as db:
            db.query(AuthSession).filter(AuthSession.user_id == uid).delete()
            db.query(User).filter(User.id == uid).delete(); db.commit()
        engine.dispose()
