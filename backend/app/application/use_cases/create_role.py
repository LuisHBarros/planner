"""UC-003: Create Role use case."""
from uuid import UUID
from typing import Optional

from app.domain.models.role import Role
from app.domain.models.enums import RoleLevel
from app.application.ports.role_repository import RoleRepository
from app.application.ports.team_repository import TeamRepository
from app.domain.exceptions import BusinessRuleViolation


class CreateRoleUseCase:
    """Use case for creating a role (UC-003)."""
    
    def __init__(
        self,
        role_repository: RoleRepository,
        team_repository: TeamRepository,
    ):
        self.role_repository = role_repository
        self.team_repository = team_repository
    
    def execute(
        self,
        team_id: UUID,
        name: str,
        level: RoleLevel,
        base_capacity: int,
        description: Optional[str] = None,
    ) -> Role:
        """
        Create a new role.
        
        Flow:
        1. Validate team exists
        2. Validate uniqueness (name + level per team)
        3. Create role
        4. Return role details
        """
        # Validate team exists
        team = self.team_repository.find_by_id(team_id)
        if team is None:
            raise BusinessRuleViolation(
                f"Team with id {team_id} not found",
                code="team_not_found"
            )
        
        # Validate uniqueness (name + level per team)
        existing_roles = self.role_repository.find_by_team_id(team_id)
        for role in existing_roles:
            if role.name == name and role.level == level:
                raise BusinessRuleViolation(
                    f"Role {name} ({level}) already exists in this team",
                    code="role_already_exists"
                )
        
        # Create role
        role = Role.create(
            team_id=team_id,
            name=name,
            level=level,
            base_capacity=base_capacity,
            description=description,
        )
        
        # Save
        self.role_repository.save(role)
        
        return role
