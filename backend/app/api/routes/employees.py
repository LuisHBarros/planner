"""Employee routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_unit_of_work
from app.application.use_cases.fire_employee import FireEmployeeUseCase
from app.application.use_cases.get_employee_workload import GetEmployeeWorkloadUseCase
from app.application.use_cases.list_team import ListTeamUseCase
from app.application.use_cases.remove_from_task import RemoveFromTaskUseCase
from app.application.use_cases.resign_from_project import ResignFromProjectUseCase
from app.domain.models.user import User
from app.domain.models.value_objects import ProjectId, TaskId, UserId
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

router = APIRouter()


class RemoveFromTaskRequest(BaseModel):
    task_id: UUID
    user_id: UUID


@router.post("/remove-from-task")
def remove_from_task(
    payload: RemoveFromTaskRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = RemoveFromTaskUseCase(uow=uow)
    output = use_case.execute(TaskId(payload.task_id), UserId(payload.user_id))
    return {"id": str(output.id), "assigned_to": str(output.assigned_to) if output.assigned_to else None}


@router.post("/{project_id}/fire/{user_id}")
def fire_employee(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = FireEmployeeUseCase(uow=uow)
    use_case.execute(ProjectId(project_id), UserId(user_id))
    return {"status": "ok"}


@router.post("/{project_id}/resign")
def resign_from_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = ResignFromProjectUseCase(uow=uow)
    use_case.execute(ProjectId(project_id), current_user.id)
    return {"status": "ok"}


@router.get("/{project_id}/team")
def list_team(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = ListTeamUseCase(uow=uow)
    members = use_case.execute(ProjectId(project_id))
    return [
        {
            "id": str(member.id),
            "user_id": str(member.user_id),
            "role_id": str(member.role_id) if member.role_id else None,
            "level": member.level.value,
            "base_capacity": member.base_capacity,
            "is_manager": member.is_manager,
        }
        for member in members
    ]


@router.get("/{project_id}/workload/{user_id}")
def get_workload(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = GetEmployeeWorkloadUseCase(uow=uow)
    output = use_case.execute(ProjectId(project_id), UserId(user_id))
    return {
        "workload_score": output.workload_score,
        "capacity": output.capacity,
        "status": output.status.value,
    }
