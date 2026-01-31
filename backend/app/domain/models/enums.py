"""Domain enums per BUSINESS_RULES.md Section 2.2."""
from enum import Enum


class MemberLevel(str, Enum):
    """Seniority level within a role."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    SPECIALIST = "specialist"
    LEAD = "lead"


class TaskStatus(str, Enum):
    """Task status per BR-TASK-003."""
    TODO = "todo"
    BLOCKED = "blocked"
    DOING = "doing"
    DONE = "done"
    CANCELLED = "cancelled"


class ProjectStatus(str, Enum):
    """Project status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class InviteStatus(str, Enum):
    """Invite status per BR-INV-004."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class ProgressSource(str, Enum):
    """Source of progress update per BR-LLM."""
    MANUAL = "manual"
    LLM = "llm"


class AbandonmentType(str, Enum):
    """Type of task abandonment per BR-ABANDON-001."""
    VOLUNTARY = "voluntary"
    FIRED_FROM_TASK = "fired_from_task"
    FIRED_FROM_PROJECT = "fired_from_project"
    RESIGNED = "resigned"
    TASK_CANCELLED = "task_cancelled"


class WorkloadStatus(str, Enum):
    """Workload status per BR-WORK-002."""
    IMPOSSIBLE = "impossible"  # ratio > 1.5
    TIGHT = "tight"  # ratio > 1.2
    HEALTHY = "healthy"  # ratio > 0.7
    RELAXED = "relaxed"  # ratio > 0.3
    IDLE = "idle"  # ratio <= 0.3


class ScheduleChangeReason(str, Enum):
    """Reason for schedule change per BR-SCHED."""
    DEPENDENCY_DELAY = "dependency_delay"
    DEPENDENCY_EARLY = "dependency_early"
    MANUAL_OVERRIDE = "manual_override"
    TASK_COMPLETED = "task_completed"
    TASK_CANCELLED = "task_cancelled"


class DependencyType(str, Enum):
    """Task dependency type - MVP only supports finish_to_start."""
    FINISH_TO_START = "finish_to_start"
