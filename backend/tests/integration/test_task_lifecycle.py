"""Integration test for task lifecycle."""
from app.application.dtos.project_dtos import CreateProjectInput
from app.application.dtos.task_dtos import (
    AbandonTaskInput,
    CreateTaskInput,
    SelectTaskInput,
    SetTaskDifficultyInput,
)
from app.application.use_cases.abandon_task import AbandonTaskUseCase
from app.application.use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.select_task import SelectTaskUseCase
from app.application.use_cases.set_task_difficulty_manual import SetTaskDifficultyManualUseCase
from app.domain.models.enums import AbandonmentType, MemberLevel, TaskStatus
from app.domain.models.project_member import ProjectMember
from app.domain.models.user import User
from app.domain.models.value_objects import ProjectId, UserId
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


def test_task_lifecycle_select_abandon_complete(session_factory):
    """Create task, select, abandon, and complete."""
    uow = make_uow(session_factory)
    manager_id = UserId()
    worker_id = UserId()
    with uow:
        uow.users.save(User(id=manager_id, email="manager@example.com", name="Manager"))
        uow.users.save(User(id=worker_id, email="worker@example.com", name="Worker"))
        uow.commit()

    create_project = CreateProjectUseCase(uow=uow, event_bus=uow.event_bus)
    project = create_project.execute(CreateProjectInput(name="Proj", created_by=manager_id))

    with uow:
        uow.project_members.save(ProjectMember.create_member(
            project_id=project.id,
            user_id=worker_id,
            level=MemberLevel.MID,
            base_capacity=10,
        ))
        uow.commit()

    create_task = CreateTaskUseCase(uow=uow, event_bus=uow.event_bus)
    task = create_task.execute(CreateTaskInput(project_id=project.id, title="Task"))

    set_difficulty = SetTaskDifficultyManualUseCase(uow=uow)
    set_difficulty.execute(SetTaskDifficultyInput(task_id=task.id, difficulty=3))

    select_task = SelectTaskUseCase(uow=uow, event_bus=uow.event_bus)
    selected = select_task.execute(SelectTaskInput(task_id=task.id, user_id=worker_id))
    assert selected.status == TaskStatus.DOING

    abandon = AbandonTaskUseCase(uow=uow, event_bus=uow.event_bus)
    abandoned = abandon.execute(AbandonTaskInput(
        task_id=task.id,
        user_id=worker_id,
        abandonment_type=AbandonmentType.VOLUNTARY,
    ))
    assert abandoned.status == TaskStatus.TODO

    # Complete a fresh task
    task2 = create_task.execute(CreateTaskInput(project_id=project.id, title="Task 2"))
    set_difficulty.execute(SetTaskDifficultyInput(task_id=task2.id, difficulty=2))
    select_task.execute(SelectTaskInput(task_id=task2.id, user_id=worker_id))

    complete = CompleteTaskUseCase(uow=uow, event_bus=uow.event_bus)
    completed = complete.execute(task2.id)
    assert completed.status == TaskStatus.DONE
