"""Team domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4


class Team:
    """Team entity - collaborative unit."""

    def __init__(
        self,
        id: UUID,
        company_id: UUID,
        name: str,
        description: Optional[str] = None,
        default_language: str = "en",
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.company_id = company_id
        self.name = name
        self.description = description
        self.default_language = default_language
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        company_id: UUID,
        name: str,
        description: Optional[str] = None,
        default_language: str = "en",
    ) -> "Team":
        """Create a new team."""
        return cls(
            id=uuid4(),
            company_id=company_id,
            name=name,
            description=description,
            default_language=default_language,
        )
