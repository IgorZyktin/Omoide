"""Repository that performs various operations on different objects."""

import sqlalchemy as sa
from databases.core import Database
from sqlalchemy.dialects.postgresql import insert as pg_insert

from omoide import models
from omoide.database import db_models
from omoide.database.interfaces.abs_signatures_repo import AbsSignaturesRepo


class SignaturesRepo(AbsSignaturesRepo[Database]):
    """Repository that performs various operations on different objects."""

    async def get_md5_signature(
        self,
        conn: Database,
        item: models.Item,
    ) -> str | None:
        """Get signature record."""
        query = sa.select(db_models.SignatureMD5).where(
            db_models.SignatureMD5.item_id == item.id
        )

        response = await conn.fetch_one(query)

        if response is None:
            return None

        return response['signature']

    async def get_md5_signatures(
        self,
        conn: Database,
        items: list[models.Item],
    ) -> dict[int, str | None]:
        """Get many signatures."""
        ids = [item.id for item in items]
        signatures: dict[int, str | None] = dict.fromkeys(ids)

        query = sa.select(
            db_models.SignatureMD5.item_id,
            db_models.SignatureMD5.signature,
        ).where(db_models.SignatureMD5.item_id.in_(ids))

        response = await conn.fetch_all(query)
        for row in response:
            signatures[row['item_id']] = row['signature']

        return signatures

    async def save_md5_signature(
        self,
        conn: Database,
        item: models.Item,
        signature: str,
    ) -> None:
        """Create signature record."""
        insert = pg_insert(db_models.SignatureMD5).values(
            item_id=item.id,
            signature=signature,
        )

        stmt = insert.on_conflict_do_update(
            index_elements=[db_models.SignatureMD5.item_id],
            set_={'signature': insert.excluded.signature},
        )

        await conn.execute(stmt)

    async def get_cr32_signature(
        self,
        conn: Database,
        item: models.Item,
    ) -> int | None:
        """Get signature record."""
        query = sa.select(db_models.SignatureCRC32).where(
            db_models.SignatureCRC32.item_id == item.id
        )

        response = await conn.fetch_one(query)

        if response is None:
            return None

        return response['signature']

    async def get_cr32_signatures(
        self,
        conn: Database,
        items: list[models.Item],
    ) -> dict[int, int | None]:
        """Get many signatures."""
        ids = [item.id for item in items]
        signatures: dict[int, str | None] = dict.fromkeys(ids)

        query = sa.select(
            db_models.SignatureCRC32.item_id,
            db_models.SignatureCRC32.signature,
        ).where(db_models.SignatureCRC32.item_id.in_(ids))

        response = await conn.fetch_all(query)
        for row in response:
            signatures[row['item_id']] = row['signature']

        return signatures

    async def save_cr32_signature(
        self,
        conn: Database,
        item: models.Item,
        signature: str,
    ) -> None:
        """Create signature record."""
        insert = pg_insert(db_models.SignatureCRC32).values(
            item_id=item.id,
            signature=signature,
        )

        stmt = insert.on_conflict_do_update(
            index_elements=[db_models.SignatureCRC32.item_id],
            set_={'signature': insert.excluded.signature},
        )

        await conn.execute(stmt)
