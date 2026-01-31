"""Database setup for SQLite."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    """Return the database URL."""
    return os.getenv("DATABASE_URL", "sqlite:///./planner.db")


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create SQLAlchemy engine."""
    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory."""
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
