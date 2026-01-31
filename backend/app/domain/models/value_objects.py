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
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectId:
    """Project identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class RoleId:
    """Role identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskId:
    """Task identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectMemberId:
    """ProjectMember identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectInviteId:
    """Project invite identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskReportId:
    """Task report identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskAbandonmentId:
    """Task abandonment identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskAssignmentHistoryId:
    """Task assignment history identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskScheduleHistoryId:
    """Task schedule history identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectScheduleHistoryId:
    """Project schedule history identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class NotificationPreferenceId:
    """Notification preference identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class MagicLinkId:
    """Magic link identifier value object."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, "value", value or uuid4())

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
        object.__setattr__(self, "value", value)

    @staticmethod
    def now() -> "UtcDateTime":
        return UtcDateTime(datetime.now(timezone.utc))

    def __str__(self) -> str:
        return self.value.isoformat()

    def __lt__(self, other: "UtcDateTime") -> bool:
        return self.value < other.value

    def __le__(self, other: "UtcDateTime") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "UtcDateTime") -> bool:
        return self.value > other.value

    def __ge__(self, other: "UtcDateTime") -> bool:
        return self.value >= other.value
