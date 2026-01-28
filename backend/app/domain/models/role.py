"""Role domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import RoleLevel


class Role:
    """Role entity - defines responsibilities within a team."""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        name: str,
        level: RoleLevel,
        base_capacity: int,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.team_id = team_id
        self.name = name
        self.level = level
        self.base_capacity = base_capacity
        self.description = description
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        team_id: UUID,
        name: str,
        level: RoleLevel,
        base_capacity: int,
        description: Optional[str] = None,
    ) -> "Role":
        """Create a new role."""
        if base_capacity < 1:
            raise ValueError("base_capacity must be at least 1")
        return cls(
            id=uuid4(),
            team_id=team_id,
            name=name,
            level=level,
            base_capacity=base_capacity,
            description=description,
        )
