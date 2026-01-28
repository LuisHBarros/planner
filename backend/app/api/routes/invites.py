"""Invitation endpoints (Spec 3.0)."""
from uuid import UUID
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyTeamRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyTeamInviteRepository,
    SqlAlchemyTeamMemberRepository,
)
from app.application.use_cases.create_team_invite import CreateTeamInviteUseCase
from app.application.use_cases.accept_team_invite import AcceptTeamInviteUseCase
from app.domain.models.team_invite import TeamInvite
from app.domain.models.team_member import TeamMember
from app.domain.models.enums import TeamMemberRole
from app.domain.exceptions import BusinessRuleViolation


router = APIRouter()


class CreateInviteRequest(BaseModel):
    """Request model to create a team invite."""

    role: TeamMemberRole = TeamMemberRole.MEMBER
    expires_at: Optional[datetime] = None
    created_by_user_id: UUID


class TeamInviteResponse(BaseModel):
    """Response model for a team invite."""

    id: str
    team_id: str
    role: TeamMemberRole
    token: str
    expires_at: str
    created_by: str
    created_at: str
    used_at: Optional[str] = None


class AcceptInviteRequest(BaseModel):
    """Request model for accepting an invite."""

    user_id: UUID


class TeamMemberResponse(BaseModel):
    """Response model for team membership."""

    id: str
    user_id: str
    team_id: str
    role: TeamMemberRole
    joined_at: str


def _invite_to_response(invite: TeamInvite) -> TeamInviteResponse:
    return TeamInviteResponse(
        id=str(invite.id),
        team_id=str(invite.team_id),
        role=invite.role,
        token=invite.token,
        expires_at=invite.expires_at.isoformat(),
        created_by=str(invite.created_by),
        created_at=invite.created_at.isoformat(),
        used_at=invite.used_at.isoformat() if invite.used_at else None,
    )


def _member_to_response(member: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=str(member.id),
        user_id=str(member.user_id),
        team_id=str(member.team_id),
        role=member.role,
        joined_at=member.joined_at.isoformat(),
    )


@router.post(
    "/teams/{team_id}/invites",
    response_model=TeamInviteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team_invite(
    team_id: UUID,
    request: CreateInviteRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new invitation link for a team.

    This corresponds to the manager creating an invite in Spec 3.0.
    """
    team_repo = SqlAlchemyTeamRepository(db)
    invite_repo = SqlAlchemyTeamInviteRepository(db)

    use_case = CreateTeamInviteUseCase(
        team_repository=team_repo,
        invite_repository=invite_repo,
    )

    try:
        invite = use_case.execute(
            team_id=team_id,
            role=request.role,
            created_by=request.created_by_user_id,
            expires_at=request.expires_at,
        )
    except BusinessRuleViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc

    db.commit()

    return _invite_to_response(invite)


@router.post(
    "/invites/{token}/accept",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_invite(
    token: str,
    request: AcceptInviteRequest,
    db: Session = Depends(get_db),
):
    """
    Accept an invitation link.

    In a full implementation this would be called after magic-link login,
    using the authenticated user id instead of a raw `user_id` field.
    """
    invite_repo = SqlAlchemyTeamInviteRepository(db)
    member_repo = SqlAlchemyTeamMemberRepository(db)
    user_repo = SqlAlchemyUserRepository(db)
    team_repo = SqlAlchemyTeamRepository(db)

    use_case = AcceptTeamInviteUseCase(
        invite_repository=invite_repo,
        member_repository=member_repo,
        user_repository=user_repo,
        team_repository=team_repo,
    )

    try:
        member = use_case.execute(token=token, user_id=request.user_id)
    except BusinessRuleViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc

    db.commit()

    return _member_to_response(member)

