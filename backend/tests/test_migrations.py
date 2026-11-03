"""Run Alembic in a fresh process, without main.py registering models for it."""
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

BACKEND = Path(__file__).resolve().parents[1]


def run_alembic(url, *args):
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args], cwd=BACKEND,
        env={**os.environ, "DATABASE_URL": url}, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture(params=["sqlite"] + (["postgresql"] if os.getenv("TEST_POSTGRES_URL") else []))
def migration_url(request, tmp_path):
    if request.param == "sqlite":
        yield f"sqlite:///{tmp_path / 'migration.db'}"
        return
    base = make_url(os.environ["TEST_POSTGRES_URL"])
    assert base.database.endswith("_test"), "Use an explicitly named disposable _test database"
    name = "jvs_migration_" + uuid.uuid4().hex
    admin = create_engine(base, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    try:
        yield base.set(database=name).render_as_string(hide_password=False)
    finally:
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def test_upgrade_preserves_data_and_matches_models(migration_url):
    url = migration_url
    run_alembic(url, "upgrade", "0b262c5f0426")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO users (id, username, hashed_password, is_active, is_superuser, created_at, updated_at) VALUES (1, 'migration', 'unused', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        conn.execute(text("INSERT INTO todo_items (id, user_id, title, status, priority, importance, created_at, updated_at) VALUES (1, 1, 'keep todo', 'pending', 3, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        conn.execute(text("INSERT INTO tick_tasks (id, user_id, title, frequency, start_date) VALUES (1, 1, 'keep task', 'daily', '2026-04-01')"))
        conn.execute(text("INSERT INTO tick_logs (id, user_id, task_id, ticked_at, period_key) VALUES (1, 1, 1, '2026-04-01 12:00:00', '2026-04-01')"))
    run_alembic(url, "upgrade", "head")
    run_alembic(url, "upgrade", "head")
    run_alembic(url, "check")
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT title FROM todo_items WHERE id=1")) == "keep todo"
        assert conn.scalar(text("SELECT period_key FROM tick_logs WHERE id=1")) == "2026-04-01"
    engine.dispose()
