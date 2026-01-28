"""Task endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_tasks():
    """List tasks (placeholder)."""
    return {"tasks": []}
