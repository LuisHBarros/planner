"""
Tests for refined schedule propagation (BR-024, BR-026, BR-027).
"""
from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest

from app.domain.models.task import Task
from app.domain.models.enums import TaskStatus
from app.domain.services.schedule_service_refined import ScheduleService


class TestScheduleDetection:
    """Tests for BR-023: Delay Detection"""

    def test_detect_delay_when_actual_greater_than_expected(self):
        """Task is delayed when actual_end > expected_end"""
        service = ScheduleService()

        now = datetime.now(UTC)
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Test",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now + timedelta(days=1),  # 1 day late
            status=TaskStatus.DONE,
        )

        assert service.detect_delay(task) is True

    def test_not_delayed_when_actual_equal_expected(self):
        """Task is not delayed when actual_end = expected_end"""
        service = ScheduleService()

        now = datetime.now(UTC)
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Test",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now,  # On time
            status=TaskStatus.DONE,
        )

        assert service.detect_delay(task) is False

    def test_not_delayed_when_actual_less_than_expected(self):
        """Task is not delayed when actual_end < expected_end"""
        service = ScheduleService()

        now = datetime.now(UTC)
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Test",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now - timedelta(days=1),  # 1 day early
            status=TaskStatus.DONE,
        )

        assert service.detect_delay(task) is False


class TestSchedulePropagation:
    """Tests for BR-024: Cascading Delay Propagation"""

    def test_propagate_shifts_not_started_tasks(self):
        """Tasks not started receive full delay shift"""
        service = ScheduleService()

        now = datetime.now(UTC)
        root_task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="A",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now + timedelta(days=3),  # 3 days delayed
            status=TaskStatus.DONE,
        )

        dependent = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="B",
            description="",
            role_responsible_id=uuid4(),
            expected_start_date=now + timedelta(days=1),
            expected_end_date=now + timedelta(days=3),
            actual_start_date=None,  # Not started
            status=TaskStatus.TODO,
        )

        updated = service.propagate_delay_to_dependents(root_task, [dependent])

        assert len(updated) == 1
        assert updated[0].expected_start_date == now + timedelta(days=4)
        assert updated[0].expected_end_date == now + timedelta(days=6)

    def test_propagate_respects_started_tasks(self):
        """Tasks already started only shift end date, preserve start"""
        service = ScheduleService()

        now = datetime.now(UTC)
        root_task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="A",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now + timedelta(days=3),  # 3 days delayed
            status=TaskStatus.DONE,
        )

        original_start = now + timedelta(days=1)
        dependent = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="B",
            description="",
            role_responsible_id=uuid4(),
            expected_start_date=original_start,
            expected_end_date=now + timedelta(days=3),
            actual_start_date=original_start,  # Already started!
            status=TaskStatus.DOING,
        )

        updated = service.propagate_delay_to_dependents(root_task, [dependent])

        assert len(updated) == 1
        # Start date doesn't change (already happened)
        assert updated[0].expected_start_date == original_start
        # End date shifts
        assert updated[0].expected_end_date == now + timedelta(days=6)

    def test_skip_completed_tasks(self):
        """Completed tasks are not shifted (immutable actual dates)"""
        service = ScheduleService()

        now = datetime.now(UTC)
        root_task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="A",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now + timedelta(days=3),
            status=TaskStatus.DONE,
        )

        dependent = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="B",
            description="",
            role_responsible_id=uuid4(),
            expected_start_date=now,
            expected_end_date=now + timedelta(days=3),
            actual_start_date=now,
            actual_end_date=now + timedelta(days=3),
            status=TaskStatus.DONE,  # Already completed!
        )

        updated = service.propagate_delay_to_dependents(root_task, [dependent])

        # Should not be updated
        assert len(updated) == 0

    def test_multiple_paths_uses_max_delay(self):
        """When multiple paths to task, use maximum delay"""
        service = ScheduleService()

        delays = {
            uuid4(): timedelta(days=2),
            uuid4(): timedelta(days=4),
            uuid4(): timedelta(days=1),
        }

        max_delay = service.calculate_max_delay_from_paths(delays)

        assert max_delay == timedelta(days=4)

    def test_preserve_duration_invariant(self):
        """Duration between start and end is preserved after shift"""
        service = ScheduleService()

        now = datetime.now(UTC)
        start = now
        end = now + timedelta(days=5)
        original_duration = end - start

        root_task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="A",
            description="",
            role_responsible_id=uuid4(),
            expected_end_date=now,
            actual_end_date=now + timedelta(days=3),
            status=TaskStatus.DONE,
        )

        dependent = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="B",
            description="",
            role_responsible_id=uuid4(),
            expected_start_date=start,
            expected_end_date=end,
            actual_start_date=None,
            status=TaskStatus.TODO,
        )

        updated = service.propagate_delay_to_dependents(root_task, [dependent])

        assert len(updated) == 1
        new_duration = updated[0].expected_end_date - updated[0].expected_start_date
        assert new_duration == original_duration  # Duration preserved!
