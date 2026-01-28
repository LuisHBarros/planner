"""Company repository port."""
from typing import Protocol, Optional
from uuid import UUID
from app.domain.models.company import Company


class CompanyRepository(Protocol):
    """Repository interface for Company entities."""
    
    def save(self, company: Company) -> None:
        """Save a company."""
        ...
    
    def find_by_id(self, company_id: UUID) -> Optional[Company]:
        """Find company by ID."""
        ...
    
    def find_by_slug(self, slug: str) -> Optional[Company]:
        """Find company by slug."""
        ...
