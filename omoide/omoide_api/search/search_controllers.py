"""API operations that process textual requests from users."""
from typing import Annotated
from typing import Literal

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status

from omoide import custom_logging
from omoide import models
from omoide import utils
from omoide.infra.mediator import Mediator
from omoide.omoide_api.common import common_api_models
from omoide.omoide_api.search import search_api_models
from omoide.omoide_api.search import search_use_cases
from omoide.presentation import dependencies as dep

LOG = custom_logging.get_logger(__name__)

search_router = APIRouter(prefix='/search', tags=['Search'])


@search_router.get(
    '/autocomplete',
    status_code=status.HTTP_200_OK,
    response_model=search_api_models.AutocompleteOutput,
)
async def api_autocomplete(
    user: Annotated[models.User, Depends(dep.get_current_user)],
    mediator: Annotated[Mediator, Depends(dep.get_mediator)],
    tag: Annotated[str, Query(
        max_length=search_api_models.AUTOCOMPLETE_MAX_LENGTH,
    )] = search_api_models.AUTOCOMPLETE_DEFAULT,
    limit: Annotated[int, Query(
        ge=search_api_models.AUTOCOMPLETE_MIN_LIMIT,
        lt=search_api_models.AUTOCOMPLETE_MAX_LIMIT,
    )] = search_api_models.AUTOCOMPLETE_DEFAULT_LIMIT,
):
    """Return tags that match supplied string.

    You will get list of strings, ordered by their frequency.
    Most popular tags will be at the top.

    This endpoint can be used by anybody, but each user will get tailored
    output. String must be an exact match, no guessing is used.
    """
    use_case = search_use_cases.AutocompleteUseCase(mediator)

    # noinspection PyBroadException
    try:
        variants = await use_case.execute(
            user=user,
            tag=tag,
            minimal_length=search_api_models.AUTOCOMPLETE_MIN_LENGTH,
            limit=limit,
        )
    except Exception:
        LOG.exception(
            'Failed to perform autocompletion for user {} and input {!r}',
            user,
            tag
        )
        variants = []

    return search_api_models.AutocompleteOutput(variants=variants)


@search_router.get(
    '/recent_updates',
    status_code=status.HTTP_200_OK,
    response_model=search_api_models.RecentUpdatesOutput,
)
async def api_get_recent_updates(
    user: Annotated[models.User, Depends(dep.get_known_user)],
    mediator: Annotated[Mediator, Depends(dep.get_mediator)],
    last_seen: Annotated[int, Query()] = search_api_models.LAST_SEEN_DEFAULT,
    limit: Annotated[int, Query(
        ge=search_api_models.RECENT_UPDATES_MIN_LIMIT,
        lt=search_api_models.RECENT_UPDATES_MAX_LIMIT,
    )] = search_api_models.RECENT_UPDATES_DEFAULT_LIMIT,
):
    """Return recently updated items.

    Request will find when newest item was updated.
    And then return all items uploaded at that day.

    This endpoint can be used by any registered user,
    but each will get tailored output.
    """
    use_case = search_use_cases.RecentUpdatesUseCase(mediator)

    items, parent_names = await use_case.execute(
        user=user,
        last_seen=last_seen,
        limit=limit,
    )

    return search_api_models.RecentUpdatesOutput(
        items=[
            common_api_models.ItemOutput(
                **item.model_dump(),
                extras={'parent_name': parent_name}
            )
            for item, parent_name in zip(items, parent_names)
        ],
    )


@search_router.get(
    'total',
    response_model=search_api_models.SearchTotalOutput,
)
async def api_search_total(
    user: Annotated[models.User, Depends(dep.get_current_user)],
    mediator: Annotated[Mediator, Depends(dep.get_mediator)],
    q: Annotated[str, Query(
        max_length=search_api_models.SEARCH_QUERY_MAX_LENGTH,
    )] = search_api_models.SEARCH_QUERY_DEFAULT,
    only_collections: Annotated[bool, Query()] = False,
):
    """Return total amount of items that correspond to search query."""
    use_case = search_use_cases.ApiSearchTotalUseCase(mediator)

    total, duration = await use_case.execute(
        user=user,
        query=q,
        minimal_length=search_api_models.SEARCH_QUERY_MIN_LENGTH,
        only_collections=only_collections,
    )

    return search_api_models.SearchTotalOutput(
        total=total,
        duration=duration,
    )


@search_router.get(
    '',
    response_model=search_api_models.SearchOutput,
)
async def api_search(
    user: Annotated[models.User, Depends(dep.get_current_user)],
    mediator: Annotated[Mediator, Depends(dep.get_mediator)],
    q: Annotated[str, Query(
        max_length=search_api_models.SEARCH_QUERY_MAX_LENGTH,
    )] = search_api_models.SEARCH_QUERY_DEFAULT,
    only_collections: Annotated[bool, Query()] = False,
    ordering: Annotated[Literal['asc', 'desc', 'random'], Query()] = 'random',
    last_seen: Annotated[int, Query()] = search_api_models.LAST_SEEN_DEFAULT,
    limit: Annotated[int, Query(
        ge=search_api_models.SEARCH_QUERY_MIN_LIMIT,
        lt=search_api_models.SEARCH_QUERY_MAX_LIMIT,
    )] = search_api_models.SEARCH_QUERY_DEFAULT_LIMIT,
):
    """Perform search request.

    Given input will be split into tags.
    For example 'cats + dogs - frogs' will be treated as
    [must include 'cats', must include 'dogs', must not include 'frogs'].
    """
    use_case = search_use_cases.ApiSearchUseCase(mediator)

    duration, items, extras = await use_case.execute(
        user=user,
        query=q,
        minimal_length=search_api_models.SEARCH_QUERY_MIN_LENGTH,
        only_collections=only_collections,
        ordering=ordering,
        last_seen=last_seen,
        limit=limit,
    )

    return search_api_models.SearchOutput(
        duration=duration,
        items=[
            common_api_models.ItemOutput(
                **utils.serialize(item.model_dump()),
                extras=utils.serialize(item_extras),
            )
            for item, item_extras in zip(items, extras)
        ]
    )
