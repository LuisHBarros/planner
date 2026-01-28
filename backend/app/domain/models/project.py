"""Project domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import ProjectStatus


class Project:
    """Project entity."""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        name: str,
        description: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.ACTIVE,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.team_id = team_id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        team_id: UUID,
        name: str,
        description: Optional[str] = None,
    ) -> "Project":
        """Create a new project."""
        return cls(
            id=uuid4(),
            team_id=team_id,
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
        )
