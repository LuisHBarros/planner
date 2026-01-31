"""API exception handlers."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import BusinessRuleViolation


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers."""

    @app.exception_handler(BusinessRuleViolation)
    async def business_rule_handler(
        _request: Request,
        exc: BusinessRuleViolation,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "code": exc.code},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
