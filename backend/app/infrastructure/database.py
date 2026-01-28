"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


# For SQLite, check_same_thread=False is needed for FastAPI/TestClient usage
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """
    Initialize database schema.

    Imports the persistence models so that SQLAlchemy is aware of all mapped
    tables, then creates them if they do not exist yet. This is primarily
    used by local tooling like `app.seed_demo`.
    """
    # Import models for side effects so they register with Base.metadata
    from app.infrastructure.persistence import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
