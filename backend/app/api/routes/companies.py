"""Company endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAlchemyCompanyRepository,
)
from app.domain.models.company import Company
from app.domain.models.enums import CompanyPlan

router = APIRouter()


# Request/Response DTOs
class CreateCompanyRequest(BaseModel):
    """Request model for creating a company."""
    name: str
    billing_email: EmailStr
    plan: CompanyPlan = CompanyPlan.FREE


class CompanyResponse(BaseModel):
    """Response model for a company."""
    id: str
    name: str
    slug: str
    plan: CompanyPlan
    billing_email: str
    ai_enabled: bool
    ai_provider: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Response model for list of companies."""
    companies: List[CompanyResponse]


def _company_to_response(company: Company) -> CompanyResponse:
    """Convert domain company to response model."""
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        slug=company.slug,
        plan=company.plan,
        billing_email=company.billing_email,
        ai_enabled=company.ai_enabled,
        ai_provider=company.ai_provider,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.get("/", response_model=CompanyListResponse)
async def list_companies(db: Session = Depends(get_db)):
    """List all companies."""
    repo = SqlAlchemyCompanyRepository(db)
    # For MVP, we'll get all companies (in production, this would be paginated)
    companies = repo.find_all()
    return CompanyListResponse(
        companies=[_company_to_response(c) for c in companies]
    )


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    request: CreateCompanyRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new company (UC-021).
    
    This creates the top-level billing entity that owns teams.
    """
    repo = SqlAlchemyCompanyRepository(db)
    
    # Create company using domain factory
    company = Company.create(
        name=request.name,
        billing_email=request.billing_email,
        plan=request.plan,
    )
    
    # Save
    repo.save(company)
    
    return _company_to_response(company)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a company by ID."""
    repo = SqlAlchemyCompanyRepository(db)
    company = repo.find_by_id(company_id)
    
    if company is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    
    return _company_to_response(company)
