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
    ) -> "Project":
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
