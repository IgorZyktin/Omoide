"""Interface for access policy.
"""
import abc

from omoide import domain
from omoide.domain import actions
from omoide.domain.errors import Error
from omoide.domain.interfaces.in_storage \
    .in_repositories import in_rp_items_read
from omoide.infra import impl

__all__ = [
    'AbsPolicy',
]


class AbsPolicy(abc.ABC):
    """Abstract policy checker."""

    def __init__(
            self,
            items_repo: in_rp_items_read.AbsItemsReadRepository,
    ) -> None:
        """Initialize instance."""
        self.items_repo = items_repo

    @abc.abstractmethod
    async def is_restricted(
            self,
            user: domain.User,
            uuid: impl.UUID | None,
            action: actions.Action,
    ) -> Error | None:
        """Return Error if action is not permitted."""
