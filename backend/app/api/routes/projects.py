"""Project routes."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_unit_of_work
from app.application.dtos.project_dtos import (
    ConfigureProjectLlmInput,
    CreateProjectInput,
    CreateRoleInput,
)
from app.application.use_cases.configure_project_llm import ConfigureProjectLlmUseCase
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.use_cases.create_role import CreateRoleUseCase
from app.application.use_cases.get_project import GetProjectUseCase
from app.domain.models.user import User
from app.domain.models.value_objects import ProjectId, UserId, UtcDateTime
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    expected_end_date: datetime | None = None


class ConfigureLlmRequest(BaseModel):
    provider: str
    api_key_encrypted: str


class CreateRoleRequest(BaseModel):
    name: str
    description: str | None = None


@router.post("/")
def create_project(
    payload: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = CreateProjectUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(CreateProjectInput(
        name=payload.name,
        created_by=current_user.id,
        description=payload.description,
        expected_end_date=UtcDateTime(payload.expected_end_date) if payload.expected_end_date else None,
    ))
    return {
        "id": str(output.id),
        "name": output.name,
        "description": output.description,
        "created_by": str(output.created_by),
        "expected_end_date": output.expected_end_date.value.isoformat() if output.expected_end_date else None,
        "status": output.status.value,
    }


@router.get("/{project_id}")
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = GetProjectUseCase(uow=uow)
    output = use_case.execute(ProjectId(project_id))
    return {
        "id": str(output.id),
        "name": output.name,
        "description": output.description,
        "created_by": str(output.created_by),
        "expected_end_date": output.expected_end_date.value.isoformat() if output.expected_end_date else None,
        "status": output.status.value,
    }


@router.post("/{project_id}/llm")
def configure_llm(
    project_id: UUID,
    payload: ConfigureLlmRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = ConfigureProjectLlmUseCase(uow=uow)
    output = use_case.execute(ConfigureProjectLlmInput(
        project_id=ProjectId(project_id),
        provider=payload.provider,
        api_key_encrypted=payload.api_key_encrypted,
    ))
    return {
        "id": str(output.id),
        "name": output.name,
        "llm_enabled": True,
        "llm_provider": payload.provider,
    }


@router.post("/{project_id}/roles")
def create_role(
    project_id: UUID,
    payload: CreateRoleRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = CreateRoleUseCase(uow=uow)
    output = use_case.execute(CreateRoleInput(
        project_id=ProjectId(project_id),
        name=payload.name,
        description=payload.description,
    ))
    return {
        "id": str(output.id),
        "project_id": str(output.project_id),
        "name": output.name,
        "description": output.description,
    }
