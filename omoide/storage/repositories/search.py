# -*- coding: utf-8 -*-
"""Search repository.
"""
from omoide.domain import auth, search, common
from omoide.domain.interfaces import database
from omoide.storage.repositories import base


class SearchRepository(
    base.BaseRepository,
    database.AbsSearchRepository
):
    """Repository that performs all search queries."""

    async def total_random_anon(self) -> int:
        """Count all available items for unauthorised user."""
        query = """
        SELECT count(*) AS total_items
        FROM items
        WHERE owner_uuid IN (SELECT user_uuid FROM public_users);
        """

        response = await self.db.fetch_one(query)
        return int(response['total_items'])

    async def total_specific_anon(self, query: common.Query) -> int:
        """Count available items for unauthorised user."""
        _query = """
        SELECT count(*) AS total_items
        FROM items it
                 RIGHT JOIN computed_tags ct ON ct.item_uuid = it.uuid
        WHERE owner_uuid IN (SELECT user_uuid FROM public_users)
          AND ct.tags @> :tags_include
          AND NOT ct.tags && :tags_exclude;
        """

        values = {
            'tags_include': query.tags_include,
            'tags_exclude': query.tags_exclude,
        }

        response = await self.db.fetch_one(_query, values)
        return int(response['total_items'])

    async def search_random_anon(
            self,
            query: common.Query,
    ) -> list[common.Item]:
        """Find random items for unauthorised user."""
        _query = """
        SELECT uuid, 
               parent_uuid,
               owner_uuid,
               number,
               name,
               is_collection,
               content_ext,
               preview_ext,
               thumbnail_ext
        FROM items
        WHERE owner_uuid IN (SELECT user_uuid FROM public_users)
        ORDER BY random() LIMIT :limit OFFSET :offset;
        """

        values = {
            'limit': query.items_per_page,
            'offset': query.offset,
        }

        response = await self.db.fetch_all(_query, values)
        return [common.Item.from_map(row) for row in response]

    async def search_specific_anon(
            self,
            query: common.Query,
    ) -> list[common.Item]:
        """Find specific items for unauthorised user."""
        _query = """
        SELECT uuid, 
               parent_uuid,
               owner_uuid,
               number,
               name,
               is_collection,
               content_ext,
               preview_ext,
               thumbnail_ext,
               ct.tags
        FROM items it
                 RIGHT JOIN computed_tags ct ON ct.item_uuid = it.uuid
        WHERE owner_uuid IN (SELECT user_uuid FROM public_users)
          AND ct.tags @> :tags_include
          AND NOT ct.tags && :tags_exclude
        ORDER BY number LIMIT :limit OFFSET :offset;
        """

        values = {
            'limit': query.items_per_page,
            'offset': query.offset,
            'tags_include': query.tags_include,
            'tags_exclude': query.tags_exclude,
        }

        response = await self.db.fetch_all(_query, values)
        return [common.Item.from_map(row) for row in response]

    async def total_random_known(
            self,
            user: auth.User,
    ) -> int:
        """Count all available items for authorised user."""
        # TODO(i.zyktin): need to implement this
        raise NotImplementedError

    async def total_specific_known(
            self,
            user: auth.User,
            query: common.Query,
    ) -> int:
        """Count available items for authorised user."""
        # TODO(i.zyktin): need to implement this
        raise NotImplementedError

    async def search_random_known(
            self,
            user: auth.User,
            query: common.Query,
    ) -> search.Result:
        """Find random items for authorised user."""
        # TODO(i.zyktin): need to implement this
        raise NotImplementedError

    async def search_specific_known(
            self,
            user: auth.User,
            query: common.Query,
    ) -> search.Result:
        """Find specific items for authorised user."""
        # TODO(i.zyktin): need to implement this
        raise NotImplementedError
