from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TickTask(Base):
    __tablename__ = "tick_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str] = mapped_column(String(10), nullable=False)  # daily / weekly / monthly
    frequency_config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    enable_quality: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_points: Mapped[bool] = mapped_column(Boolean, default=False)
    points_rule: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    logs = relationship("TickLog", back_populates="task", cascade="all, delete-orphan", lazy="select")


class TickLog(Base):
    __tablename__ = "tick_logs"
    __table_args__ = (
        UniqueConstraint("task_id", "period_key", name="uq_tick_log_task_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tick_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    ticked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_key: Mapped[str] = mapped_column(String(10), nullable=False)  # 2026-04-06 / 2026-W15 / 2026-04
    quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    task = relationship("TickTask", back_populates="logs", lazy="select")
