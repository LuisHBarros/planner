"""ProjectScheduleHistory domain model."""
from dataclasses import dataclass, field

from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.value_objects import (
    ProjectId,
    ProjectScheduleHistoryId,
    UtcDateTime,
)


@dataclass
class ProjectScheduleHistory:
    """Audit record for project schedule changes."""
    id: ProjectScheduleHistoryId
    project_id: ProjectId
    previous_end: UtcDateTime
    new_end: UtcDateTime
    reason: ScheduleChangeReason
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        previous_end: UtcDateTime,
        new_end: UtcDateTime,
        reason: ScheduleChangeReason,
    ) -> "ProjectScheduleHistory":
        """Create a project schedule history record."""
        return cls(
            id=ProjectScheduleHistoryId(),
            project_id=project_id,
            previous_end=previous_end,
            new_end=new_end,
            reason=reason,
        )
