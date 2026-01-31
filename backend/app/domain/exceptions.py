"""Domain exceptions."""


class BusinessRuleViolation(ValueError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str, code: str = "business_rule_violation"):
        super().__init__(message)
        self.code = code
