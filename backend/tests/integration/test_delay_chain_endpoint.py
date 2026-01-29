"""Integration tests for GET /api/tasks/{id}/delay-chain endpoint."""
import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.infrastructure.database import Base, get_db, SessionLocal
from app.infrastructure.persistence.models import (
    CompanyModel,
    TeamModel,
    UserModel,
    RoleModel,
    ProjectModel,
    TaskModel,
    ScheduleHistoryModel,
)
from app.domain.models.enums import (
    TaskStatus,
    TaskPriority,
    CompanyPlan,
    ProjectStatus,
    RoleLevel,
    ScheduleChangeReason,
)


# Create in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_app():
    """Create test application with in-memory database."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    yield app

    # Clean up
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_app):
    """Create test client with patched SessionLocal to use test database."""
    # Patch the SessionLocal in uow.py to use our test session factory
    with patch('app.infrastructure.persistence.uow.SessionLocal', TestingSessionLocal):
        yield TestClient(test_app)


@pytest.fixture
def db_session():
    """Create database session for test setup."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_data(db_session):
    """Create sample data for tests."""
    now = datetime.now(UTC)

    # Company
    company = CompanyModel(
        id=str(uuid4()),
        name="Test Company",
        slug="test-company",
        plan=CompanyPlan.PRO,
        billing_email="test@example.com",
    )
    db_session.add(company)

    # Team
    team = TeamModel(
        id=str(uuid4()),
        company_id=company.id,
        name="Test Team",
        description="Test team description",
    )
    db_session.add(team)

    # Role
    role = RoleModel(
        id=str(uuid4()),
        team_id=team.id,
        name="Developer",
        level=RoleLevel.MID,
        base_capacity=40,
    )
    db_session.add(role)

    # Project
    project = ProjectModel(
        id=str(uuid4()),
        team_id=team.id,
        name="Test Project",
        description="Test project",
        status=ProjectStatus.ACTIVE,
    )
    db_session.add(project)

    # Tasks
    task_a = TaskModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Task A - Root Cause",
        description="This task was delayed",
        status=TaskStatus.DONE,
        priority=TaskPriority.HIGH,
        rank_index=1.0,
        role_responsible_id=role.id,
        expected_start_date=now - timedelta(days=10),
        expected_end_date=now - timedelta(days=5),
        actual_start_date=now - timedelta(days=10),
        actual_end_date=now - timedelta(days=2),  # 3 days late!
        is_delayed=True,
    )
    db_session.add(task_a)

    task_b = TaskModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Task B - Affected by A",
        description="This task was shifted due to A",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        rank_index=2.0,
        role_responsible_id=role.id,
        expected_start_date=now - timedelta(days=4),
        expected_end_date=now + timedelta(days=1),
        is_delayed=False,
    )
    db_session.add(task_b)

    task_c = TaskModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Task C - No history",
        description="This task has no schedule history",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        rank_index=3.0,
        role_responsible_id=role.id,
        is_delayed=False,
    )
    db_session.add(task_c)

    db_session.commit()

    # Schedule history for task B (caused by task A)
    history = ScheduleHistoryModel(
        id=str(uuid4()),
        task_id=task_b.id,
        old_expected_start=now - timedelta(days=4),
        old_expected_end=now - timedelta(days=2),
        new_expected_start=now - timedelta(days=1),
        new_expected_end=now + timedelta(days=1),
        reason=ScheduleChangeReason.DEPENDENCY_DELAY,
        caused_by_task_id=task_a.id,
    )
    db_session.add(history)
    db_session.commit()

    return {
        "company": company,
        "team": team,
        "role": role,
        "project": project,
        "task_a": task_a,
        "task_b": task_b,
        "task_c": task_c,
        "history": history,
    }


class TestDelayChainEndpoint:
    """Integration tests for delay chain endpoint."""

    def test_get_delay_chain_success(self, client, sample_data):
        """Should return delay chain for a task with history."""
        task_b = sample_data["task_b"]
        task_a = sample_data["task_a"]

        response = client.get(f"/api/tasks/{task_b.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        assert data["task_id"] == task_b.id
        assert data["task_title"] == "Task B - Affected by A"
        assert data["is_delayed"] is False
        assert len(data["entries"]) == 1

        entry = data["entries"][0]
        assert entry["reason"] == "dependency_delay"
        assert entry["caused_by_task_id"] == task_a.id
        assert entry["caused_by_task_title"] == "Task A - Root Cause"

    def test_get_delay_chain_empty_history(self, client, sample_data):
        """Should return empty entries for task with no schedule history."""
        task_c = sample_data["task_c"]

        response = client.get(f"/api/tasks/{task_c.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        assert data["task_id"] == task_c.id
        assert data["task_title"] == "Task C - No history"
        assert data["is_delayed"] is False
        assert len(data["entries"]) == 0
        assert data["total_delay_days"] is None

    def test_get_delay_chain_task_not_found(self, client, sample_data):
        """Should return 404 when task doesn't exist."""
        fake_id = str(uuid4())

        response = client.get(f"/api/tasks/{fake_id}/delay-chain")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_delay_chain_delayed_task_with_total_days(self, client, sample_data):
        """Should calculate total_delay_days for delayed tasks."""
        task_a = sample_data["task_a"]

        response = client.get(f"/api/tasks/{task_a.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        assert data["task_id"] == task_a.id
        assert data["is_delayed"] is True
        assert data["total_delay_days"] is not None
        # Task A was 3 days late (expected: -5 days, actual: -2 days)
        assert data["total_delay_days"] == pytest.approx(3.0, abs=0.1)

    def test_get_delay_chain_invalid_uuid(self, client, sample_data):
        """Should return 422 for invalid UUID format."""
        response = client.get("/api/tasks/not-a-uuid/delay-chain")

        assert response.status_code == 422

    def test_get_delay_chain_response_format(self, client, sample_data):
        """Should return properly formatted response with all fields."""
        task_b = sample_data["task_b"]

        response = client.get(f"/api/tasks/{task_b.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        # Check all required fields exist
        assert "task_id" in data
        assert "task_title" in data
        assert "is_delayed" in data
        assert "total_delay_days" in data
        assert "entries" in data
        assert "root_cause_task_id" in data
        assert "root_cause_task_title" in data

        # Check entry format
        if data["entries"]:
            entry = data["entries"][0]
            assert "task_id" in entry
            assert "task_title" in entry
            assert "old_expected_start" in entry
            assert "old_expected_end" in entry
            assert "new_expected_start" in entry
            assert "new_expected_end" in entry
            assert "reason" in entry
            assert "caused_by_task_id" in entry
            assert "caused_by_task_title" in entry
            assert "changed_by_user_id" in entry
            assert "created_at" in entry


class TestDelayChainEndpointEdgeCases:
    """Edge case tests for delay chain endpoint."""

    def test_delay_chain_with_multiple_history_entries(self, client, db_session, sample_data):
        """Should return all history entries in order."""
        task = sample_data["task_b"]
        now = datetime.now(UTC)

        # Add another history entry
        history2 = ScheduleHistoryModel(
            id=str(uuid4()),
            task_id=task.id,
            old_expected_start=now - timedelta(days=1),
            old_expected_end=now + timedelta(days=1),
            new_expected_start=now,
            new_expected_end=now + timedelta(days=2),
            reason=ScheduleChangeReason.SCOPE_CHANGE,
            changed_by_user_id=str(uuid4()),
        )
        db_session.add(history2)
        db_session.commit()

        response = client.get(f"/api/tasks/{task.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        # Should have 2 entries now
        assert len(data["entries"]) == 2

    def test_delay_chain_date_format_is_iso(self, client, sample_data):
        """Should return dates in ISO 8601 format."""
        task_b = sample_data["task_b"]

        response = client.get(f"/api/tasks/{task_b.id}/delay-chain")

        assert response.status_code == 200
        data = response.json()

        if data["entries"]:
            entry = data["entries"][0]
            # Check that dates are valid ISO format
            if entry["old_expected_start"]:
                # Should be parseable as ISO datetime
                datetime.fromisoformat(entry["old_expected_start"].replace("Z", "+00:00"))
            if entry["created_at"]:
                datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
