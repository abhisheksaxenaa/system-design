import importlib

from sqlalchemy import inspect

import app.boundary.db as db
from app.boundary.db import engine
from app.main import on_startup


def test_env_file_loads_database_settings():
    importlib.reload(db)

    assert db.DATABASE_DIALECT == 'postgresql'
    assert db.DATABASE_URL.startswith('postgresql+psycopg://system_design:lldsystemdesign@localhost:5432/system_design')


def test_startup_creates_all_tables():
    on_startup()

    tables = inspect(engine).get_table_names()
    assert {'players', 'games', 'moves'}.issubset(tables)
