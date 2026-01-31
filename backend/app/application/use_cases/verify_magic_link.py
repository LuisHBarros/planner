"""UC-002: Verify Magic Link use case."""
from app.application.dtos.auth_dtos import UserOutput, VerifyMagicLinkInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation


class VerifyMagicLinkUseCase:
    """Use case for verifying a magic link (UC-002)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: VerifyMagicLinkInput) -> UserOutput:
        """Verify a magic link and return user."""
        with self.uow:
            link = self.uow.magic_links.find_by_token(input_dto.token)
            if link is None:
                raise BusinessRuleViolation("Magic link not found", code="magic_link_not_found")

            link.consume()
            self.uow.magic_links.save(link)

            user = self.uow.users.find_by_id(link.user_id)
            if user is None:
                raise BusinessRuleViolation("User not found", code="user_not_found")

            self.uow.commit()
            return UserOutput.from_domain(user)
