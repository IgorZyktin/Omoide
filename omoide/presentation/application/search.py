# -*- coding: utf-8 -*-
"""Search related routes.
"""
import fastapi
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from omoide import use_cases
from omoide.domain import auth
from omoide.presentation import dependencies, constants
from omoide.presentation import infra

router = fastapi.APIRouter()

templates = Jinja2Templates(directory='presentation/templates')


@router.get('/')
@router.get('/search')
async def search(
        request: fastapi.Request,
        user: auth.User = fastapi.Depends(dependencies.get_current_user),
        use_case: use_cases.SearchUseCase = fastapi.Depends(
            dependencies.get_search_use_case
        ),
        response_class=HTMLResponse,
):
    """Main page of the application."""
    query = infra.query_maker.from_request(
        params=request.query_params,
        items_per_page=constants.ITEMS_PER_PAGE,
    )

    with infra.Timer() as timer:
        result = await use_case.execute(user, query.query)

    if result.is_random:
        paginator = infra.Paginator.empty()
    else:
        paginator = infra.Paginator(
            page=result.page,
            items_per_page=query.query.items_per_page,
            total_items=result.total_items,
            pages_in_block=constants.PAGES_IN_BLOCK,
        )

    context = {
        'request': request,
        'query': query,
        'placeholder': 'Enter something',
        'paginator': paginator,
        'result': result,
        'duration': timer.seconds,
    }
    return dependencies.templates.TemplateResponse('search.html', context)
