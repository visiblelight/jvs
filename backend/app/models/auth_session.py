from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.datetime import UTCDateTime


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_valid_until: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    idle_expires_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    absolute_expires_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
