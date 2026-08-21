import os
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class DatabaseFactory:
    _instances = {}
    _lock = Lock()

    @staticmethod
    def _postgres_database_url() -> str:
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            return database_url

        database_name = os.environ.get("DATABASE_DB") or os.environ.get("DB") or "postgres"
        database_user = os.environ.get("DATABASE_USER") or os.environ.get("USER") or "postgres"
        database_password = os.environ.get("DATABASE_PASSWORD") or os.environ.get("PASSWORD") or ""
        database_schema = os.environ.get("DATABASE_SCHEMA") or os.environ.get("SCHEMA")
        database_host = os.environ.get("DATABASE_HOST") or os.environ.get("DB_HOST") or "localhost"
        database_port = os.environ.get("DATABASE_PORT") or os.environ.get("DB_PORT") or "5432"

        database_url = (
            f"postgresql+psycopg://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
        )
        if database_schema:
            database_url += f"?options=-csearch_path%3D{database_schema}"
        return database_url

    @staticmethod
    def _sqlite_database_url() -> str:
        return f"sqlite:///{BASE_DIR / 'parking.db'}"

    @classmethod
    def create_engine(cls, dialect: str | None = None):
        selected_dialect = (dialect or os.environ.get("DATABASE_DIALECT") or os.environ.get("DIALECT") or "sqlite").lower()

        if selected_dialect.startswith("postgres"):
            return create_engine(cls._postgres_database_url(), echo=False)

        return create_engine(cls._sqlite_database_url(), echo=False, connect_args={"check_same_thread": False})

    @classmethod
    def get_engine(cls, dialect: str | None = None):
        selected_dialect = (dialect or os.environ.get("DATABASE_DIALECT") or os.environ.get("DIALECT") or "sqlite").lower()
        if selected_dialect.startswith("postgres"):
            key = "postgres"
        else:
            key = "sqlite"

        if key not in cls._instances:
            with cls._lock:
                if key not in cls._instances:
                    cls._instances[key] = cls.create_engine(selected_dialect)
        return cls._instances[key]


engine = DatabaseFactory.get_engine()


def get_session():
    with Session(engine) as session:
        yield session
