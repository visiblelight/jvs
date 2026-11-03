"""Instants are stored as UTC-naive SQL timestamps and returned as UTC-aware values.

Date/period fields are deliberately not converted by this type.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


def utc_now():
    return datetime.now(timezone.utc)


def as_utc(value):
    if value.tzinfo is None:
        # Only internal/persisted legacy values have this convention. HTTP inputs
        # are validated with AwareDatetime before reaching the database.
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def business_today(now=None):
    return as_utc(now or utc_now()).astimezone(ZoneInfo(settings.BUSINESS_TIMEZONE)).date()


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return as_utc(value).replace(tzinfo=None) if value is not None else None

    def process_result_value(self, value, dialect):
        return as_utc(value) if value is not None else None
