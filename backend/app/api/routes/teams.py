"""Team endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyTeamRepository,
    SqlAlchemyCompanyRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyRoleRepository,
)
from app.application.use_cases.create_team import CreateTeamUseCase
from app.application.use_cases.invite_user_to_team import InviteUserToTeamUseCase
from app.domain.models.team import Team
from app.domain.models.user import User

router = APIRouter()


# Request/Response DTOs
class CreateTeamRequest(BaseModel):
    """Request model for creating a team."""
    company_id: UUID
    name: str
    description: Optional[str] = None
    default_language: str = "en"


class InviteUserRequest(BaseModel):
    """Request model for inviting a user to a team."""
    email: EmailStr
    name: str
    role_ids: List[UUID] = []


class TeamResponse(BaseModel):
    """Response model for a team."""
    id: str
    company_id: str
    name: str
    description: Optional[str] = None
    default_language: str
    created_at: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Response model for a user."""
    id: str
    email: str
    name: str
    preferred_language: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Response model for list of teams."""
    teams: List[TeamResponse]


def _team_to_response(team: Team) -> TeamResponse:
    """Convert domain team to response model."""
    return TeamResponse(
        id=str(team.id),
        company_id=str(team.company_id),
        name=team.name,
        description=team.description,
        default_language=team.default_language,
        created_at=team.created_at.isoformat(),
    )


def _user_to_response(user: User) -> UserResponse:
    """Convert domain user to response model."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        preferred_language=user.preferred_language,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
    )


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """List teams, optionally filtered by company."""
    repo = SqlAlchemyTeamRepository(db)
    
    if company_id:
        teams = repo.find_by_company_id(company_id)
    else:
        # For MVP, list all teams (would normally require auth)
        teams = repo.find_all()
    
    return TeamListResponse(
        teams=[_team_to_response(t) for t in teams]
    )


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    request: CreateTeamRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new team (UC-001).
    
    Creates a team under a company. The team can have its own
    default language for notifications.
    """
    team_repo = SqlAlchemyTeamRepository(db)
    company_repo = SqlAlchemyCompanyRepository(db)
    
    use_case = CreateTeamUseCase(
        team_repository=team_repo,
        company_repository=company_repo,
    )
    
    team = use_case.execute(
        company_id=request.company_id,
        name=request.name,
        description=request.description,
        default_language=request.default_language,
    )
    
    db.commit()
    
    return _team_to_response(team)


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a team by ID."""
    repo = SqlAlchemyTeamRepository(db)
    team = repo.find_by_id(team_id)
    
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found"
        )
    
    return _team_to_response(team)


@router.post("/{team_id}/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user_to_team(
    team_id: UUID,
    request: InviteUserRequest,
    db: Session = Depends(get_db),
):
    """
    Invite/add a user to a team (UC-002 - simplified).
    
    For MVP, this directly creates/links the user without sending
    an invitation email. In full implementation, this would send
    an email invitation.
    """
    user_repo = SqlAlchemyUserRepository(db)
    team_repo = SqlAlchemyTeamRepository(db)
    role_repo = SqlAlchemyRoleRepository(db)
    
    use_case = InviteUserToTeamUseCase(
        user_repository=user_repo,
        team_repository=team_repo,
        role_repository=role_repo,
    )
    
    user = use_case.execute(
        team_id=team_id,
        email=request.email,
        name=request.name,
        role_ids=request.role_ids,
    )
    
    db.commit()
    
    return _user_to_response(user)
