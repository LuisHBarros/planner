"""E2E test fixtures."""
from datetime import datetime, timedelta, timezone
from typing import Tuple
from uuid import UUID

import pytest
from fastapi import Depends, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import dependencies
from app.domain.models.user import User
from app.domain.models.value_objects import UserId
from app.infrastructure.email.email_service import MockEmailService
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.llm.llm_service import SimpleLlmService
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.main import create_app


@pytest.fixture(scope="function")
def client() -> Tuple[TestClient, User, User]:
    """Create a test client with dependency overrides."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    event_bus = InMemoryEventBus()
    email_service = MockEmailService()
    llm_service = SimpleLlmService(api_url=None, api_key=None)

    def get_uow_override() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(
            session_factory=session_factory,
            event_bus=event_bus,
            email_service=email_service,
            llm_service=llm_service,
        )

    manager = User(id=UserId(), email="manager@example.com", name="Manager")
    worker = User(id=UserId(), email="worker@example.com", name="Worker")
    with get_uow_override() as uow:
        uow.users.save(manager)
        uow.users.save(worker)
        uow.commit()

    def get_current_user_override(
        request: Request,
        uow: SqlAlchemyUnitOfWork = Depends(get_uow_override),
    ) -> User:
        header = request.headers.get("X-User", "manager")
        user_id = manager.id if header == "manager" else worker.id
        with uow:
            return uow.users.find_by_id(user_id)

    app = create_app()
    app.dependency_overrides[dependencies.get_unit_of_work] = get_uow_override
    app.dependency_overrides[dependencies.get_current_user] = get_current_user_override

    return TestClient(app), manager, worker
