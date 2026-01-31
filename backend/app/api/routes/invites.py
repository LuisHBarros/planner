"""Invite routes."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_unit_of_work
from app.application.dtos.project_dtos import AcceptInviteInput, CreateProjectInviteInput
from app.application.use_cases.accept_invite import AcceptInviteUseCase
from app.application.use_cases.create_project_invite import CreateProjectInviteUseCase
from app.application.use_cases.view_invite import ViewInviteUseCase
from app.domain.models.enums import MemberLevel
from app.domain.models.user import User
from app.domain.models.value_objects import InviteToken, ProjectId, RoleId, UtcDateTime
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

router = APIRouter()


class CreateInviteRequest(BaseModel):
    email: str
    role_id: UUID | None = None
    expires_at: datetime | None = None


class AcceptInviteRequest(BaseModel):
    token: str
    level: str
    base_capacity: int


@router.post("/project/{project_id}")
def create_invite(
    project_id: UUID,
    payload: CreateInviteRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    with uow:
        project = uow.projects.find_by_id(ProjectId(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_manager(current_user.id):
        raise HTTPException(status_code=403, detail="Manager access required")

    use_case = CreateProjectInviteUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(CreateProjectInviteInput(
        project_id=ProjectId(project_id),
        email=payload.email,
        role_id=RoleId(payload.role_id) if payload.role_id else None,
        expires_at=UtcDateTime(payload.expires_at) if payload.expires_at else None,
    ))
    return {
        "id": str(output.id),
        "project_id": str(output.project_id),
        "email": output.email,
        "token": str(output.token),
        "role_id": str(output.role_id) if output.role_id else None,
        "status": output.status.value,
        "expires_at": output.expires_at.value.isoformat() if output.expires_at else None,
    }


@router.get("/token/{token}")
def view_invite(
    token: str,
    _current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = ViewInviteUseCase(uow=uow)
    output = use_case.execute(InviteToken(token))
    return {
        "id": str(output.id),
        "project_id": str(output.project_id),
        "email": output.email,
        "token": str(output.token),
        "role_id": str(output.role_id) if output.role_id else None,
        "status": output.status.value,
        "expires_at": output.expires_at.value.isoformat() if output.expires_at else None,
    }


@router.post("/accept")
def accept_invite(
    payload: AcceptInviteRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
):
    use_case = AcceptInviteUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(AcceptInviteInput(
        token=InviteToken(payload.token),
        user_id=current_user.id,
        level=MemberLevel(payload.level),
        base_capacity=payload.base_capacity,
    ))
    return {
        "id": str(output.id),
        "project_id": str(output.project_id),
        "email": output.email,
        "token": str(output.token),
        "role_id": str(output.role_id) if output.role_id else None,
        "status": output.status.value,
        "expires_at": output.expires_at.value.isoformat() if output.expires_at else None,
    }
