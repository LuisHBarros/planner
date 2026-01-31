"""JWT service using authlib."""
from __future__ import annotations

from typing import Any, Dict

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import UtcDateTime


class JwtService:
    """JWT creation/validation service."""

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def create_token(self, subject: str, expires_at: UtcDateTime) -> str:
        """Create a JWT token."""
        try:
            from authlib.jose import jwt
        except ModuleNotFoundError as exc:
            raise BusinessRuleViolation("authlib is not installed", code="authlib_missing") from exc
        header = {"alg": self.algorithm}
        payload = {"sub": subject, "exp": int(expires_at.value.timestamp())}
        token = jwt.encode(header, payload, self.secret)
        return token.decode("utf-8") if isinstance(token, bytes) else str(token)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return claims."""
        try:
            from authlib.jose import JoseError, jwt
            claims = jwt.decode(token, self.secret)
            claims.validate()
            return dict(claims)
        except JoseError as exc:
            raise BusinessRuleViolation("Invalid token", code="invalid_token") from exc
        except ModuleNotFoundError as exc:
            raise BusinessRuleViolation("authlib is not installed", code="authlib_missing") from exc
