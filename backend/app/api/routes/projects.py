"""Project endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyProjectRepository,
    SqlAlchemyTeamRepository,
    SqlAlchemyTaskRepository,
)
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.use_cases.rank_tasks import RankTasksUseCase
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.enums import ProjectStatus, TaskStatus, TaskPriority, CompletionSource

router = APIRouter()


# Request/Response DTOs
class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""
    team_id: UUID
    name: str
    description: Optional[str] = None


class RankTasksRequest(BaseModel):
    """Request model for ranking tasks."""
    task_ids: List[UUID]


class ProjectResponse(BaseModel):
    """Response model for a project."""
    id: str
    team_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    created_at: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Response model for a task."""
    id: str
    project_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    rank_index: float
    role_responsible_id: str
    user_responsible_id: Optional[str] = None
    completion_percentage: Optional[int] = None
    completion_source: Optional[CompletionSource] = None
    due_date: Optional[str] = None
    blocked_reason: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response model for list of projects."""
    projects: List[ProjectResponse]


class TaskListResponse(BaseModel):
    """Response model for list of tasks."""
    tasks: List[TaskResponse]


def _project_to_response(project: Project) -> ProjectResponse:
    """Convert domain project to response model."""
    return ProjectResponse(
        id=str(project.id),
        team_id=str(project.team_id),
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at.isoformat(),
    )


def _task_to_response(task: Task) -> TaskResponse:
    """Convert domain task to response model."""
    return TaskResponse(
        id=str(task.id),
        project_id=str(task.project_id),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        rank_index=task.rank_index,
        role_responsible_id=str(task.role_responsible_id),
        user_responsible_id=str(task.user_responsible_id) if task.user_responsible_id else None,
        completion_percentage=task.completion_percentage,
        completion_source=task.completion_source,
        due_date=task.due_date.isoformat() if task.due_date else None,
        blocked_reason=task.blocked_reason,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    team_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """List projects, optionally filtered by team."""
    repo = SqlAlchemyProjectRepository(db)
    
    if team_id:
        projects = repo.find_by_team_id(team_id)
    else:
        # For MVP, list all projects (would normally require auth)
        projects = repo.find_all()
    
    return ProjectListResponse(
        projects=[_project_to_response(p) for p in projects]
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new project (UC-004).
    
    Projects contain tasks and belong to a team.
    """
    project_repo = SqlAlchemyProjectRepository(db)
    team_repo = SqlAlchemyTeamRepository(db)
    
    use_case = CreateProjectUseCase(
        project_repository=project_repo,
        team_repository=team_repo,
    )
    
    project = use_case.execute(
        team_id=request.team_id,
        name=request.name,
        description=request.description,
    )
    
    db.commit()
    
    return _project_to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a project by ID."""
    repo = SqlAlchemyProjectRepository(db)
    project = repo.find_by_id(project_id)
    
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return _project_to_response(project)


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
async def list_project_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """List all tasks in a project, ordered by rank."""
    project_repo = SqlAlchemyProjectRepository(db)
    task_repo = SqlAlchemyTaskRepository(db)
    
    # Verify project exists
    project = project_repo.find_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    tasks = task_repo.find_by_project_id(project_id)
    
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks]
    )


@router.post("/{project_id}/tasks/rank", response_model=TaskListResponse)
async def rank_tasks(
    project_id: UUID,
    request: RankTasksRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Rank tasks in a project (UC-009).
    
    Reorders tasks based on the provided list of task IDs.
    The order of task_ids defines the new ranking.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    
    # Get event bus from app state
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = RankTasksUseCase(
        task_repository=task_repo,
        event_bus=event_bus,
    )
    
    tasks = use_case.execute(
        project_id=project_id,
        task_ids=request.task_ids,
    )
    
    db.commit()
    
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks]
    )
