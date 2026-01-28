"""Team endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_teams():
    """List teams (placeholder)."""
    return {"teams": []}
