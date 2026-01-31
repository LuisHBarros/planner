# Planner Multiplayer v3.0 - Implementation Script

**For:** Claude (AI Assistant)  
**Purpose:** Complete rewrite following BUSINESS_RULES.md and architecture_guide.md  
**Database:** SQLite  
**Auth Library:** authlib  

---

## 🎯 CRITICAL INSTRUCTIONS

1. **Follow ONLY what is in BUSINESS_RULES.md** - No features beyond the specification
2. **Follow architecture_guide.md strictly** - Hexagonal Architecture, SOLID, TDD
3. **Delete ALL old code** - This is a complete rewrite
4. **Create tests BEFORE implementation** - TDD approach
5. **Use Value Objects** - TaskId, ProjectId, UserId, etc.
6. **Domain layer is PURE** - No framework imports in domain/

---

## 📁 TARGET PROJECT STRUCTURE

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   │
│   ├── api/                          # PRIMARY ADAPTERS
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── dependencies.py           # FastAPI dependencies (get_db, get_current_user)
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── auth.py               # JWT validation middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py               # UC-001, UC-002
│   │       ├── projects.py           # UC-010, UC-011, UC-012, UC-013
│   │       ├── invites.py            # UC-020, UC-021, UC-022
│   │       ├── tasks.py              # UC-030 to UC-045
│   │       ├── employees.py          # UC-050 to UC-054
│   │       ├── schedule.py           # UC-060 to UC-064
│   │       └── me.py                 # Current user endpoints
│   │
│   ├── application/                  # APPLICATION LAYER
│   │   ├── __init__.py
│   │   ├── ports/                    # INTERFACES (Output Ports)
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── project_member_repository.py
│   │   │   ├── role_repository.py
│   │   │   ├── project_invite_repository.py
│   │   │   ├── task_repository.py
│   │   │   ├── task_dependency_repository.py
│   │   │   ├── task_report_repository.py
│   │   │   ├── task_abandonment_repository.py
│   │   │   ├── task_assignment_history_repository.py
│   │   │   ├── schedule_history_repository.py
│   │   │   ├── notification_preference_repository.py
│   │   │   ├── magic_link_repository.py
│   │   │   ├── event_bus.py
│   │   │   ├── email_service.py
│   │   │   ├── llm_service.py
│   │   │   └── unit_of_work.py
│   │   │
│   │   ├── services/                 # APPLICATION SERVICES
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── schedule_service.py
│   │   │   ├── notification_service.py
│   │   │   └── llm_application_service.py
│   │   │
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   └── domain_events.py
│   │   │
│   │   ├── dtos/
│   │   │   ├── __init__.py
│   │   │   ├── auth_dtos.py
│   │   │   ├── project_dtos.py
│   │   │   ├── task_dtos.py
│   │   │   └── schedule_dtos.py
│   │   │
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       │
│   │       │ # Authentication (UC-001, UC-002)
│   │       ├── register_user.py
│   │       ├── login_user.py
│   │       ├── verify_magic_link.py
│   │       │
│   │       │ # Project Management (UC-010 to UC-013)
│   │       ├── create_project.py
│   │       ├── configure_project_llm.py
│   │       ├── create_role.py
│   │       ├── get_project.py
│   │       │
│   │       │ # Invitations (UC-020 to UC-022)
│   │       ├── create_project_invite.py
│   │       ├── view_invite.py
│   │       ├── accept_invite.py
│   │       │
│   │       │ # Task Management (UC-030 to UC-035)
│   │       ├── create_task.py
│   │       ├── set_task_difficulty_manual.py
│   │       ├── calculate_task_difficulty_llm.py
│   │       ├── add_task_dependency.py
│   │       ├── remove_task_dependency.py
│   │       ├── cancel_task.py
│   │       │
│   │       │ # Task Execution (UC-040 to UC-045)
│   │       ├── select_task.py
│   │       ├── abandon_task.py
│   │       ├── add_task_report.py
│   │       ├── calculate_progress_llm.py
│   │       ├── update_progress_manual.py
│   │       ├── complete_task.py
│   │       │
│   │       │ # Employee Management (UC-050 to UC-054)
│   │       ├── remove_from_task.py
│   │       ├── fire_employee.py
│   │       ├── resign_from_project.py
│   │       ├── list_team.py
│   │       ├── get_employee_workload.py
│   │       │
│   │       │ # Schedule (UC-060 to UC-064, UC-070)
│   │       ├── detect_delay.py
│   │       ├── propagate_schedule.py
│   │       ├── update_project_date.py
│   │       ├── view_schedule_history.py
│   │       ├── manual_date_override.py
│   │       ├── change_employee_role.py
│   │       │
│   │       │ # Notifications (UC-080 to UC-084)
│   │       ├── send_manager_daily_report.py
│   │       ├── send_workload_alert.py
│   │       ├── send_new_task_toast.py
│   │       ├── send_employee_daily_email.py
│   │       └── send_project_deadline_warning.py
│   │
│   ├── domain/                       # DOMAIN LAYER (PURE)
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── value_objects.py      # UserId, ProjectId, TaskId, etc.
│   │   │   ├── enums.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── project_member.py
│   │   │   ├── role.py
│   │   │   ├── project_invite.py
│   │   │   ├── task.py
│   │   │   ├── task_dependency.py
│   │   │   ├── task_report.py
│   │   │   ├── task_abandonment.py
│   │   │   ├── task_assignment_history.py
│   │   │   ├── task_schedule_history.py
│   │   │   ├── project_schedule_history.py
│   │   │   ├── notification_preference.py
│   │   │   └── magic_link.py
│   │   │
│   │   └── services/                 # DOMAIN SERVICES (pure logic, no I/O)
│   │       ├── __init__.py
│   │       ├── schedule_calculator.py
│   │       ├── workload_calculator.py
│   │       ├── ranking_service.py
│   │       └── dependency_validator.py
│   │
│   └── infrastructure/               # SECONDARY ADAPTERS
│       ├── __init__.py
│       ├── database.py
│       │
│       ├── persistence/
│       │   ├── __init__.py
│       │   ├── models.py             # SQLAlchemy ORM models
│       │   ├── repositories.py       # Repository implementations
│       │   └── uow.py                # Unit of Work implementation
│       │
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt_service.py        # JWT creation/validation
│       │   └── magic_link_service.py # Magic link generation
│       │
│       ├── email/
│       │   ├── __init__.py
│       │   └── email_service.py      # Email sending (mock for MVP)
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   └── llm_service.py        # LLM API client
│       │
│       ├── notifications/
│       │   ├── __init__.py
│       │   ├── notification_service.py
│       │   └── handlers/
│       │       ├── __init__.py
│       │       ├── workload_handler.py
│       │       └── task_handler.py
│       │
│       └── events/
│           ├── __init__.py
│           ├── in_memory_event_bus.py
│           └── handlers/
│               ├── __init__.py
│               ├── schedule_handler.py
│               └── notification_handler.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py                   # Pytest fixtures
    │
    ├── unit/
    │   ├── __init__.py
    │   ├── domain/
    │   │   ├── __init__.py
    │   │   ├── test_user.py
    │   │   ├── test_project.py
    │   │   ├── test_project_member.py
    │   │   ├── test_role.py
    │   │   ├── test_project_invite.py
    │   │   ├── test_task.py
    │   │   ├── test_task_status_transitions.py
    │   │   ├── test_task_dependency.py
    │   │   ├── test_task_abandonment.py
    │   │   ├── test_workload_calculator.py
    │   │   ├── test_schedule_calculator.py
    │   │   └── test_dependency_validator.py
    │   │
    │   └── use_cases/
    │       ├── __init__.py
    │       ├── test_register_user.py
    │       ├── test_create_project.py
    │       ├── test_create_invite.py
    │       ├── test_accept_invite.py
    │       ├── test_create_task.py
    │       ├── test_select_task.py
    │       ├── test_abandon_task.py
    │       ├── test_complete_task.py
    │       ├── test_cancel_task.py
    │       ├── test_fire_employee.py
    │       ├── test_schedule_propagation.py
    │       └── test_workload_blocking.py
    │
    ├── integration/
    │   ├── __init__.py
    │   ├── test_auth_flow.py
    │   ├── test_project_invite_flow.py
    │   ├── test_task_lifecycle.py
    │   └── test_schedule_propagation.py
    │
    └── e2e/
        ├── __init__.py
        ├── test_complete_workflow.py
        └── test_api_endpoints.py
```

---

## 📝 IMPLEMENTATION PHASES

Execute each phase in order. Do not proceed to next phase until current phase passes all tests.

---

### PHASE 1: Domain Models & Value Objects

**Goal:** Create all domain entities following BUSINESS_RULES.md Section 2.

#### Step 1.1: Value Objects
Create `domain/models/value_objects.py`:

```python
"""Value Objects for type-safe identifiers.

Per architecture_guide.md v2.1: Use Value Objects instead of raw primitives.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserId:
    """User identifier value object."""
    value: UUID
    
    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectId:
    """Project identifier value object."""
    value: UUID
    
    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class RoleId:
    """Role identifier value object."""
    value: UUID
    
    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskId:
    """Task identifier value object."""
    value: UUID
    
    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectMemberId:
    """ProjectMember identifier value object."""
    value: UUID
    
    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class InviteToken:
    """Invite token value object."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UtcDateTime:
    """Always-UTC datetime value object.
    
    Prevents timezone confusion per Spec 2.1.
    """
    value: datetime
    
    def __init__(self, value: Optional[datetime] = None):
        if value is None:
            value = datetime.now(timezone.utc)
        elif value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        object.__setattr__(self, 'value', value)
    
    @staticmethod
    def now() -> 'UtcDateTime':
        return UtcDateTime(datetime.now(timezone.utc))
    
    def __str__(self) -> str:
        return self.value.isoformat()
    
    def __lt__(self, other: 'UtcDateTime') -> bool:
        return self.value < other.value
    
    def __le__(self, other: 'UtcDateTime') -> bool:
        return self.value <= other.value
    
    def __gt__(self, other: 'UtcDateTime') -> bool:
        return self.value > other.value
    
    def __ge__(self, other: 'UtcDateTime') -> bool:
        return self.value >= other.value
```

#### Step 1.2: Enums
Create `domain/models/enums.py`:

```python
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
    IMPOSSIBLE = "impossible"   # ratio > 1.5
    TIGHT = "tight"             # ratio > 1.2
    HEALTHY = "healthy"         # ratio > 0.7
    RELAXED = "relaxed"         # ratio > 0.3
    IDLE = "idle"               # ratio <= 0.3


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
```

#### Step 1.3: Domain Entities
Create each entity file following BUSINESS_RULES.md Section 2.1.

**User (`domain/models/user.py`):**
```python
"""User domain model per BUSINESS_RULES.md."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.value_objects import UserId, UtcDateTime


@dataclass
class User:
    """User entity - registered via magic link."""
    id: UserId
    email: str
    name: str
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)
    
    @classmethod
    def create(cls, email: str, name: str) -> 'User':
        """Create a new user (BR-AUTH-003: email unique, case-insensitive)."""
        return cls(
            id=UserId(),
            email=email.lower().strip(),
            name=name.strip(),
        )
```

**Project (`domain/models/project.py`):**
```python
"""Project domain model per BUSINESS_RULES.md."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.value_objects import ProjectId, UserId, UtcDateTime
from app.domain.models.enums import ProjectStatus


@dataclass
class Project:
    """Project entity - created by user who becomes Manager.
    
    BR-PROJ-001: Creator automatically becomes Manager.
    BR-PROJ-002: Manager CANNOT execute tasks.
    BR-PROJ-003: expected_end_date auto-recalculated.
    """
    id: ProjectId
    name: str
    description: Optional[str]
    created_by: UserId  # The Manager
    expected_end_date: Optional[UtcDateTime]
    status: ProjectStatus
    
    # LLM Configuration (BR-LLM)
    llm_enabled: bool = False
    llm_provider: Optional[str] = None
    llm_api_key_encrypted: Optional[str] = None  # BR-LLM-002: encrypted
    
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)
    
    @classmethod
    def create(
        cls,
        name: str,
        created_by: UserId,
        expected_end_date: Optional[UtcDateTime] = None,
        description: Optional[str] = None,
    ) -> 'Project':
        """Create a new project."""
        return cls(
            id=ProjectId(),
            name=name.strip(),
            description=description,
            created_by=created_by,
            expected_end_date=expected_end_date,
            status=ProjectStatus.ACTIVE,
        )
    
    def is_manager(self, user_id: UserId) -> bool:
        """Check if user is the manager (BR-PROJ-002)."""
        return self.created_by == user_id
    
    def enable_llm(self, provider: str, api_key_encrypted: str) -> None:
        """Enable LLM integration (BR-LLM-002)."""
        self.llm_enabled = True
        self.llm_provider = provider
        self.llm_api_key_encrypted = api_key_encrypted
    
    def disable_llm(self) -> None:
        """Disable LLM integration."""
        self.llm_enabled = False
        self.llm_provider = None
        self.llm_api_key_encrypted = None
```

**Continue creating:**
- `domain/models/project_member.py` (see BUSINESS_RULES.md ProjectMember)
- `domain/models/role.py` (BR-ROLE)
- `domain/models/project_invite.py` (BR-INV)
- `domain/models/task.py` (BR-TASK, including status transitions)
- `domain/models/task_dependency.py` (BR-DEP)
- `domain/models/task_report.py` (NEW entity)
- `domain/models/task_abandonment.py` (BR-ABANDON)
- `domain/models/task_assignment_history.py` (BR-ASSIGN-005)
- `domain/models/task_schedule_history.py` (BR-SCHED-007)
- `domain/models/project_schedule_history.py` (BR-SCHED-006)
- `domain/models/notification_preference.py` (BR-NOTIF-006)
- `domain/models/magic_link.py` (BR-AUTH)

**CRITICAL for Task entity - Status Transitions (BR-TASK-003):**
```python
# In task.py
VALID_TRANSITIONS = {
    TaskStatus.TODO: [TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.BLOCKED: [TaskStatus.TODO, TaskStatus.CANCELLED],
    TaskStatus.DOING: [TaskStatus.DONE, TaskStatus.TODO, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.DONE: [],  # Terminal
    TaskStatus.CANCELLED: [],  # Terminal
}

def can_transition_to(self, new_status: TaskStatus) -> bool:
    """Check if transition is valid per BR-TASK-003."""
    return new_status in VALID_TRANSITIONS.get(self.status, [])
```

#### Step 1.4: Domain Services (Pure Logic)
Create domain services with NO I/O, NO framework dependencies:

**`domain/services/workload_calculator.py`:**
```python
"""Workload calculator per BR-WORK."""
from typing import List
from app.domain.models.task import Task
from app.domain.models.enums import MemberLevel, WorkloadStatus, TaskStatus

# BR-WORK-001: Level multipliers
LEVEL_MULTIPLIERS = {
    MemberLevel.JUNIOR: 0.6,
    MemberLevel.MID: 1.0,
    MemberLevel.SENIOR: 1.3,
    MemberLevel.SPECIALIST: 1.2,
    MemberLevel.LEAD: 1.1,
}


def calculate_workload_score(tasks: List[Task]) -> int:
    """Calculate total workload from DOING tasks."""
    return sum(
        task.difficulty or 0 
        for task in tasks 
        if task.status == TaskStatus.DOING
    )


def calculate_capacity(base_capacity: int, level: MemberLevel) -> float:
    """Calculate effective capacity based on level."""
    return base_capacity * LEVEL_MULTIPLIERS.get(level, 1.0)


def calculate_workload_status(
    workload_score: int, 
    capacity: float
) -> WorkloadStatus:
    """Determine workload status per BR-WORK-002."""
    if capacity == 0:
        return WorkloadStatus.IDLE
    
    ratio = workload_score / capacity
    
    if ratio > 1.5:
        return WorkloadStatus.IMPOSSIBLE
    elif ratio > 1.2:
        return WorkloadStatus.TIGHT
    elif ratio > 0.7:
        return WorkloadStatus.HEALTHY
    elif ratio > 0.3:
        return WorkloadStatus.RELAXED
    else:
        return WorkloadStatus.IDLE


def would_be_impossible(
    current_tasks: List[Task],
    new_task: Task,
    base_capacity: int,
    level: MemberLevel,
) -> bool:
    """Check if adding new_task would result in IMPOSSIBLE status (BR-ASSIGN-003)."""
    current_score = calculate_workload_score(current_tasks)
    new_score = current_score + (new_task.difficulty or 0)
    capacity = calculate_capacity(base_capacity, level)
    status = calculate_workload_status(new_score, capacity)
    return status == WorkloadStatus.IMPOSSIBLE
```

**`domain/services/schedule_calculator.py`:**
```python
"""Schedule calculator per BR-SCHED."""
from datetime import timedelta
from typing import List, Dict, Optional
from app.domain.models.task import Task
from app.domain.models.value_objects import TaskId, UtcDateTime
from app.domain.models.enums import TaskStatus


def detect_delay(task: Task) -> bool:
    """Detect if task is delayed (BR-SCHED-001)."""
    if task.actual_end_date is None or task.expected_end_date is None:
        return False
    return task.actual_end_date > task.expected_end_date


def calculate_delay_delta(task: Task) -> Optional[timedelta]:
    """Calculate delay amount."""
    if task.actual_end_date is None or task.expected_end_date is None:
        return None
    return task.actual_end_date.value - task.expected_end_date.value


def calculate_max_delay_from_parents(
    parent_tasks: List[Task],
) -> Optional[UtcDateTime]:
    """
    Calculate the maximum end date from parent tasks (BR-SCHED-003).
    
    Uses actual_end_date if task is DONE, otherwise expected_end_date.
    """
    if not parent_tasks:
        return None
    
    max_date = None
    for parent in parent_tasks:
        if parent.status == TaskStatus.DONE and parent.actual_end_date:
            parent_end = parent.actual_end_date
        elif parent.expected_end_date:
            parent_end = parent.expected_end_date
        else:
            continue
        
        if max_date is None or parent_end > max_date:
            max_date = parent_end
    
    return max_date


def calculate_new_dates(
    task: Task,
    delay_delta: timedelta,
) -> tuple[Optional[UtcDateTime], Optional[UtcDateTime]]:
    """
    Calculate new expected dates respecting task lifecycle (BR-SCHED-005).
    
    - If DONE: skip (immutable)
    - If started (actual_start_date set): only shift expected_end
    - If not started: shift both
    """
    if task.status == TaskStatus.DONE:
        return task.expected_start_date, task.expected_end_date
    
    new_start = task.expected_start_date
    new_end = task.expected_end_date
    
    if task.actual_start_date is not None:
        # Task started - only shift end (BR-SCHED-005)
        if task.expected_end_date:
            new_end = UtcDateTime(task.expected_end_date.value + delay_delta)
    else:
        # Task not started - shift both
        if task.expected_start_date:
            new_start = UtcDateTime(task.expected_start_date.value + delay_delta)
        if task.expected_end_date:
            new_end = UtcDateTime(task.expected_end_date.value + delay_delta)
    
    return new_start, new_end
```

**`domain/services/dependency_validator.py`:**
```python
"""Dependency validation per BR-DEP."""
from typing import Dict, Set, List
from app.domain.models.value_objects import TaskId


def detect_cycle(
    task_id: TaskId,
    depends_on_id: TaskId,
    existing_dependencies: Dict[TaskId, List[TaskId]],  # task_id -> [depends_on_ids]
) -> bool:
    """
    Detect if adding dependency would create a cycle (BR-DEP-002).
    
    Uses DFS to check if depends_on_id can reach task_id.
    """
    if task_id == depends_on_id:
        return True  # Self-dependency
    
    visited: Set[TaskId] = set()
    stack: List[TaskId] = [depends_on_id]
    
    while stack:
        current = stack.pop()
        if current == task_id:
            return True  # Found cycle
        
        if current in visited:
            continue
        visited.add(current)
        
        # Add dependencies of current task
        for dep_id in existing_dependencies.get(current, []):
            stack.append(dep_id)
    
    return False
```

---

### PHASE 2: Application Ports (Interfaces)

**Goal:** Define all repository interfaces per architecture_guide.md.

Create each port file in `application/ports/`. Example:

**`application/ports/project_repository.py`:**
```python
"""Project repository port."""
from typing import Protocol, Optional, List
from app.domain.models.project import Project
from app.domain.models.value_objects import ProjectId, UserId


class ProjectRepository(Protocol):
    """Repository interface for Project entities."""
    
    def save(self, project: Project) -> None:
        """Persist a project."""
        ...
    
    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """Find project by ID."""
        ...
    
    def find_by_created_by(self, user_id: UserId) -> List[Project]:
        """Find all projects created by a user."""
        ...
    
    def delete(self, project_id: ProjectId) -> None:
        """Delete a project."""
        ...
```

Create similar ports for all entities listed in the structure.

---

### PHASE 3: Use Cases (TDD)

**Goal:** Implement all use cases per BUSINESS_RULES.md Appendix A.

**CRITICAL: Write test FIRST, then implementation.**

#### Example: UC-010 Create Project

**Test first (`tests/unit/use_cases/test_create_project.py`):**
```python
"""Tests for CreateProjectUseCase (UC-010)."""
import pytest
from unittest.mock import Mock, MagicMock
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.dtos.project_dtos import CreateProjectInput
from app.domain.models.user import User
from app.domain.models.value_objects import UserId


class TestCreateProjectUseCase:
    """Test suite for UC-010: Create Project."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = CreateProjectUseCase(
            uow=self.uow,
            event_bus=self.event_bus,
        )
        
        # Create test user
        self.user = User.create(email="test@example.com", name="Test User")
        self.uow.users.find_by_id.return_value = self.user
    
    def test_creates_project_successfully(self):
        """User can create a project."""
        input_dto = CreateProjectInput(
            name="My Project",
            description="Test project",
            created_by=self.user.id,
        )
        
        result = self.use_case.execute(input_dto)
        
        assert result.name == "My Project"
        self.uow.projects.save.assert_called_once()
        self.uow.commit.assert_called_once()
    
    def test_creator_becomes_manager(self):
        """BR-PROJ-001: Creator is automatically Manager."""
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=self.user.id,
        )
        
        result = self.use_case.execute(input_dto)
        
        # Verify ProjectMember was created for manager
        self.uow.project_members.save.assert_called_once()
        saved_member = self.uow.project_members.save.call_args[0][0]
        assert saved_member.is_manager == True
    
    def test_emits_project_created_event(self):
        """Event is emitted on creation."""
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=self.user.id,
        )
        
        self.use_case.execute(input_dto)
        
        self.event_bus.emit.assert_called_once()
    
    def test_fails_if_user_not_found(self):
        """Raises error if user doesn't exist."""
        self.uow.users.find_by_id.return_value = None
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=UserId(),
        )
        
        with pytest.raises(Exception) as exc_info:
            self.use_case.execute(input_dto)
        
        assert "user" in str(exc_info.value).lower()
```

**Then implementation (`application/use_cases/create_project.py`):**
```python
"""UC-010: Create Project use case."""
from app.domain.models.project import Project
from app.domain.models.project_member import ProjectMember
from app.domain.models.enums import MemberLevel
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.event_bus import EventBus
from app.application.dtos.project_dtos import CreateProjectInput, ProjectOutput
from app.application.events.domain_events import ProjectCreated
from app.domain.exceptions import BusinessRuleViolation


class CreateProjectUseCase:
    """Use case for creating a project (UC-010, BR-PROJ-001)."""
    
    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus
    
    def execute(self, input_dto: CreateProjectInput) -> ProjectOutput:
        """
        Create a new project.
        
        Flow:
        1. Validate user exists
        2. Create project with user as created_by
        3. Create ProjectMember with is_manager=True (BR-PROJ-001)
        4. Emit ProjectCreated event
        5. Return project details
        """
        with self.uow:
            # Validate user exists
            user = self.uow.users.find_by_id(input_dto.created_by)
            if user is None:
                raise BusinessRuleViolation(
                    f"User with id {input_dto.created_by} not found",
                    code="user_not_found"
                )
            
            # Create project
            project = Project.create(
                name=input_dto.name,
                created_by=input_dto.created_by,
                expected_end_date=input_dto.expected_end_date,
                description=input_dto.description,
            )
            self.uow.projects.save(project)
            
            # BR-PROJ-001: Creator becomes Manager
            manager_member = ProjectMember.create_manager(
                project_id=project.id,
                user_id=input_dto.created_by,
            )
            self.uow.project_members.save(manager_member)
            
            # Commit transaction
            self.uow.commit()
            
            # Emit event
            self.event_bus.emit(ProjectCreated(
                project_id=project.id,
                created_by=input_dto.created_by,
                name=project.name,
            ))
            
            return ProjectOutput.from_domain(project)
```

---

### PHASE 4: Infrastructure Implementation

**Goal:** Implement all adapters (repositories, services).

#### Step 4.1: Database Models
Create SQLAlchemy models in `infrastructure/persistence/models.py`.

#### Step 4.2: Repositories
Implement all repository interfaces in `infrastructure/persistence/repositories.py`.

#### Step 4.3: Unit of Work
Implement `infrastructure/persistence/uow.py`.

#### Step 4.4: Auth Infrastructure
- `infrastructure/auth/jwt_service.py` - Use authlib
- `infrastructure/auth/magic_link_service.py`

#### Step 4.5: Email Service
Create mock email service in `infrastructure/email/email_service.py`.

#### Step 4.6: LLM Service
Create `infrastructure/llm/llm_service.py` with actual API calls.

---

### PHASE 5: API Routes

**Goal:** Create all FastAPI routes following BUSINESS_RULES.md use cases.

#### Step 5.1: Auth Middleware
Create JWT validation in `api/middleware/auth.py`.

#### Step 5.2: Dependencies
Create FastAPI dependencies in `api/dependencies.py`:
- `get_db` - Database session
- `get_current_user` - Extract user from JWT
- `get_unit_of_work` - UoW instance

#### Step 5.3: Routes
Create all route files following the use case structure.

---

### PHASE 6: Notification System

**Goal:** Implement notification handlers per BR-NOTIF.

#### Step 6.1: Event Handlers
Create handlers that listen to domain events and trigger notifications.

#### Step 6.2: Daily Report Job
Create scheduled job for daily reports (can be simple timer for MVP).

---

### PHASE 7: Integration & E2E Tests

**Goal:** Verify complete flows work correctly.

---

## ✅ VALIDATION CHECKLIST

Before considering implementation complete, verify:

### Domain Layer
- [ ] All entities have factory methods (`.create()`)
- [ ] No framework imports in `domain/`
- [ ] Value Objects used for all IDs
- [ ] Business rules implemented in domain methods
- [ ] Domain services are pure (no I/O)

### Application Layer
- [ ] All ports are Protocol classes
- [ ] Use cases only orchestrate (no business logic)
- [ ] DTOs used for input/output
- [ ] Events emitted for significant changes

### Infrastructure Layer
- [ ] Repositories implement ports
- [ ] Unit of Work coordinates transactions
- [ ] Auth uses authlib
- [ ] Email service exists (mock OK)
- [ ] LLM service exists with fallback

### API Layer
- [ ] JWT middleware validates tokens
- [ ] All endpoints require authentication (except auth routes)
- [ ] Manager-only endpoints check `project.is_manager()`
- [ ] Response models match DTOs

### Tests
- [ ] Unit tests for all domain entities
- [ ] Unit tests for all use cases
- [ ] Integration tests for main flows
- [ ] E2E tests for API endpoints

### Business Rules
- [ ] BR-AUTH-001 to BR-AUTH-003 (Magic link auth)
- [ ] BR-PROJ-001 to BR-PROJ-004 (Project rules)
- [ ] BR-INV-001 to BR-INV-006 (Invitation rules)
- [ ] BR-ROLE-001 to BR-ROLE-007 (Role rules)
- [ ] BR-TASK-001 to BR-TASK-007 (Task rules)
- [ ] BR-ASSIGN-001 to BR-ASSIGN-006 (Assignment rules)
- [ ] BR-DEP-001 to BR-DEP-007 (Dependency rules)
- [ ] BR-ABANDON-001 to BR-ABANDON-008 (Abandonment rules)
- [ ] BR-EMP-001 to BR-EMP-003 (Employee rules)
- [ ] BR-SCHED-001 to BR-SCHED-007 (Schedule rules)
- [ ] BR-WORK-001 to BR-WORK-004 (Workload rules)
- [ ] BR-LLM-001 to BR-LLM-008 (LLM rules)
- [ ] BR-VIS-001 to BR-VIS-004 (Visibility rules)
- [ ] BR-MANUAL-001 to BR-MANUAL-003 (Manual override rules)
- [ ] BR-NOTIF-001 to BR-NOTIF-006 (Notification rules)

---

## 🚫 DO NOT

1. **DO NOT** add features not in BUSINESS_RULES.md
2. **DO NOT** skip writing tests
3. **DO NOT** put business logic in use cases
4. **DO NOT** import frameworks in domain layer
5. **DO NOT** use raw UUIDs instead of Value Objects
6. **DO NOT** forget to emit events
7. **DO NOT** forget to create audit records (ScheduleHistory, AssignmentHistory)
8. **DO NOT** allow managers to claim tasks
9. **DO NOT** allow task selection without difficulty set
10. **DO NOT** allow workload to become IMPOSSIBLE on task selection

---

## 📎 REFERENCE FILES

Always keep these files open for reference:
1. `BUSINESS_RULES.md` - The source of truth for all rules
2. `architecture_guide.md` - Architecture patterns to follow
3. This script - Implementation order and structure

---

*End of Implementation Script*