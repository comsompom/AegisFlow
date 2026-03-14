"""SQLite database setup and session management."""
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings
from app.models_db import Base


def get_engine():
    url = get_settings().database_url
    # Use sync SQLite: ensure url is sqlite:// (not aiosqlite)
    if url.startswith("sqlite+aiosqlite"):
        url = url.replace("sqlite+aiosqlite", "sqlite", 1)
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if "sqlite" in url else {},
        echo=False,
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables. Call on application startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session. Commit on success, rollback on error, close in finally."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
