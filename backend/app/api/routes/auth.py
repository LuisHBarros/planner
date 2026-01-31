"""Auth routes."""
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_unit_of_work
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.application.dtos.auth_dtos import (
    LoginUserInput,
    RegisterUserInput,
    VerifyMagicLinkInput,
)
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.verify_magic_link import VerifyMagicLinkUseCase
from app.domain.models.value_objects import InviteToken, UtcDateTime

router = APIRouter()


class RegisterRequest(BaseModel):
    """Register request body."""
    email: str
    name: str


class LoginRequest(BaseModel):
    """Login request body."""
    email: str
    expires_at: datetime


class VerifyRequest(BaseModel):
    """Verify magic link request body."""
    token: str


@router.post("/register")
def register_user(payload: RegisterRequest, uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)):
    """Register a new user."""
    use_case = RegisterUserUseCase(uow=uow, event_bus=uow.event_bus)
    output = use_case.execute(RegisterUserInput(email=payload.email, name=payload.name))
    return {
        "id": str(output.id),
        "email": output.email,
        "name": output.name,
        "created_at": output.created_at.value.isoformat(),
    }


@router.post("/login")
def login_user(payload: LoginRequest, uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)):
    """Request a magic link."""
    use_case = LoginUserUseCase(uow=uow)
    output = use_case.execute(LoginUserInput(
        email=payload.email,
        expires_at=UtcDateTime(payload.expires_at),
    ))
    return {
        "token": str(output.token),
        "expires_at": output.expires_at.value.isoformat(),
    }


@router.post("/verify")
def verify_magic_link(payload: VerifyRequest, uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)):
    """Verify magic link and return user."""
    use_case = VerifyMagicLinkUseCase(uow=uow)
    output = use_case.execute(VerifyMagicLinkInput(token=InviteToken(payload.token)))
    return {
        "id": str(output.id),
        "email": output.email,
        "name": output.name,
        "created_at": output.created_at.value.isoformat(),
    }
