"""UC-002: Login User (magic link) use case."""
from uuid import uuid4

from app.application.dtos.auth_dtos import LoginUserInput, MagicLinkOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.magic_link import MagicLink
from app.domain.models.value_objects import InviteToken


class LoginUserUseCase:
    """Use case for requesting a magic link (UC-002)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: LoginUserInput) -> MagicLinkOutput:
        """Request a magic link for a user."""
        with self.uow:
            user = self.uow.users.find_by_email(input_dto.email.lower().strip())
            if user is None:
                raise BusinessRuleViolation("User not found", code="user_not_found")

            token = input_dto.token or InviteToken(str(uuid4()))
            magic_link = MagicLink.create(
                token=token,
                user_id=user.id,
                expires_at=input_dto.expires_at,
            )
            self.uow.magic_links.save(magic_link)
            self.uow.commit()

            self.uow.email_service.send_magic_link(user.email, str(token))
            return MagicLinkOutput(token=token, expires_at=magic_link.expires_at)
