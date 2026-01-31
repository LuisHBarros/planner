"""Task routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_unit_of_work
from app.application.dtos.task_dtos import (
    AbandonTaskInput,
    CalculateProgressInput,
    CreateTaskInput,
    SelectTaskInput,
    SetTaskDifficultyInput,
    TaskDependencyInput,
    TaskReportInput,
)
from app.application.use_cases.abandon_task import AbandonTaskUseCase
from app.application.use_cases.add_task_dependency import AddTaskDependencyUseCase
from app.application.use_cases.add_task_report import AddTaskReportUseCase
from app.application.use_cases.calculate_progress_llm import CalculateProgressLlmUseCase
from app.application.use_cases.calculate_task_difficulty_llm import CalculateTaskDifficultyLlmUseCase
from app.application.use_cases.cancel_task import CancelTaskUseCase
from app.application.use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.remove_task_dependency import RemoveTaskDependencyUseCase
from app.application.use_cases.select_task import SelectTaskUseCase
from app.application.use_cases.set_task_difficulty_manual import SetTaskDifficultyManualUseCase
from app.application.use_cases.update_progress_manual import UpdateProgressManualUseCase
from app.domain.models.enums import AbandonmentType, ProgressSource
from app.domain.models.user import User
from app.domain.models.value_objects import ProjectId, RoleId, TaskId
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

router = APIRouter()


class CreateTaskRequest(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    role_id: UUID | None = None


class SetDifficultyRequest(BaseModel):
    task_id: UUID
    difficulty: int


class DependencyRequest(BaseModel):
    task_id: UUID
    depends_on_id: UUID


class AbandonTaskRequest(BaseModel):
    task_id: UUID
    abandonment_type: AbandonmentType
    note: str | None = None


class TaskReportRequest(BaseModel):
    task_id: UUID
    progress: int
    note: str | None = None


class ProgressUpdateRequest(BaseModel):
    progress: int
    note: str | None = None


@router.post("/")
def create_task(
    payload: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(payload.project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = CreateTaskUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(CreateTaskInput(
        project_id=ProjectId(payload.project_id),
        title=payload.title,
        description=payload.description,
        role_id=RoleId(payload.role_id) if payload.role_id else None,
    ))
    return {
        "id": str(output.id),
        "project_id": str(output.project_id),
        "title": output.title,
        "description": output.description,
        "status": output.status.value,
        "difficulty": output.difficulty,
    }


@router.post("/difficulty/manual")
def set_task_difficulty(
    payload: SetDifficultyRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        task = uow.tasks.find_by_id(TaskId(payload.task_id))
        project = uow.projects.find_by_id(task.project_id) if task else None
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if project and not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = SetTaskDifficultyManualUseCase(uow=uow)
    output = use_case.execute(SetTaskDifficultyInput(
        task_id=TaskId(payload.task_id),
        difficulty=payload.difficulty,
    ))
    return {"id": str(output.id), "difficulty": output.difficulty}


@router.post("/difficulty/llm/{task_id}")
def calculate_task_difficulty(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        task = uow.tasks.find_by_id(TaskId(task_id))
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        project = uow.projects.find_by_id(task.project_id)
        if project and not project.is_manager(current_user.id):
            raise HTTPException(status_code=403, detail="Manager access required")

    use_case = CalculateTaskDifficultyLlmUseCase(uow=uow)
    output = use_case.execute(TaskId(task_id))
    return {"id": str(output.id), "difficulty": output.difficulty}


@router.post("/dependencies")
def add_dependency(
    payload: DependencyRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        task = uow.tasks.find_by_id(TaskId(payload.task_id))
        project = uow.projects.find_by_id(task.project_id) if task else None
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if project and not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = AddTaskDependencyUseCase(uow=uow)
    use_case.execute(TaskDependencyInput(
        task_id=TaskId(payload.task_id),
        depends_on_id=TaskId(payload.depends_on_id),
    ))
    return {"status": "ok"}


@router.delete("/dependencies")
def remove_dependency(
    payload: DependencyRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        task = uow.tasks.find_by_id(TaskId(payload.task_id))
        project = uow.projects.find_by_id(task.project_id) if task else None
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if project and not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = RemoveTaskDependencyUseCase(uow=uow)
    use_case.execute(TaskDependencyInput(
        task_id=TaskId(payload.task_id),
        depends_on_id=TaskId(payload.depends_on_id),
    ))
    return {"status": "ok"}


@router.post("/{task_id}/cancel")
def cancel_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        task = uow.tasks.find_by_id(TaskId(task_id))
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        project = uow.projects.find_by_id(task.project_id)
        if project and not project.is_manager(current_user.id):
            raise HTTPException(status_code=403, detail="Manager access required")

    use_case = CancelTaskUseCase(uow=uow)
    output = use_case.execute(TaskId(task_id))
    return {"id": str(output.id), "status": output.status.value}


@router.post("/{task_id}/select")
def select_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = SelectTaskUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(SelectTaskInput(
        task_id=TaskId(task_id),
        user_id=current_user.id,
    ))
    return {"id": str(output.id), "status": output.status.value, "assigned_to": str(output.assigned_to)}


@router.post("/abandon")
def abandon_task(
    payload: AbandonTaskRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = AbandonTaskUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(AbandonTaskInput(
        task_id=TaskId(payload.task_id),
        user_id=current_user.id,
        abandonment_type=payload.abandonment_type,
        note=payload.note,
    ))
    return {"id": str(output.id), "status": output.status.value}


@router.post("/reports")
def add_report(
    payload: TaskReportRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = AddTaskReportUseCase(uow=uow)
    output = use_case.execute(TaskReportInput(
        task_id=TaskId(payload.task_id),
        author_id=current_user.id,
        progress=payload.progress,
        source=ProgressSource.MANUAL,
        note=payload.note,
    ))
    return {"id": str(output.id), "progress": output.progress}


@router.post("/{task_id}/progress/llm")
def calculate_progress(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = CalculateProgressLlmUseCase(uow=uow)
    output = use_case.execute(CalculateProgressInput(
        task_id=TaskId(task_id),
        author_id=current_user.id,
    ))
    return {"id": str(output.id), "progress": output.progress}


@router.post("/{task_id}/progress/manual")
def update_progress(
    task_id: UUID,
    payload: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = UpdateProgressManualUseCase(uow=uow)
    output = use_case.execute(TaskReportInput(
        task_id=TaskId(task_id),
        author_id=current_user.id,
        progress=payload.progress,
        source=ProgressSource.MANUAL,
        note=payload.note,
    ))
    return {"id": str(output.id), "progress": output.progress}


@router.post("/{task_id}/complete")
def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = CompleteTaskUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(TaskId(task_id))
    return {"id": str(output.id), "status": output.status.value}
