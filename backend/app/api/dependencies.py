"""FastAPI dependencies."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.config import settings
from app.domain.models.user import User
from app.domain.models.value_objects import UserId
from app.infrastructure.auth.jwt_service import JwtService
from app.infrastructure.database import create_db_engine, create_session_factory
from app.infrastructure.email.email_service import MockEmailService
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.llm.llm_service import SimpleLlmService
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

engine = create_db_engine(settings.database_url)
session_factory = create_session_factory(engine)
jwt_service = JwtService(settings.jwt_secret, settings.jwt_algorithm)
event_bus = InMemoryEventBus()
email_service = MockEmailService()
llm_service = SimpleLlmService(settings.llm_api_url, settings.llm_api_key)


def get_db() -> Session:
    """Provide a database session."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_unit_of_work() -> SqlAlchemyUnitOfWork:
    """Provide a unit of work."""
    return SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        event_bus=event_bus,
        email_service=email_service,
        llm_service=llm_service,
    )


def get_current_user(
    request: Request,
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
) -> User:
    """Extract current user from JWT."""
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        token = auth.replace("Bearer ", "", 1)
        claims = jwt_service.verify_token(token)
        user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        user_id_value = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    with uow:
        user = uow.users.find_by_id(UserId(user_id_value))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
