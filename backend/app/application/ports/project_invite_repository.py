"""ProjectInvite repository port."""
from typing import Protocol, Optional, List

from app.domain.models.project_invite import ProjectInvite
from app.domain.models.value_objects import InviteToken, ProjectId, ProjectInviteId


class ProjectInviteRepository(Protocol):
    """Repository interface for ProjectInvite entities."""

    def save(self, invite: ProjectInvite) -> None:
        """Persist a project invite."""
        ...

    def find_by_id(self, invite_id: ProjectInviteId) -> Optional[ProjectInvite]:
        """Find invite by ID."""
        ...

    def find_by_token(self, token: InviteToken) -> Optional[ProjectInvite]:
        """Find invite by token."""
        ...

    def list_by_project(self, project_id: ProjectId) -> List[ProjectInvite]:
        """List invites for a project."""
        ...
