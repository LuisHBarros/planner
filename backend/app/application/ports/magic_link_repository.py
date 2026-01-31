"""MagicLink repository port."""
from typing import Protocol, Optional

from app.domain.models.magic_link import MagicLink
from app.domain.models.value_objects import InviteToken, MagicLinkId


class MagicLinkRepository(Protocol):
    """Repository interface for MagicLink entities."""

    def save(self, magic_link: MagicLink) -> None:
        """Persist a magic link."""
        ...

    def find_by_id(self, link_id: MagicLinkId) -> Optional[MagicLink]:
        """Find magic link by ID."""
        ...

    def find_by_token(self, token: InviteToken) -> Optional[MagicLink]:
        """Find magic link by token."""
        ...
