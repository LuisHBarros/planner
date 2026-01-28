"""SQLAlchemy ORM models for database persistence."""
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base
from app.domain.models.enums import (
    TaskStatus,
    TaskPriority,
    RoleLevel,
    ProjectStatus,
    CompanyPlan,
    DependencyType,
    NoteType,
    CompletionSource,
    ScheduleChangeReason,
    TeamMemberRole,
)


class CompanyModel(Base):
    """SQLAlchemy model for Company."""
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    plan = Column(SQLEnum(CompanyPlan), nullable=False, default=CompanyPlan.FREE)
    billing_email = Column(String(255), nullable=False)
    ai_enabled = Column(Boolean, default=False)
    ai_provider = Column(String(50), nullable=True)
    ai_api_key = Column(Text, nullable=True)  # Encrypted in production
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    teams = relationship("TeamModel", back_populates="company")


class TeamModel(Base):
    """SQLAlchemy model for Team."""
    __tablename__ = "teams"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("CompanyModel", back_populates="teams")
    roles = relationship("RoleModel", back_populates="team")
    projects = relationship("ProjectModel", back_populates="team")


class UserModel(Base):
    """SQLAlchemy model for User."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    preferred_language = Column(String(10), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoleModel(Base):
    """SQLAlchemy model for Role."""
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(SQLEnum(RoleLevel), nullable=False)
    base_capacity = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("TeamModel", back_populates="roles")


class ProjectModel(Base):
    """SQLAlchemy model for Project."""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("TeamModel", back_populates="projects")
    tasks = relationship("TaskModel", back_populates="project")


class TaskModel(Base):
    """SQLAlchemy model for Task."""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    rank_index = Column(Float, nullable=False, default=1.0)
    role_responsible_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    user_responsible_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    completion_percentage = Column(Integer, nullable=True)
    completion_source = Column(SQLEnum(CompletionSource), nullable=True)
    due_date = Column(DateTime, nullable=True)
    expected_start_date = Column(DateTime, nullable=True)
    expected_end_date = Column(DateTime, nullable=True)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    is_delayed = Column(Boolean, default=False)
    blocked_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    project = relationship("ProjectModel", back_populates="tasks")
    notes = relationship("NoteModel", back_populates="task", order_by="NoteModel.created_at")
    dependencies = relationship(
        "TaskDependencyModel",
        foreign_keys="TaskDependencyModel.task_id",
        back_populates="task"
    )
    dependents = relationship(
        "TaskDependencyModel",
        foreign_keys="TaskDependencyModel.depends_on_task_id",
        back_populates="depends_on_task"
    )


class ScheduleHistoryModel(Base):
    """SQLAlchemy model for ScheduleHistory."""

    __tablename__ = "schedule_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    old_expected_start = Column(DateTime, nullable=True)
    old_expected_end = Column(DateTime, nullable=True)
    new_expected_start = Column(DateTime, nullable=True)
    new_expected_end = Column(DateTime, nullable=True)
    reason = Column(SQLEnum(ScheduleChangeReason), nullable=False)
    caused_by_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True)
    changed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class TaskDependencyModel(Base):
    """SQLAlchemy model for TaskDependency."""
    __tablename__ = "task_dependencies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    depends_on_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    dependency_type = Column(SQLEnum(DependencyType), default=DependencyType.BLOCKS)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("TaskModel", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("TaskModel", foreign_keys=[depends_on_task_id], back_populates="dependents")


class NoteModel(Base):
    """SQLAlchemy model for Note."""
    __tablename__ = "notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(SQLEnum(NoteType), default=NoteType.COMMENT)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    task = relationship("TaskModel", back_populates="notes")


class EmailPreferencesModel(Base):
    """SQLAlchemy model for EmailPreferences."""
    __tablename__ = "email_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    task_created = Column(Boolean, default=True)
    task_assigned = Column(Boolean, default=True)
    due_date_reminder = Column(Boolean, default=True)
    task_completed = Column(Boolean, default=False)
    task_blocked = Column(Boolean, default=True)
    task_unblocked = Column(Boolean, default=True)
    digest_mode = Column(String(20), default="daily")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamMemberModel(Base):
    """SQLAlchemy model for TeamMember."""

    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    role = Column(SQLEnum(TeamMemberRole), nullable=False, default=TeamMemberRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.utcnow)


class TeamInviteModel(Base):
    """SQLAlchemy model for TeamInvite."""

    __tablename__ = "team_invites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    role = Column(SQLEnum(TeamMemberRole), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
