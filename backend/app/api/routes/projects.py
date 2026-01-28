"""Project endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_projects():
    """List projects (placeholder)."""
    return {"projects": []}
