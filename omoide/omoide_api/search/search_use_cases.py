"""Use cases that process search requests from users."""

import re
import time
from itertools import chain
from typing import Any

from omoide import const
from omoide import models
from omoide import utils
from omoide.omoide_api.common.common_use_cases import BaseAPIUseCase


class AutocompleteUseCase(BaseAPIUseCase):
    """Use case for suggesting tag autocomplete."""

    async def execute(
        self,
        user: models.User,
        tag: str,
        minimal_length: int,
        limit: int,
    ) -> list[str]:
        """Execute."""
        if len(tag) < minimal_length:
            return []

        async with self.mediator.database.transaction() as conn:
            if user.is_anon:
                variants = await self.mediator.search.autocomplete_tag_anon(conn, tag, limit)
            else:
                variants = await self.mediator.search.autocomplete_tag_known(conn, user, tag, limit)
        return variants


class RecentUpdatesUseCase(BaseAPIUseCase):
    """Use case for getting recently updated items."""

    async def execute(
        self,
        user: models.User,
        order: const.ORDER_TYPE,
        collections: bool,
        last_seen: int,
        limit: int,
    ) -> tuple[list[models.Item], dict[int, models.User | None]]:
        """Execute."""
        self.mediator.policy.ensure_registered(user, to='read recently updated items')

        async with self.mediator.database.transaction() as conn:
            items = await self.mediator.browse.get_recently_updated_items(
                conn=conn,
                user=user,
                order=order,
                collections=collections,
                last_seen=last_seen,
                limit=limit,
            )
            users = await self.mediator.users.get_map(conn, items)

        return items, users


class BaseSearchUseCase(BaseAPIUseCase):
    """Base class for search queries."""

    pattern = re.compile(r'(\s+\+\s+|\s+-\s+)')

    def parse_tags(self, query: str) -> tuple[set[str], set[str]]:
        """Split  user query into tags."""
        tags_include: set[str] = set()
        tags_exclude: set[str] = set()

        parts = self.pattern.split(query)
        clean_parts = [x.strip() for x in parts if x.strip()]

        if not clean_parts:
            return tags_include, tags_exclude

        if clean_parts[0] not in ('+', '-'):
            clean_parts.insert(0, '+')

        for operator, tag in utils.group_to_size(clean_parts):
            _tag = str(tag).lower()
            if operator == '+':
                tags_include.add(_tag)
            else:
                tags_exclude.add(_tag)

        return tags_include, tags_exclude


class ApiSearchTotalUseCase(BaseSearchUseCase):
    """Use case for calculating total results of search."""

    async def execute(
        self,
        user: models.User,
        query: str,
        minimal_length: int,
        collections: bool,
    ) -> tuple[int, float]:
        """Execute."""
        total = 0
        duration = 0.0

        if len(query) < minimal_length:
            return total, duration

        start = time.perf_counter()
        tags_include, tags_exclude = self.parse_tags(query)

        async with self.mediator.database.transaction() as conn:
            total = await self.mediator.search.count(
                conn=conn,
                user=user,
                tags_include=tags_include,
                tags_exclude=tags_exclude,
                collections=collections,
            )

        duration = time.perf_counter() - start

        return total, duration


class ApiSearchUseCase(BaseSearchUseCase):
    """Use case for search."""

    async def execute(
        self,
        user: models.User,
        query: str,
        minimal_length: int,
        order: const.ORDER_TYPE,
        collections: bool,
        last_seen: int,
        limit: int,
    ) -> tuple[float, list[models.Item], list[dict[str, Any]]]:
        """Execute."""
        duration = 0.0
        items: list[models.Item] = []
        extras: list[dict[str, Any]] = []

        if len(query) < minimal_length:
            return duration, items, extras

        start = time.perf_counter()
        tags_include, tags_exclude = self.parse_tags(query)

        async with self.mediator.database.transaction() as conn:
            items = await self.mediator.search.search(
                conn=conn,
                user=user,
                tags_include=tags_include,
                tags_exclude=tags_exclude,
                order=order,
                collections=collections,
                last_seen=last_seen,
                limit=limit,
            )
            names = await self.mediator.items.get_parent_names(conn, items)

        duration = time.perf_counter() - start

        return duration, items, [{'parent_name': names.get(item.parent_id)} for item in items]
