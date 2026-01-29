"""Value Objects for type-safe domain modeling."""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from typing import Optional


@dataclass(frozen=True)
class TaskId:
    """Task identifier - type-safe wrapper around UUID."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, TaskId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectId:
    """Project identifier."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, ProjectId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class UserId:
    """User identifier."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, UserId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TeamId:
    """Team identifier."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, TeamId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class RoleId:
    """Role identifier."""
    value: UUID

    def __init__(self, value: Optional[UUID] = None):
        object.__setattr__(self, 'value', value or uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, RoleId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class UtcDateTime:
    """DateTime always in UTC - prevents timezone confusion."""
    value: datetime

    def __init__(self, value: Optional[datetime] = None):
        if value is None:
            value = datetime.now(timezone.utc)
        elif value.tzinfo is None:
            raise ValueError("DateTime must have timezone info")
        elif value.tzinfo != timezone.utc:
            value = value.astimezone(timezone.utc)

        object.__setattr__(self, 'value', value)

    @staticmethod
    def now() -> "UtcDateTime":
        """Get current UTC time."""
        return UtcDateTime(datetime.now(timezone.utc))

    def __str__(self) -> str:
        return self.value.isoformat()

    def __repr__(self) -> str:
        return f"UtcDateTime({self.value.isoformat()})"

    def __eq__(self, other) -> bool:
        if isinstance(other, UtcDateTime):
            return self.value == other.value
        return False

    def __lt__(self, other: "UtcDateTime") -> bool:
        if not isinstance(other, UtcDateTime):
            raise TypeError(f"'<' not supported between 'UtcDateTime' and '{type(other)}'")
        return self.value < other.value

    def __le__(self, other: "UtcDateTime") -> bool:
        if not isinstance(other, UtcDateTime):
            raise TypeError(f"'<=' not supported between 'UtcDateTime' and '{type(other)}'")
        return self.value <= other.value

    def __gt__(self, other: "UtcDateTime") -> bool:
        if not isinstance(other, UtcDateTime):
            raise TypeError(f"'>' not supported between 'UtcDateTime' and '{type(other)}'")
        return self.value > other.value

    def __ge__(self, other: "UtcDateTime") -> bool:
        if not isinstance(other, UtcDateTime):
            raise TypeError(f"'>=' not supported between 'UtcDateTime' and '{type(other)}'")
        return self.value >= other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __add__(self, delta: timedelta) -> "UtcDateTime":
        """Add timedelta to this datetime."""
        return UtcDateTime(self.value + delta)

    def __sub__(self, other: "UtcDateTime") -> timedelta:
        """Subtract another UtcDateTime to get timedelta."""
        if not isinstance(other, UtcDateTime):
            raise TypeError(f"unsupported operand type(s) for -: 'UtcDateTime' and '{type(other)}'")
        return self.value - other.value
