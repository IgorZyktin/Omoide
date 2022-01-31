# -*- coding: utf-8 -*-
"""Browse related routes.
"""
import fastapi
from fastapi.responses import HTMLResponse

from omoide import use_cases
from omoide.domain import auth
from omoide.presentation import dependencies, infra, constants

router = fastapi.APIRouter()


@router.get('/browse/{uuid}')
async def browse(
        request: fastapi.Request,
        uuid: str,
        user: auth.User = fastapi.Depends(dependencies.get_current_user),
        use_case: use_cases.BrowseUseCase = fastapi.Depends(
            dependencies.get_browse_use_case
        ),
        response_class=HTMLResponse,
):
    """Browse contents of a single item as collection."""
    query = infra.query_maker.from_request(
        params=request.query_params,
        items_per_page=constants.ITEMS_PER_PAGE,
    )

    result = await use_case.execute(user, uuid, query.query)

    if result.access.does_not_exist:
        raise fastapi.HTTPException(status_code=404)

    if result.access.is_not_given:
        raise fastapi.HTTPException(status_code=401)

    paginator = infra.Paginator(
        page=result.page,
        items_per_page=query.query.items_per_page,
        total_items=result.total_items,
        pages_in_block=constants.PAGES_IN_BLOCK,
    )

    context = {
        'request': request,
        'uuid': uuid,
        'query': query,
        'placeholder': 'Enter something',
        'paginator': paginator,
        'result': result,
    }
    return dependencies.templates.TemplateResponse('browse.html', context)
