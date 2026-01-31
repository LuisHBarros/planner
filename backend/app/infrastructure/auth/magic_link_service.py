"""Magic link service."""
from __future__ import annotations

from uuid import uuid4

from app.domain.models.value_objects import InviteToken


class MagicLinkService:
    """Service to generate magic link tokens."""

    def generate_token(self) -> InviteToken:
        """Generate a new invite token."""
        return InviteToken(str(uuid4()))
