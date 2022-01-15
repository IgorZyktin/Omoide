# -*- coding: utf-8 -*-
"""External components.
"""
from databases import Database

from omoide import use_cases
from omoide.domain import auth
from omoide.storage import repositories

DB_URL = 'postgresql://postgres:mypass@localhost:5432/test'

db = Database(DB_URL)

search_repository = repositories.SearchRepository(db)
search_use_case = use_cases.SearchUseCase(search_repository)


def get_current_user():
    """Load current user or use anon user."""
    return auth.User(
        uuid=None,
        login='anon',
        password='',
        name='anon',
        visiblity=None,
        language=None,
        last_seen=None,
    )


def get_search_use_case():
    """Get use case instance."""
    return search_use_case
