"""Role endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyRoleRepository,
    SqlAlchemyTeamRepository,
)
from app.application.use_cases.create_role import CreateRoleUseCase
from app.domain.models.role import Role
from app.domain.models.enums import RoleLevel

router = APIRouter()


# Request/Response DTOs
class CreateRoleRequest(BaseModel):
    """Request model for creating a role."""
    team_id: UUID
    name: str
    level: RoleLevel
    base_capacity: int = Field(ge=1, description="Default tasks per person")
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Response model for a role."""
    id: str
    team_id: str
    name: str
    level: RoleLevel
    base_capacity: int
    description: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Response model for list of roles."""
    roles: List[RoleResponse]


def _role_to_response(role: Role) -> RoleResponse:
    """Convert domain role to response model."""
    return RoleResponse(
        id=str(role.id),
        team_id=str(role.team_id),
        name=role.name,
        level=role.level,
        base_capacity=role.base_capacity,
        description=role.description,
        created_at=role.created_at.isoformat(),
    )


@router.get("/", response_model=RoleListResponse)
async def list_roles(
    team_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """List roles, optionally filtered by team."""
    repo = SqlAlchemyRoleRepository(db)
    
    if team_id:
        roles = repo.find_by_team_id(team_id)
    else:
        # For MVP, list all roles (would normally require auth)
        roles = repo.find_all()
    
    return RoleListResponse(
        roles=[_role_to_response(r) for r in roles]
    )


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: CreateRoleRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new role (UC-003).
    
    Roles define responsibility types within a team (e.g., Backend Senior,
    Frontend Junior). Tasks are assigned to roles, not directly to users.
    """
    role_repo = SqlAlchemyRoleRepository(db)
    team_repo = SqlAlchemyTeamRepository(db)
    
    use_case = CreateRoleUseCase(
        role_repository=role_repo,
        team_repository=team_repo,
    )
    
    role = use_case.execute(
        team_id=request.team_id,
        name=request.name,
        level=request.level,
        base_capacity=request.base_capacity,
        description=request.description,
    )
    
    db.commit()
    
    return _role_to_response(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a role by ID."""
    repo = SqlAlchemyRoleRepository(db)
    role = repo.find_by_id(role_id)
    
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )
    
    return _role_to_response(role)
