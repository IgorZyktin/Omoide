# -*- coding: utf-8 -*-
"""Search related routes.
"""
import time
from typing import Type

import fastapi
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import Response

from omoide import domain
from omoide import use_cases
from omoide import utils
from omoide.infra.special_types import Failure
from omoide.presentation import constants
from omoide.presentation import dependencies as dep
from omoide.presentation import infra
from omoide.presentation import web
from omoide.presentation.app_config import Config

router = fastapi.APIRouter()


@router.get('/search')
async def app_search(
        request: Request,
        user: domain.User = Depends(dep.get_current_user),
        use_case_dynamic: use_cases.AppDynamicSearchUseCase = Depends(
            dep.app_dynamic_search_use_case),
        use_case_paged: use_cases.AppPagedSearchUseCase = Depends(
            dep.app_paged_search_use_case),
        aim_wrapper: web.AimWrapper = Depends(dep.get_aim),
        config: Config = Depends(dep.config),
        response_class: Type[Response] = HTMLResponse,
):
    """Main page of the application."""
    start = time.perf_counter()
    aim = aim_wrapper.aim
    query = infra.query_maker.from_request(request.query_params)

    result = await use_case_dynamic.execute(user, query, aim_wrapper.aim)
    if isinstance(result, Failure):
        return web.redirect_from_error(request, result.error)

    matching_items = result.value

    if aim.paged:
        template = 'search_paged.html'
        paged_result = await use_case_paged.execute(user, query, aim)

        if isinstance(paged_result, Failure):
            return web.redirect_from_error(request, paged_result.error)

        items = paged_result.value
        paginator = infra.Paginator(
            page=aim.page,
            items_per_page=aim.items_per_page,
            total_items=matching_items,
            pages_in_block=constants.PAGES_IN_BLOCK,
        )

    else:
        items = []
        template = 'search_dynamic.html'
        paginator = None

    delta = time.perf_counter() - start

    context = {
        'request': request,
        'config': config,
        'user': user,
        'aim': aim,
        'query': infra.query_maker.QueryWrapper(query, details),
        'details': details,
        'paginator': paginator,
        'items': items,
        'matching_items': utils.sep_digits(matching_items),
        'delta': f'{delta:0.3f}',
        'endpoint': request.url_for('api_search'),
    }

    return dep.templates.TemplateResponse(template, context)
