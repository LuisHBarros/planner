"""Project endpoints."""
from datetime import datetime, UTC
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
    SqlAlchemyTaskDependencyRepository,
)
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.use_cases.rank_tasks import RankTasksUseCase
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.enums import (
    ProjectStatus,
    TaskStatus,
    TaskPriority,
    CompletionSource,
    DependencyType,
)

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
    
    Only team managers can rank tasks. In MVP, actor_user_id is optional
    and permission check is skipped if not provided.
    
    Note: actor_user_id is a temporary MVP mechanism. In production, this value
    MUST come from the authenticated request context (JWT/session), not from client input.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    project_repo = SqlAlchemyProjectRepository(db)
    
    # Get event bus from app state
    event_bus = fastapi_request.app.state.event_bus
    
    team_member_repo = None
    try:
        from app.infrastructure.persistence.repositories import (
            SqlAlchemyTeamMemberRepository,
        )
        team_member_repo = SqlAlchemyTeamMemberRepository(db)
    except ImportError:
        pass
    
    use_case = RankTasksUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        event_bus=event_bus,
        team_member_repository=team_member_repo,
    )
    
    # In MVP, accept actor_user_id from query param (optional)
    actor_user_id = None  # Would come from auth context in production
    
    tasks = use_case.execute(
        project_id=project_id,
        task_ids=request.task_ids,
        actor_user_id=actor_user_id,
    )
    
    db.commit()
    
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks]
    )


class DependencyGraphNode(BaseModel):
    """Node in dependency graph."""
    task_id: str
    title: str
    status: TaskStatus
    expected_start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    is_delayed: bool = False


class DependencyGraphEdge(BaseModel):
    """Edge in dependency graph."""
    from_task_id: str
    to_task_id: str
    type: str


class DependencyGraphResponse(BaseModel):
    """Response model for project dependency graph."""
    nodes: List[DependencyGraphNode]
    edges: List[DependencyGraphEdge]


class TimelineTask(BaseModel):
    """Task in timeline view."""
    id: str
    title: str
    expected_start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    actual_start_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    is_delayed: bool
    blocking_dependencies: int
    blocked_by: List[str]


class TimelineResponse(BaseModel):
    """Response model for project timeline."""
    project_id: str
    tasks: List[TimelineTask]


@router.get("/{project_id}/dependency-graph", response_model=DependencyGraphResponse)
async def get_project_dependency_graph(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get dependency graph for a project (read-only).
    
    Returns nodes (tasks) and edges (dependencies) for UI visualization
    (timeline, Gantt, DAG view). This is a read model and does not change domain state.
    """
    project_repo = SqlAlchemyProjectRepository(db)
    task_repo = SqlAlchemyTaskRepository(db)
    dep_repo = SqlAlchemyTaskDependencyRepository(db)
    
    # Verify project exists
    project = project_repo.find_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Load all tasks in project
    tasks = task_repo.find_by_project_id(project_id)
    task_ids = {t.id for t in tasks}
    
    # Build nodes
    nodes = []
    for task in tasks:
        # Handle optional scheduling fields (Spec 2.0)
        expected_start = None
        expected_end = None
        is_delayed = False
        
        if hasattr(task, "expected_start_date") and task.expected_start_date:
            expected_start = task.expected_start_date.isoformat()
        if hasattr(task, "expected_end_date") and task.expected_end_date:
            expected_end = task.expected_end_date.isoformat()
        if hasattr(task, "is_delayed"):
            is_delayed = task.is_delayed
        
        nodes.append(
            DependencyGraphNode(
                task_id=str(task.id),
                title=task.title,
                status=task.status,
                expected_start_date=expected_start,
                expected_end_date=expected_end,
                is_delayed=is_delayed,
            )
        )
    
    # Build edges (dependencies where both tasks are in project)
    edges = []
    for task in tasks:
        deps = dep_repo.find_by_task_id(task.id)
        for dep in deps:
            # Only include edges where both tasks are in this project
            if dep.depends_on_task_id in task_ids:
                edges.append(
                    DependencyGraphEdge(
                        from_task_id=str(dep.depends_on_task_id),
                        to_task_id=str(dep.task_id),
                        type=dep.dependency_type.value,
                    )
                )
    
    return DependencyGraphResponse(nodes=nodes, edges=edges)


@router.get("/{project_id}/timeline", response_model=TimelineResponse)
async def get_project_timeline(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get timeline summary for a project (derived view).
    
    Provides a timeline-friendly dataset for frontend planning views.
    This is a computed projection, not persisted data.
    """
    project_repo = SqlAlchemyProjectRepository(db)
    task_repo = SqlAlchemyTaskRepository(db)
    dep_repo = SqlAlchemyTaskDependencyRepository(db)
    
    # Verify project exists
    project = project_repo.find_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Load all tasks in project
    tasks = task_repo.find_by_project_id(project_id)
    
    # Build timeline tasks with computed fields
    timeline_tasks = []
    now = datetime.now(UTC)
    
    for task in tasks:
        # Extract scheduling fields (optional, Spec 2.0)
        expected_start = None
        expected_end = None
        actual_start = None
        actual_end = None
        
        if hasattr(task, "expected_start_date") and task.expected_start_date:
            expected_start = task.expected_start_date.isoformat()
        if hasattr(task, "expected_end_date") and task.expected_end_date:
            expected_end = task.expected_end_date.isoformat()
        if hasattr(task, "actual_start_date") and task.actual_start_date:
            actual_start = task.actual_start_date.isoformat()
        if hasattr(task, "actual_end_date") and task.actual_end_date:
            actual_end = task.actual_end_date.isoformat()
        
        # Compute is_delayed: now > expected_end_date AND status != done
        is_delayed = False
        if expected_end:
            try:
                expected_end_dt = datetime.fromisoformat(expected_end.replace("Z", "+00:00"))
                if now > expected_end_dt and task.status != TaskStatus.DONE:
                    is_delayed = True
            except (ValueError, AttributeError):
                pass
        elif hasattr(task, "is_delayed"):
            is_delayed = task.is_delayed
        
        # Count blocking dependencies not completed
        blocking_deps = dep_repo.find_by_task_id(task.id)
        blocking_deps = [
            d
            for d in blocking_deps
            if d.dependency_type == DependencyType.BLOCKS
        ]
        
        blocking_dependencies = 0
        blocked_by = []
        
        for dep in blocking_deps:
            blocker_task = task_repo.find_by_id(dep.depends_on_task_id)
            if blocker_task and blocker_task.status != TaskStatus.DONE:
                blocking_dependencies += 1
                blocked_by.append(str(dep.depends_on_task_id))
        
        timeline_tasks.append(
            TimelineTask(
                id=str(task.id),
                title=task.title,
                expected_start_date=expected_start,
                expected_end_date=expected_end,
                actual_start_date=actual_start,
                actual_end_date=actual_end,
                is_delayed=is_delayed,
                blocking_dependencies=blocking_dependencies,
                blocked_by=blocked_by,
            )
        )
    
    return TimelineResponse(
        project_id=str(project_id),
        tasks=timeline_tasks,
    )
