"""UC-002: Invite User to Team use case (simplified for MVP)."""
from uuid import UUID
from typing import List

from app.domain.models.user import User
from app.application.ports.user_repository import UserRepository
from app.application.ports.team_repository import TeamRepository
from app.application.ports.role_repository import RoleRepository
from app.domain.exceptions import BusinessRuleViolation


class InviteUserToTeamUseCase:
    """Use case for inviting a user to a team (UC-002 - simplified)."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        team_repository: TeamRepository,
        role_repository: RoleRepository,
    ):
        self.user_repository = user_repository
        self.team_repository = team_repository
        self.role_repository = role_repository
    
    def execute(
        self,
        team_id: UUID,
        email: str,
        name: str,
        role_ids: List[UUID],
    ) -> User:
        """
        Invite/add a user to a team (simplified - no email sending in MVP).
        
        Flow:
        1. Validate team exists
        2. Validate roles exist and belong to team
        3. Find or create user
        4. Assign roles (simplified - just return user)
        5. Return user details
        
        Note: In full implementation, this would send an invitation email.
        For MVP, we just create/link the user.
        """
        # Validate team exists
        team = self.team_repository.find_by_id(team_id)
        if team is None:
            raise BusinessRuleViolation(
                f"Team with id {team_id} not found",
                code="team_not_found"
            )
        
        # Validate roles exist and belong to team
        team_roles = self.role_repository.find_by_team_id(team_id)
        team_role_ids = {role.id for role in team_roles}
        
        for role_id in role_ids:
            if role_id not in team_role_ids:
                raise BusinessRuleViolation(
                    f"Role {role_id} does not belong to team {team_id}",
                    code="role_not_in_team"
                )
        
        # Find or create user
        user = self.user_repository.find_by_email(email)
        if user is None:
            user = User.create(
                email=email,
                name=name,
            )
            self.user_repository.save(user)
        
        # Note: In full implementation, we'd create a UserTeamRole junction record
        # For MVP, we'll just return the user. The actual role assignment
        # would be handled by a separate service or in the repository.
        
        return user
