"""ProjectInvite domain model."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.domain.models.enums import InviteStatus
from app.domain.models.value_objects import InviteToken, ProjectId, ProjectInviteId, RoleId, UtcDateTime
from app.domain.exceptions import BusinessRuleViolation


@dataclass
class ProjectInvite:
    """Invitation to join a project."""
    id: ProjectInviteId
    project_id: ProjectId
    email: str
    token: InviteToken
    role_id: Optional[RoleId]
    status: InviteStatus
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)
    expires_at: Optional[UtcDateTime] = None

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        email: str,
        token: InviteToken,
        role_id: Optional[RoleId] = None,
        expires_at: Optional[datetime] = None,
    ) -> "ProjectInvite":
        """Create a new project invite."""
        return cls(
            id=ProjectInviteId(),
            project_id=project_id,
            email=email.lower().strip(),
            token=token,
            role_id=role_id,
            status=InviteStatus.PENDING,
            expires_at=UtcDateTime(expires_at) if expires_at else None,
        )

    def accept(self) -> None:
        """Accept invite if still pending."""
        if self.status != InviteStatus.PENDING:
            raise BusinessRuleViolation("Invite is not pending", code="invite_not_pending")
        if self.is_expired():
            raise BusinessRuleViolation("Invite is expired", code="invite_expired")
        self.status = InviteStatus.ACCEPTED

    def is_expired(self) -> bool:
        """Check whether invite has expired."""
        if self.expires_at is None:
            return False
        return self.expires_at.value < datetime.now(timezone.utc)
