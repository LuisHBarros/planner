"""Domain exceptions for business rule violations."""
from typing import Optional


class BusinessRuleViolation(Exception):
    """Raised when a business rule is violated."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DomainError(Exception):
    """Base exception for domain errors."""
    pass
