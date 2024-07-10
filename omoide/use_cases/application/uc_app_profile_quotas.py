"""Use case for user profile quotas."""
from omoide import models
from omoide.domain import errors
from omoide.domain import interfaces
from omoide.infra.mediator import Mediator
from omoide.infra.special_types import Failure
from omoide.infra.special_types import Result
from omoide.infra.special_types import Success
from omoide.storage.interfaces.in_repositories.in_rp_users import AbsUsersRepo

__all__ = [
    'AppProfileQuotasUseCase',
]


class AppProfileQuotasUseCase:
    """Use case for user profile quotas."""

    def __init__(
            self,
            mediator: Mediator,
            users_repo: AbsUsersRepo,
            items_repo: interfaces.AbsItemsRepo,
    ) -> None:
        """Initialize instance."""
        self.mediator = mediator
        self.users_repo = users_repo
        self.items_repo = items_repo

    async def execute(
            self,
            user: models.User,
    ) -> Result[errors.Error, tuple[models.SpaceUsage, int, int]]:
        """Return amount of items that correspond to query (not items)."""
        if user.is_anon or user.uuid is None:
            return Failure(errors.AuthenticationRequired())

        if user.root_item is None:
            return Success((models.SpaceUsage.empty(user.uuid), 0, 0))

        async with self.mediator.storage.transaction():
            root = await self.items_repo.read_item(user.root_item)
            if root is None:
                return Success((models.SpaceUsage.empty(user.uuid), 0, 0))

            size = await self.users_repo.calc_total_space_used_by(user)
            total_items = await self.items_repo \
                .count_items_by_owner(user)
            total_collections = await self.items_repo \
                .count_items_by_owner(user, only_collections=True)

        return Success((size, total_items, total_collections))
