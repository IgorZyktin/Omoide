"""Repository that performs CRUD operations on EXIF."""

from typing import Any

import sqlalchemy as sa
from asyncpg import exceptions as asyncpg_exceptions
from databases.core import Database
from sqlalchemy.dialects.postgresql import insert as pg_insert

from omoide import exceptions
from omoide import models
from omoide.database import db_models
from omoide.database.interfaces.abs_exif_repo import AbsEXIFRepo


# TODO - remove this class
class EXIFRepository(AbsEXIFRepo[Database]):
    """Repository that performs CRUD operations on EXIF."""

    async def create(
        self,
        conn: Database,
        item: models.Item,
        exif: dict[str, Any],
    ) -> None:
        """Create EXIF record for given item or update existing one."""
        stmt = sa.insert(db_models.EXIF).values(item_id=item.id, exif=exif)

        try:
            await conn.execute(stmt)
        except asyncpg_exceptions.UniqueViolationError as exc:
            msg = 'EXIF data for item {item_uuid} already exists'
            raise exceptions.AlreadyExistsError(
                msg,
                item_uuid=item.uuid,
            ) from exc

    async def get_by_item(
        self,
        conn: Database,
        item: models.Item,
    ) -> dict[str, Any]:
        """Return EXIF record for given item."""
        stmt = sa.select(db_models.EXIF).where(
            db_models.EXIF.item_id == item.id
        )

        response = await conn.fetch_one(stmt)

        if response is None:
            msg = 'EXIF data for item {item_uuid} does not exist'
            raise exceptions.DoesNotExistError(msg, item_uuid=item.uuid)

        return dict(response['exif'])

    async def save(
        self,
        conn: Database,
        item: models.Item,
        exif: dict[str, Any],
    ) -> bool:
        """Update existing EXIF record for given item or create new one."""
        insert = (
            pg_insert(db_models.EXIF)
            .where(db_models.EXIF.item_id == item.id)
            .values(exif=exif)
        )

        stmt = insert.on_conflict_do_update(
            index_elements=[db_models.EXIF.item_id],
            set_={'exif': insert.excluded.exif},
        )

        await conn.execute(stmt)
        return True

    async def delete(
        self,
        conn: Database,
        item: models.Item,
    ) -> None:
        """Delete EXIF record for given item."""
        stmt = (
            sa.delete(db_models.EXIF)
            .where(db_models.EXIF.item_id == item.id)
            .returning(1)
        )

        response = await conn.fetch_one(stmt)

        if response is None:
            msg = 'EXIF data for item {item_uuid} does not exist'
            raise exceptions.DoesNotExistError(msg, item_uuid=item.uuid)
