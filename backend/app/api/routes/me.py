"""Endpoints related to the current user (/me) context."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyTeamMemberRepository,
    SqlAlchemyTeamRepository,
)
from app.application.use_cases.get_user_teams import GetUserTeamsUseCase
from app.domain.models.team import Team


router = APIRouter()


class MeTeamResponse(BaseModel):
    """Response model for a team in /me/teams."""

    id: str
    name: str
    created_at: str


class MeTeamsListResponse(BaseModel):
    """Response model for list of teams for current user."""

    teams: List[MeTeamResponse]


def _team_to_me_response(team: Team) -> MeTeamResponse:
    return MeTeamResponse(
        id=str(team.id),
        name=team.name,
        created_at=team.created_at.isoformat(),
    )


@router.get("/me/teams", response_model=MeTeamsListResponse)
async def get_my_teams(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    List teams for the current user (Spec 3.0 /me/teams).

    For MVP we accept `user_id` as a query parameter.
    In production, this would be derived from the authenticated JWT.
    """
    member_repo = SqlAlchemyTeamMemberRepository(db)
    team_repo = SqlAlchemyTeamRepository(db)

    use_case = GetUserTeamsUseCase(
        team_member_repository=member_repo,
        team_repository=team_repo,
    )

    teams = use_case.execute(user_id=user_id)

    return MeTeamsListResponse(
        teams=[_team_to_me_response(t) for t in teams]
    )

