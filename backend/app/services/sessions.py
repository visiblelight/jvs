"""Persist only hashes of rotating refresh credentials; never expose them to JS."""
from datetime import timedelta
import hashlib
import hmac
import secrets
import uuid

from app.core.config import settings
from app.core.datetime import utc_now
from app.core.security import create_access_token
from app.models.auth_session import AuthSession
from app.models.user import User

COOKIE_NAME = "jvs_refresh"
COOKIE_PATH = "/api/admin/auth"
ROTATION_GRACE_SECONDS = 30


class SessionFailure(Exception):
    def __init__(self, detail="登录已过期，请重新登录", status=401):
        self.detail, self.status = detail, status


def digest(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def session_id(raw):
    try:
        sid, secret = raw.split(".")
        if str(uuid.UUID(sid)) != sid or not 32 <= len(secret) <= 64:
            return None
        return sid
    except (ValueError, AttributeError):
        return None


def next_credential(raw):
    secret = hmac.new(settings.SECRET_KEY.encode(), ("jvs-refresh-v1:" + raw).encode(), hashlib.sha256).hexdigest()
    return raw.split(".")[0] + "." + secret


def active(session, now=None):
    now = now or utc_now()
    return session.revoked_at is None and now < session.idle_expires_at and now < session.absolute_expires_at


def access_token(user, session):
    expires = min(utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                  session.idle_expires_at, session.absolute_expires_at)
    return create_access_token(str(user.id), session_id=session.id, token_version=user.token_version, expires_at=expires)


def cookie_options():
    return dict(httponly=True, secure=settings.REFRESH_COOKIE_SECURE,
                samesite=settings.REFRESH_COOKIE_SAMESITE, path=COOKIE_PATH)


def set_cookie(response, raw, session):
    expires = min(session.idle_expires_at, session.absolute_expires_at)
    response.set_cookie(COOKIE_NAME, raw, max_age=max(0, int((expires - utc_now()).total_seconds())),
                        expires=expires, **cookie_options())
    response.headers["Cache-Control"] = "no-store"


def clear_cookie(response):
    response.delete_cookie(COOKIE_NAME, **cookie_options())
    response.headers["Cache-Control"] = "no-store"


def verified_credential(session, raw):
    value = digest(raw)
    return hmac.compare_digest(session.token_hash, value) or bool(
        session.previous_token_hash and hmac.compare_digest(session.previous_token_hash, value))


def create_session(db, user, old_raw=None):
    now = utc_now()
    old_id = session_id(old_raw)
    if old_id:
        old = db.query(AuthSession).filter(AuthSession.id == old_id).with_for_update().first()
        if old and verified_credential(old, old_raw):
            old.revoked_at = now
    sid = str(uuid.uuid4())
    raw = sid + "." + secrets.token_urlsafe(32)
    session = AuthSession(id=sid, user_id=user.id, token_hash=digest(raw), created_at=now,
                          last_used_at=now, idle_expires_at=now + timedelta(days=settings.REFRESH_IDLE_DAYS),
                          absolute_expires_at=now + timedelta(days=settings.REFRESH_ABSOLUTE_DAYS))
    db.add(session)
    db.commit()
    return session, raw


def locked_session(db, raw):
    sid = session_id(raw)
    hint = db.get(AuthSession, sid) if sid else None
    if not hint:
        raise SessionFailure()
    # User -> session lock order also used by password reset/disable.
    user = db.query(User).filter(User.id == hint.user_id).populate_existing().with_for_update().first()
    session = db.query(AuthSession).filter(AuthSession.id == sid).populate_existing().with_for_update().first()
    if not user or not session:
        raise SessionFailure()
    return user, session


def refresh_session(db, raw, expected_session=None, expected_user=None):
    user, session = locked_session(db, raw)
    if ((expected_session is not None and session.id != expected_session) or
            (expected_user is not None and user.id != expected_user)):
        raise SessionFailure("登录账号已在其他页面改变，请重新登录", 409)
    now = utc_now()
    if not user.is_active or not active(session, now):
        raise SessionFailure()
    value = digest(raw)
    grace = session.previous_valid_until is not None and now < session.previous_valid_until
    if hmac.compare_digest(session.token_hash, value):
        if not grace:
            session.previous_token_hash = value
            session.previous_valid_until = now + timedelta(seconds=ROTATION_GRACE_SECONDS)
            raw = next_credential(raw)
            session.token_hash = digest(raw)
    elif session.previous_token_hash and hmac.compare_digest(session.previous_token_hash, value):
        if not grace:
            session.revoked_at = now
            db.commit()
            raise SessionFailure()
        raw = next_credential(raw)
        if not hmac.compare_digest(session.token_hash, digest(raw)):
            raise SessionFailure()
    else:
        # An arbitrary bad secret must not let an attacker revoke a known ID.
        raise SessionFailure()
    session.last_used_at = now
    session.idle_expires_at = min(now + timedelta(days=settings.REFRESH_IDLE_DAYS), session.absolute_expires_at)
    db.commit()
    return user, session, raw


def logout_session(db, raw, expected_session=None):
    if not session_id(raw):
        return
    try:
        _, session = locked_session(db, raw)
    except SessionFailure:
        return
    if expected_session is not None and session.id != expected_session:
        raise SessionFailure("登录账号已在其他页面改变，请刷新页面", 409)
    if verified_credential(session, raw):
        session.revoked_at = utc_now()
        db.commit()


def revoke_user_sessions(db, user):
    # Caller holds the user row lock and commits password/version/revocations together.
    user.token_version += 1
    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update(
        {AuthSession.revoked_at: utc_now()}, synchronize_session=False)
