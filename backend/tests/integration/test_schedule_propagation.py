"""Integration test for schedule propagation."""
from datetime import datetime, timezone

from app.application.dtos.schedule_dtos import PropagateScheduleInput
from app.application.use_cases.propagate_schedule import PropagateScheduleUseCase
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UtcDateTime
from app.infrastructure.email.email_service import MockEmailService
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.llm.llm_service import SimpleLlmService
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork


def make_uow(session_factory):
    """Create unit of work for integration tests."""
    return SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        event_bus=InMemoryEventBus(),
        email_service=MockEmailService(),
        llm_service=SimpleLlmService(api_url=None, api_key=None),
    )


def test_schedule_propagation_creates_history(session_factory):
    """Propagates schedule and records history."""
    uow = make_uow(session_factory)
    task = Task.create(project_id=ProjectId(), title="Task")
    task.expected_start_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))

    with uow:
        uow.tasks.save(task)
        uow.commit()

    use_case = PropagateScheduleUseCase(uow=uow)
    use_case.execute(PropagateScheduleInput(
        task_id=task.id,
        delay_delta_seconds=86400,
    ))

    with uow:
        history = uow.schedule_history.list_task_history(task.id)

    assert len(history) == 1
