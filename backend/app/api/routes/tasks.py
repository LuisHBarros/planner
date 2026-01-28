"""Task endpoints."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyTaskRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyNoteRepository,
    SqlAlchemyTaskDependencyRepository,
)
try:
    from app.infrastructure.persistence.repositories import (
        SqlAlchemyTeamMemberRepository,
    )
except ImportError:
    SqlAlchemyTeamMemberRepository = None  # type: ignore
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.claim_task import ClaimTaskUseCase
from app.application.use_cases.update_task_status import UpdateTaskStatusUseCase
from app.application.use_cases.add_task_note import AddTaskNoteUseCase
from app.application.use_cases.add_task_dependency import AddTaskDependencyUseCase
from app.application.use_cases.remove_task_dependency import RemoveTaskDependencyUseCase
from app.application.use_cases.update_task_progress_manual import UpdateTaskProgressManualUseCase
from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.enums import (
    TaskStatus,
    TaskPriority,
    CompletionSource,
    DependencyType,
    NoteType,
)
from app.domain.exceptions import BusinessRuleViolation

router = APIRouter()


# Request/Response DTOs
class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""
    project_id: UUID
    title: str
    description: str
    role_responsible_id: UUID
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class ClaimTaskRequest(BaseModel):
    """Request model for claiming a task."""
    user_id: UUID
    # Note: user_id is a temporary MVP mechanism.
    # In production, this value MUST come from the authenticated request context
    # (JWT/session) and not from client input.


class UpdateStatusRequest(BaseModel):
    """Request model for updating task status."""
    status: TaskStatus
    user_id: Optional[UUID] = None
    # Note: user_id is a temporary MVP mechanism.
    # In production, this value MUST come from the authenticated request context
    # (JWT/session) and not from client input.


class AddNoteRequest(BaseModel):
    """Request model for adding a note."""
    content: str
    author_id: UUID


class AddDependencyRequest(BaseModel):
    """Request model for adding a dependency."""
    depends_on_task_id: UUID
    dependency_type: DependencyType = DependencyType.BLOCKS


class UpdateProgressRequest(BaseModel):
    """Request model for updating progress."""
    completion_percentage: int = Field(ge=0, le=100)
    user_id: UUID
    # Note: user_id is a temporary MVP mechanism.
    # In production, this value MUST come from the authenticated request context
    # (JWT/session) and not from client input.


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


class NoteResponse(BaseModel):
    """Response model for a note."""
    id: str
    task_id: str
    content: str
    note_type: NoteType
    author_id: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TaskDependencyResponse(BaseModel):
    """Response model for a task dependency."""
    id: str
    task_id: str
    depends_on_task_id: str
    dependency_type: DependencyType
    created_at: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response model for list of tasks."""
    tasks: List[TaskResponse]


class NoteListResponse(BaseModel):
    """Response model for list of notes."""
    notes: List[NoteResponse]


class DependencyListResponse(BaseModel):
    """Response model for list of dependencies."""
    dependencies: List[TaskDependencyResponse]


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


def _note_to_response(note: Note) -> NoteResponse:
    """Convert domain note to response model."""
    return NoteResponse(
        id=str(note.id),
        task_id=str(note.task_id),
        content=note.content,
        note_type=note.note_type,
        author_id=str(note.author_id) if note.author_id else None,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat(),
    )


def _dependency_to_response(dep: TaskDependency) -> TaskDependencyResponse:
    """Convert domain dependency to response model."""
    return TaskDependencyResponse(
        id=str(dep.id),
        task_id=str(dep.task_id),
        depends_on_task_id=str(dep.depends_on_task_id),
        dependency_type=dep.dependency_type,
        created_at=dep.created_at.isoformat(),
    )


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    project_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    task_status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
):
    """
    List tasks with optional filters.
    
    - project_id: Filter by project
    - role_id: Filter by responsible role
    - user_id: Filter by assigned user
    - status: Filter by task status
    """
    task_repo = SqlAlchemyTaskRepository(db)
    
    if project_id:
        tasks = task_repo.find_by_project_id(project_id)
    elif role_id:
        tasks = task_repo.find_by_role_id(role_id, status=task_status)
    elif user_id:
        tasks = task_repo.find_by_user_id(user_id)
    else:
        # For MVP, return empty list without specific filter
        # In production, this would require auth and return user's tasks
        tasks = []
    
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks]
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Create a new task (UC-005).
    
    Tasks are assigned to roles, not directly to users.
    The rank_index is automatically calculated to place the task
    at the end of the project's task list.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    project_repo = SqlAlchemyProjectRepository(db)
    role_repo = SqlAlchemyRoleRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    # Get event bus from app state
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = CreateTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        role_repository=role_repo,
        note_repository=note_repo,
        event_bus=event_bus,
    )
    
    task = use_case.execute(
        project_id=request.project_id,
        title=request.title,
        description=request.description,
        role_responsible_id=request.role_responsible_id,
        priority=request.priority,
        due_date=request.due_date,
    )
    
    db.commit()
    
    return _task_to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a task by ID."""
    repo = SqlAlchemyTaskRepository(db)
    task = repo.find_by_id(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return _task_to_response(task)


@router.post("/{task_id}/claim", response_model=TaskResponse)
async def claim_task(
    task_id: UUID,
    request: ClaimTaskRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Claim a task (UC-006).
    
    Assigns the task to a user and changes status from 'todo' to 'doing'.
    The user must have the role that the task is assigned to.
    
    Note: user_id is a temporary MVP mechanism. In production, this value
    MUST come from the authenticated request context (JWT/session), not from client input.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    user_repo = SqlAlchemyUserRepository(db)
    role_repo = SqlAlchemyRoleRepository(db)
    project_repo = SqlAlchemyProjectRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = ClaimTaskUseCase(
        task_repository=task_repo,
        user_repository=user_repo,
        role_repository=role_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        event_bus=event_bus,
    )
    
    use_case.execute(
        task_id=task_id,
        user_id=request.user_id,
    )
    
    db.commit()
    
    # Reload task to get updated state
    task = task_repo.find_by_id(task_id)
    return _task_to_response(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: UUID,
    request: UpdateStatusRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Update task status (UC-007).
    
    Valid transitions:
    - todo → doing, blocked
    - doing → done, blocked
    - blocked → todo
    - done → (terminal, cannot change)
    
    Note: user_id is a temporary MVP mechanism. In production, this value
    MUST come from the authenticated request context (JWT/session), not from client input.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = UpdateTaskStatusUseCase(
        task_repository=task_repo,
        note_repository=note_repo,
        event_bus=event_bus,
    )
    
    task = use_case.execute(
        task_id=task_id,
        new_status=request.status,
        user_id=request.user_id,
    )
    
    db.commit()
    
    return _task_to_response(task)


@router.post("/{task_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def add_task_note(
    task_id: UUID,
    request: AddNoteRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Add a note to a task (UC-008).
    
    Notes form a timeline of comments and updates on a task.
    """
    note_repo = SqlAlchemyNoteRepository(db)
    task_repo = SqlAlchemyTaskRepository(db)
    
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = AddTaskNoteUseCase(
        note_repository=note_repo,
        task_repository=task_repo,
        event_bus=event_bus,
    )
    
    note = use_case.execute(
        task_id=task_id,
        content=request.content,
        author_id=request.author_id,
    )
    
    db.commit()
    
    return _note_to_response(note)


@router.get("/{task_id}/notes", response_model=NoteListResponse)
async def list_task_notes(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """List all notes for a task, ordered by creation time."""
    task_repo = SqlAlchemyTaskRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    # Verify task exists
    task = task_repo.find_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    notes = note_repo.find_by_task_id(task_id)
    
    return NoteListResponse(
        notes=[_note_to_response(n) for n in notes]
    )


@router.post("/{task_id}/dependencies", response_model=TaskDependencyResponse, status_code=status.HTTP_201_CREATED)
async def add_task_dependency(
    task_id: UUID,
    request: AddDependencyRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Add a dependency to a task (UC-010).
    
    When a blocking dependency is added and the blocker task is not done,
    the dependent task is automatically blocked.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    dep_repo = SqlAlchemyTaskDependencyRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = AddTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        note_repository=note_repo,
        event_bus=event_bus,
    )
    
    dependency = use_case.execute(
        task_id=task_id,
        depends_on_task_id=request.depends_on_task_id,
        dependency_type=request.dependency_type,
    )
    
    db.commit()
    
    return _dependency_to_response(dependency)


@router.get("/{task_id}/dependencies", response_model=DependencyListResponse)
async def list_task_dependencies(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """List all dependencies for a task (what this task depends on)."""
    task_repo = SqlAlchemyTaskRepository(db)
    dep_repo = SqlAlchemyTaskDependencyRepository(db)
    
    # Verify task exists
    task = task_repo.find_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    dependencies = dep_repo.find_by_task_id(task_id)
    
    return DependencyListResponse(
        dependencies=[_dependency_to_response(d) for d in dependencies]
    )


@router.delete("/{task_id}/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_dependency(
    task_id: UUID,
    dependency_id: UUID,
    request: Request,
    actor_user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """
    Remove a dependency between tasks.
    
    If the removed dependency was of type BLOCKS and no remaining blocking
    dependencies exist, the task will be automatically unblocked (status changes
    from blocked → todo). Status will not change if task is already doing or done.
    
    Only team managers can remove dependencies. In MVP, actor_user_id is optional
    and permission check is skipped if not provided.
    
    Note: actor_user_id is a temporary MVP mechanism. In production, this value
    MUST come from the authenticated request context (JWT/session), not from client input.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    dep_repo = SqlAlchemyTaskDependencyRepository(db)
    project_repo = SqlAlchemyProjectRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    event_bus = request.app.state.event_bus
    
    team_member_repo = None
    if SqlAlchemyTeamMemberRepository:
        team_member_repo = SqlAlchemyTeamMemberRepository(db)
    
    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=team_member_repo,
        event_bus=event_bus,
    )
    
    try:
        use_case.execute(
            task_id=task_id,
            dependency_id=dependency_id,
            actor_user_id=actor_user_id,
        )
    except BusinessRuleViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc
    
    db.commit()


@router.patch("/{task_id}/progress", response_model=TaskResponse)
async def update_task_progress(
    task_id: UUID,
    request: UpdateProgressRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    """
    Update task progress manually (UC-023).
    
    Sets the completion percentage (0-100) and marks it as manually set.
    
    Note: user_id is a temporary MVP mechanism. In production, this value
    MUST come from the authenticated request context (JWT/session), not from client input.
    """
    task_repo = SqlAlchemyTaskRepository(db)
    note_repo = SqlAlchemyNoteRepository(db)
    
    event_bus = fastapi_request.app.state.event_bus
    
    use_case = UpdateTaskProgressManualUseCase(
        task_repository=task_repo,
        note_repository=note_repo,
        event_bus=event_bus,
    )
    
    task = use_case.execute(
        task_id=task_id,
        completion_percentage=request.completion_percentage,
        user_id=request.user_id,
    )
    
    db.commit()
    
    return _task_to_response(task)
