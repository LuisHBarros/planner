"""UC-001: Register User use case."""
from app.application.dtos.auth_dtos import RegisterUserInput, UserOutput
from app.application.events.domain_events import UserRegistered
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.user import User


class RegisterUserUseCase:
    """Use case for registering a user (UC-001, BR-AUTH-003)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: RegisterUserInput) -> UserOutput:
        """Register a new user."""
        with self.uow:
            existing = self.uow.users.find_by_email(input_dto.email.lower().strip())
            if existing is not None:
                raise BusinessRuleViolation(
                    "Email already registered",
                    code="email_already_registered",
                )

            user = User.create(email=input_dto.email, name=input_dto.name)
            self.uow.users.save(user)
            self.uow.commit()

            self.event_bus.emit(UserRegistered(user_id=user.id, email=user.email))
            return UserOutput.from_domain(user)
