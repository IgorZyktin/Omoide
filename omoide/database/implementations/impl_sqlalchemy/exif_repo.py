"""Repository that perform operations on EXIF data."""

from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncConnection

from omoide import exceptions
from omoide import models
from omoide.database import db_models
from omoide.database.interfaces.abs_exif_repo import AbsEXIFRepo


class EXIFRepo(AbsEXIFRepo[AsyncConnection]):
    """Repository that perform operations on EXIF data."""

    async def create(self, conn: AsyncConnection, item: models.Item, exif: dict[str, Any]) -> None:
        """Create EXIF record for given item."""
        stmt = sa.insert(db_models.EXIF).values(item_id=item.id, exif=exif)

        try:
            await conn.execute(stmt)
        except sa.exc.IntegrityError as exc:
            msg = 'EXIF data for item {item_uuid} already exists'
            raise exceptions.AlreadyExistsError(msg, item_uuid=item.uuid) from exc

    async def get_by_item(self, conn: AsyncConnection, item: models.Item) -> dict[str, Any]:
        """Return EXIF record for given item."""
        query = sa.select(db_models.EXIF.exif).where(db_models.EXIF.item_id == item.id)

        response = (await conn.execute(query)).scalar()

        if response is None:
            msg = 'EXIF data for item {item_uuid} does not exist'
            raise exceptions.DoesNotExistError(msg, item_uuid=item.uuid)

        return dict(response)

    async def save(self, conn: AsyncConnection, item: models.Item, exif: dict[str, Any]) -> bool:
        """Update existing EXIF record for given item or create new one."""
        insert = pg_insert(db_models.EXIF).values(item_id=item.id, exif=exif)
        stmt = insert.on_conflict_do_update(
            index_elements=[db_models.EXIF.item_id],
            set_={'exif': insert.excluded.exif},
        )

        response = await conn.execute(stmt)
        return bool(response.rowcount)

    async def delete(self, conn: AsyncConnection, item: models.Item) -> None:
        """Delete EXIF record for given item."""
        stmt = sa.delete(db_models.EXIF).where(db_models.EXIF.item_id == item.id).returning(1)

        response = await conn.execute(stmt)

        if response is None:
            msg = 'EXIF data for item {item_uuid} does not exist'
            raise exceptions.DoesNotExistError(msg, item_uuid=item.uuid)
