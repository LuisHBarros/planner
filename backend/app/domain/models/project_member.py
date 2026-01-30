"""ProjectMember domain model (v3.0 BR-PROJ, BR-WORK)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import ProjectMemberRole, RoleLevel


# Level multipliers for capacity calculation (BR-WORK-001)
LEVEL_MULTIPLIERS = {
    RoleLevel.JUNIOR: 0.6,
    RoleLevel.MID: 1.0,
    RoleLevel.SENIOR: 1.3,
    RoleLevel.SPECIALIST: 1.2,
    RoleLevel.LEAD: 1.1,
}


class ProjectMember:
    """
    Project member entity representing a user's membership in a project (v3.0).

    Attributes:
        id: Unique identifier
        project_id: The project this membership belongs to
        user_id: The user who is a member
        role: MANAGER or EMPLOYEE (BR-PROJ-001)
        level: Seniority level (JUNIOR/MID/SENIOR/SPECIALIST/LEAD)
        is_active: Whether the membership is active
        joined_at: When the user joined the project
        left_at: When the user left (if applicable)
    """

    def __init__(
        self,
        id: UUID,
        project_id: UUID,
        user_id: UUID,
        role: ProjectMemberRole,
        level: RoleLevel,
        is_active: bool = True,
        joined_at: Optional[datetime] = None,
        left_at: Optional[datetime] = None,
    ):
        self.id = id
        self.project_id = project_id
        self.user_id = user_id
        self.role = role
        self.level = level
        self.is_active = is_active
        self.joined_at = joined_at or datetime.now(UTC)
        self.left_at = left_at

    @classmethod
    def create(
        cls,
        project_id: UUID,
        user_id: UUID,
        role: ProjectMemberRole,
        level: RoleLevel,
    ) -> "ProjectMember":
        """Create a new project member."""
        return cls(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            role=role,
            level=level,
            is_active=True,
        )

    @classmethod
    def create_manager(
        cls,
        project_id: UUID,
        user_id: UUID,
        level: RoleLevel = RoleLevel.LEAD,
    ) -> "ProjectMember":
        """Create a new project manager."""
        return cls.create(
            project_id=project_id,
            user_id=user_id,
            role=ProjectMemberRole.MANAGER,
            level=level,
        )

    @classmethod
    def create_employee(
        cls,
        project_id: UUID,
        user_id: UUID,
        level: RoleLevel,
    ) -> "ProjectMember":
        """Create a new project employee."""
        return cls.create(
            project_id=project_id,
            user_id=user_id,
            role=ProjectMemberRole.EMPLOYEE,
            level=level,
        )

    def is_manager(self) -> bool:
        """Check if this member is a manager (BR-PROJ-002)."""
        return self.role == ProjectMemberRole.MANAGER

    def is_employee(self) -> bool:
        """Check if this member is an employee."""
        return self.role == ProjectMemberRole.EMPLOYEE

    def get_level_multiplier(self) -> float:
        """
        Get the capacity multiplier for this member's level (BR-WORK-001).

        Returns:
            Multiplier value (0.6 for JUNIOR to 1.3 for SENIOR)
        """
        return LEVEL_MULTIPLIERS.get(self.level, 1.0)

    def calculate_capacity(self, base_capacity: int) -> float:
        """
        Calculate effective capacity based on level (BR-WORK-001).

        Args:
            base_capacity: The base capacity to apply multiplier to

        Returns:
            Effective capacity (base * multiplier)
        """
        return base_capacity * self.get_level_multiplier()

    def deactivate(self, left_at: Optional[datetime] = None) -> None:
        """Deactivate this membership (user left project)."""
        self.is_active = False
        self.left_at = left_at or datetime.now(UTC)

    def reactivate(self) -> None:
        """Reactivate this membership."""
        self.is_active = True
        self.left_at = None
