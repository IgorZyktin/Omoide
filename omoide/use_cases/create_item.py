# -*- coding: utf-8 -*-
"""Use case for item creation.
"""
from typing import Optional
from uuid import UUID

from omoide import domain
from omoide.domain import interfaces


class CreateItemUseCase:
    """Use case for item creation."""

    def __init__(self, repo: interfaces.AbsItemCRUDRepository) -> None:
        """Initialize instance."""
        self._repo = repo

    async def execute(
            self,
            user: domain.User,
            payload: domain.CreateItemPayload,
    ) -> tuple[domain.AccessStatus, Optional[UUID]]:
        """Return preview model suitable for rendering."""
        async with self._repo.transaction():
            payload.uuid = await self._repo.generate_uuid()

            if not payload.parent_uuid:
                # TODO - need to implement root level items
                access = domain.AccessStatus(
                    exists=True,
                    is_public=False,
                    is_permitted=True,
                    is_owner=True,
                )
                item_uuid = await self._repo.create_root_item(user, payload)
            else:
                access = await self._repo.check_access(user,
                                                       payload.parent_uuid)

                if access.is_given:
                    item_uuid = await self._repo.create_dependant_item(user,
                                                                       payload)
                else:
                    item_uuid = None

        return access, item_uuid
