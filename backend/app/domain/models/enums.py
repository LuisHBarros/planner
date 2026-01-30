"""Domain enums."""
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum (BR-004)."""
    TODO = "todo"
    DOING = "doing"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"  # Terminal state (v3.0)


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoleLevel(str, Enum):
    """Role level enum."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    SPECIALIST = "specialist"


class ProjectStatus(str, Enum):
    """Project status enum."""
    ACTIVE = "active"
    ARCHIVED = "archived"


class CompanyPlan(str, Enum):
    """Company plan enum."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class DependencyType(str, Enum):
    """Task dependency type enum."""
    BLOCKS = "blocks"
    RELATES_TO = "relates_to"


class NoteType(str, Enum):
    """Note type enum."""
    COMMENT = "comment"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    BLOCKER = "blocker"
    SYSTEM = "system"


class CompletionSource(str, Enum):
    """Task completion percentage source."""
    MANUAL = "manual"
    AI = "ai"


class ScheduleChangeReason(str, Enum):
    """Reason for a schedule change in ScheduleHistory."""

    DEPENDENCY_DELAY = "dependency_delay"
    MANUAL_OVERRIDE = "manual_override"
    SCOPE_CHANGE = "scope_change"
    ESTIMATION_ERROR = "estimation_error"


class TeamMemberRole(str, Enum):
    """Role of a user within a team (Spec 3.0)."""

    MANAGER = "manager"
    BACKEND = "backend"
    MEMBER = "member"


class AbandonmentType(str, Enum):
    """Type of task abandonment (v3.0 BR-ASSIGN)."""

    VOLUNTARY = "voluntary"  # Employee abandons their own task
    FIRED_FROM_TASK = "fired_from_task"  # Manager removes employee from task
    FIRED_FROM_PROJECT = "fired_from_project"  # Manager fires employee (abandons all tasks)
    RESIGNED = "resigned"  # Employee resigns (abandons all tasks)
    TASK_CANCELLED = "task_cancelled"  # Task was cancelled while in progress


class WorkloadStatus(str, Enum):
    """Workload status for an individual (v3.0 BR-WORK)."""

    IMPOSSIBLE = "impossible"  # ratio > 1.5
    TIGHT = "tight"  # ratio > 1.2
    HEALTHY = "healthy"  # ratio > 0.7
    RELAXED = "relaxed"  # ratio > 0.3
    IDLE = "idle"  # ratio <= 0.3


class ProjectMemberRole(str, Enum):
    """Role of a user within a project (v3.0 BR-PROJ)."""

    MANAGER = "manager"
    EMPLOYEE = "employee"


class AssignmentAction(str, Enum):
    """Actions recorded in task assignment history (v3.0)."""

    STARTED = "started"
    ABANDONED = "abandoned"
    RESUMED = "resumed"
    COMPLETED = "completed"
