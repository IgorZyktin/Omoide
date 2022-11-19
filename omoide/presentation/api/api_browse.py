# -*- coding: utf-8 -*-
"""Browse page related API operations.
"""
import fastapi
from fastapi import Depends
from starlette.requests import Request

from omoide import domain
from omoide import use_cases
from omoide import utils as global_utils
from omoide.domain import interfaces
from omoide.infra.special_types import Failure
from omoide.presentation import dependencies as dep
from omoide.presentation import utils
from omoide.presentation import web

router = fastapi.APIRouter()


@router.get('/api/browse/{uuid}')
async def api_browse(
        request: Request,
        uuid: str,
        user: domain.User = Depends(dep.get_current_user),
        policy: interfaces.AbsPolicy = Depends(dep.get_policy),
        use_case: use_cases.APIBrowseUseCase = Depends(
            dep.api_browse_use_case),
        aim_wrapper: web.AimWrapper = Depends(dep.get_aim),
):
    """Return portion of items for browse template."""
    valid_uuid = global_utils.cast_uuid(uuid)

    if valid_uuid is None:
        return []

    result = await use_case.execute(policy, user, valid_uuid, aim_wrapper.aim)

    if isinstance(result, Failure):
        return []

    return utils.to_simple_items(request, result.value)
