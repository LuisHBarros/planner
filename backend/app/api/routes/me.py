"""Current user routes."""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.domain.models.user import User

router = APIRouter()


@router.get("")
def get_me(current_user: User = Depends(get_current_user)):
    """Return current user profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at.value.isoformat(),
    }
