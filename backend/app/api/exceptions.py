"""Exception handlers for FastAPI."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import BusinessRuleViolation


def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the application."""
    
    @app.exception_handler(BusinessRuleViolation)
    async def business_rule_violation_handler(
        request: Request, exc: BusinessRuleViolation
    ):
        """Handle business rule violations."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Business rule violation",
                "message": exc.message,
                "code": exc.code,
            },
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation error", "message": str(exc)},
        )
