"""Company domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import CompanyPlan


class Company:
    """Company entity - top-level billing entity."""

    def __init__(
        self,
        id: UUID,
        name: str,
        slug: str,
        plan: CompanyPlan,
        billing_email: str,
        ai_enabled: bool = False,
        ai_provider: Optional[str] = None,
        ai_api_key: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.slug = slug
        self.plan = plan
        self.billing_email = billing_email
        self.ai_enabled = ai_enabled
        self.ai_provider = ai_provider
        self.ai_api_key = ai_api_key
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        name: str,
        billing_email: str,
        plan: CompanyPlan = CompanyPlan.FREE,
    ) -> "Company":
        """Create a new company."""
        slug = cls._generate_slug(name)
        return cls(
            id=uuid4(),
            name=name,
            slug=slug,
            plan=plan,
            billing_email=billing_email,
            ai_enabled=False,
            ai_provider=None,
            ai_api_key=None,
        )

    @staticmethod
    def _generate_slug(name: str) -> str:
        """Generate URL-friendly slug from name."""
        import re

        slug = re.sub(r"[^\w\s-]", "", name.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def enable_ai(self, provider: str, api_key: str):
        """Enable AI features for company."""
        if self.plan == CompanyPlan.FREE:
            raise ValueError("AI features require pro or enterprise plan")
        self.ai_enabled = True
        self.ai_provider = provider
        self.ai_api_key = api_key
        self.updated_at = datetime.now(UTC)
