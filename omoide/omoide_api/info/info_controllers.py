"""Technical information about the API."""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from omoide import const
from omoide import models
from omoide.presentation import dependencies as dep

api_info_router = APIRouter(prefix='/info', tags=['Info'])


@api_info_router.get(
    '/version',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
)
async def api_get_version() -> dict[str, str]:
    """Get current version of the API."""
    return {'version': const.VERSION}


@api_info_router.get(
    '/whoami',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str | None],
)
async def api_get_myself(
    user: Annotated[models.User, Depends(dep.get_current_user)],
) -> dict[str, str | None]:
    """Return current user as API sees it."""
    if user.is_anon:
        result = {
            'uuid': None,
            'name': 'anon',
        }
    else:
        result = {
            'uuid': str(user.uuid),
            'name': user.name,
        }

    return result
