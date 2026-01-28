"""Role endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_roles():
    """List roles (placeholder)."""
    return {"roles": []}
