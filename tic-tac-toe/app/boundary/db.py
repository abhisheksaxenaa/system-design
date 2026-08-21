import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import create_engine, Session

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_DIALECT = os.environ.get("DATABASE_DIALECT")
DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_NAME = os.environ.get("DB") or os.environ.get("DATABASE_DB")
DATABASE_USER = os.environ.get("USER") or os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("PASSWORD") or os.environ.get("DATABASE_PASSWORD")
DATABASE_SCHEMA = os.environ.get("SCHEMA") or os.environ.get("DATABASE_SCHEMA")
DATABASE_HOST = os.environ.get("DB_HOST") or os.environ.get("DATABASE_HOST") or "localhost"
DATABASE_PORT = os.environ.get("DB_PORT") or os.environ.get("DATABASE_PORT") or "5432"

if DATABASE_DIALECT == "postgresql":
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

print(DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
