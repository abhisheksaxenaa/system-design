import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_DIALECT = os.environ.get("DIALECT") or os.environ.get("DIALECT") or "sqlite"
DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_NAME = os.environ.get("DATABASE_DB") or os.environ.get("DB") or "postgres"
DATABASE_USER = os.environ.get("DATABASE_USER") or os.environ.get("USER") or "postgres"
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD") or os.environ.get("PASSWORD") or ""
DATABASE_SCHEMA = os.environ.get("DATABASE_SCHEMA") or os.environ.get("SCHEMA")
DATABASE_HOST = os.environ.get("DATABASE_HOST") or os.environ.get("DB_HOST") or "localhost"
DATABASE_PORT = os.environ.get("DATABASE_PORT") or os.environ.get("DB_PORT") or "5432"

print(f"Using database dialect: {DATABASE_DIALECT}")
if not DATABASE_URL and DATABASE_DIALECT == "postgresql":
    DATABASE_URL = (
        f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    if DATABASE_SCHEMA:
        DATABASE_URL += f"?options=-csearch_path%3D{DATABASE_SCHEMA}"

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./parking.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session
