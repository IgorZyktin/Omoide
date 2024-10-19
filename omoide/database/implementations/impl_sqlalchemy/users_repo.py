"""Repository that performs operations on users."""

from collections.abc import Collection
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from omoide import exceptions
from omoide import models
from omoide.database import db_models
from omoide.database.interfaces.abs_users_repo import AbsUsersRepo


class UsersRepo(AbsUsersRepo[AsyncConnection]):
    """Repository that performs operations on users."""

    @staticmethod
    def _user_from_response(response: Any) -> models.User:
        """Convert DB response to user model."""
        return models.User(
            id=response.id,
            uuid=response.uuid,
            name=response.name,
            login=response.login,
            role=response.role,
            is_public=response.is_public,
        )

    async def get_by_id(
        self,
        conn: AsyncConnection,
        user_id: int,
    ) -> models.User:
        """Return User with given id."""
        stmt = sa.select(db_models.User).where(db_models.User.id == user_id)
        response = (await conn.execute(stmt)).first()

        if response is None:
            msg = 'User with ID {user_id} does not exist'
            raise exceptions.DoesNotExistError(msg, user_id=user_id)

        return self._user_from_response(response)

    async def get_by_uuid(
        self,
        conn: AsyncConnection,
        uuid: UUID,
    ) -> models.User:
        """Return User with given UUID."""
        stmt = sa.select(db_models.User).where(db_models.User.uuid == uuid)
        response = (await conn.execute(stmt)).first()

        if response is None:
            msg = 'User with UUID {user_uuid} does not exist'
            raise exceptions.DoesNotExistError(msg, user_uuid=uuid)

        return self._user_from_response(response)

    async def select(
        self,
        conn: AsyncConnection,
        user_id: int | None = None,
        uuid: UUID | None = None,
        login: str | None = None,
        ids: Collection[int] | None = None,
        uuids: Collection[UUID] | None = None,
        limit: int | None = None,
    ) -> list[models.User]:
        """Return filtered list of users."""
        stmt = sa.select(db_models.User)

        if user_id is not None:
            stmt = stmt.where(db_models.User.id == user_id)

        if uuid is not None:
            stmt = stmt.where(db_models.User.uuid == uuid)

        if login is not None:
            stmt = stmt.where(db_models.User.login == login)

        if ids is not None:
            stmt = stmt.where(db_models.User.id.in_(tuple(ids)))

        if uuids is not None:
            stmt = stmt.where(db_models.User.uuid.in_(tuple(uuids)))

        if limit is not None:
            stmt = stmt.limit(limit)

        response = (await conn.execute(stmt)).fetchall()
        return [self._user_from_response(row) for row in response]
