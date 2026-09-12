from collections.abc import Generator

from sqlmodel import Session

from app.db.engine import engine


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise