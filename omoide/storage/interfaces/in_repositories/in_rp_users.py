"""Repository that performs operations on users."""
import abc
from typing import Any
from uuid import UUID

from omoide import models


class AbsUsersRepo(abc.ABC):
    """Repository that performs read operations on users."""

    @abc.abstractmethod
    async def get_free_uuid(self) -> UUID:
        """Generate new unused UUID."""

    @abc.abstractmethod
    async def create_user(
        self,
        user: models.User,
        auth_complexity: int,
    ) -> models.User:
        """Create new user."""

    @abc.abstractmethod
    async def read_user(self, uuid: UUID) -> models.User | None:
        """Return User or None."""

    @abc.abstractmethod
    async def update_user(self, uuid: UUID, user: dict[str, Any]) -> None:
        """Update User."""

    @abc.abstractmethod
    async def read_filtered_users(
        self,
        *uuids: UUID,
        login: str | None = None,
    ) -> list[models.User]:
        """Return list of users with given uuids or filters."""

    @abc.abstractmethod
    async def read_all_users(self) -> list[models.User]:
        """Return all users."""

    @abc.abstractmethod
    async def calc_total_space_used_by(
        self,
        user: models.User,
    ) -> models.SpaceUsage:
        """Return total amount of used space for user."""

    @abc.abstractmethod
    async def user_is_public(self, uuid: UUID) -> bool:
        """Return True if given user is public."""

    @abc.abstractmethod
    async def get_public_users_uuids(self) -> set[UUID]:
        """Return set of UUIDs for public users."""
