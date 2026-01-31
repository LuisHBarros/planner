"""Role domain model."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.value_objects import ProjectId, RoleId, UtcDateTime


@dataclass
class Role:
    """Role within a project."""
    id: RoleId
    project_id: ProjectId
    name: str
    description: Optional[str]
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        name: str,
        description: Optional[str] = None,
    ) -> "Role":
        """Create a new role."""
        return cls(
            id=RoleId(),
            project_id=project_id,
            name=name.strip(),
            description=description,
        )
