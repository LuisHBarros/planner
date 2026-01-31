"""Schedule routes."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_unit_of_work
from app.application.dtos.schedule_dtos import ManualDateOverrideInput, PropagateScheduleInput, UpdateProjectDateInput
from app.application.use_cases.change_employee_role import ChangeEmployeeRoleUseCase
from app.application.use_cases.detect_delay import DetectDelayUseCase
from app.application.use_cases.manual_date_override import ManualDateOverrideUseCase
from app.application.use_cases.propagate_schedule import PropagateScheduleUseCase
from app.application.use_cases.update_project_date import UpdateProjectDateUseCase
from app.application.use_cases.view_schedule_history import ViewScheduleHistoryUseCase
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.user import User
from app.domain.models.value_objects import ProjectId, RoleId, TaskId, UtcDateTime, UserId
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

router = APIRouter()


class PropagateRequest(BaseModel):
    task_id: UUID
    delay_delta_seconds: int


class UpdateProjectDateRequest(BaseModel):
    project_id: UUID
    new_end_date: datetime
    reason: ScheduleChangeReason


class ManualOverrideRequest(BaseModel):
    task_id: UUID
    new_start_date: datetime
    new_end_date: datetime


class ChangeRoleRequest(BaseModel):
    project_id: UUID
    user_id: UUID
    role_id: UUID | None = None


@router.get("/delay/{task_id}")
def detect_delay(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = DetectDelayUseCase(uow=uow)
    delayed = use_case.execute(TaskId(task_id))
    return {"task_id": str(task_id), "delayed": delayed}


@router.post("/propagate")
def propagate_schedule(
    payload: PropagateRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = PropagateScheduleUseCase(uow=uow)
    use_case.execute(PropagateScheduleInput(
        task_id=TaskId(payload.task_id),
        delay_delta_seconds=payload.delay_delta_seconds,
    ))
    return {"status": "ok"}


@router.post("/project-date")
def update_project_date(
    payload: UpdateProjectDateRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(payload.project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = UpdateProjectDateUseCase(uow=uow)
    use_case.execute(UpdateProjectDateInput(
        project_id=ProjectId(payload.project_id),
        new_end_date=UtcDateTime(payload.new_end_date),
        reason=payload.reason,
    ))
    return {"status": "ok"}


@router.get("/history")
def view_schedule_history(
    project_id: UUID | None = None,
    task_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = ViewScheduleHistoryUseCase(uow=uow)
    projects, tasks = use_case.execute(
        project_id=ProjectId(project_id) if project_id else None,
        task_id=TaskId(task_id) if task_id else None,
    )
    return {
        "projects": [
            {
                "id": str(item.id),
                "project_id": str(item.project_id),
                "previous_end": item.previous_end.value.isoformat(),
                "new_end": item.new_end.value.isoformat(),
                "reason": item.reason.value,
            }
            for item in projects
        ],
        "tasks": [
            {
                "id": str(item.id),
                "task_id": str(item.task_id),
                "previous_start": item.previous_start.value.isoformat(),
                "previous_end": item.previous_end.value.isoformat(),
                "new_start": item.new_start.value.isoformat(),
                "new_end": item.new_end.value.isoformat(),
                "reason": item.reason.value,
            }
            for item in tasks
        ],
    }


@router.post("/manual-override")
def manual_override(
    payload: ManualOverrideRequest,
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

    use_case = ManualDateOverrideUseCase(uow=uow)
    use_case.execute(ManualDateOverrideInput(
        task_id=TaskId(payload.task_id),
        new_start_date=UtcDateTime(payload.new_start_date),
        new_end_date=UtcDateTime(payload.new_end_date),
    ))
    return {"status": "ok"}


@router.post("/change-role")
def change_employee_role(
    payload: ChangeRoleRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(payload.project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = ChangeEmployeeRoleUseCase(uow=uow)
    use_case.execute(
        ProjectId(payload.project_id),
        UserId(payload.user_id),
        RoleId(payload.role_id) if payload.role_id else None,
    )
    return {"status": "ok"}
