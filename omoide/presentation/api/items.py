# -*- coding: utf-8 -*-
"""Item related API operations.
"""
import http
from uuid import UUID

from fastapi import HTTPException, Response, Depends, APIRouter, Request

from omoide import domain, use_cases
from omoide.domain import exceptions
from omoide.presentation import dependencies as dep

router = APIRouter(prefix='/api/items')


@router.post('', status_code=http.HTTPStatus.CREATED)
async def api_create_item(
        request: Request,
        response: Response,
        payload: domain.CreateItemIn,
        user: domain.User = Depends(dep.get_current_user),
        use_case: use_cases.CreateItemUseCase = Depends(
            dep.create_item_use_case),
):
    """Create item."""
    try:
        uuid = await use_case.execute(user, payload)
    except exceptions.Forbidden as exc:
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                            detail=str(exc))

    response.headers['Location'] = request.url_for('api_get_item', uuid=uuid)

    if payload.is_collection:
        url = request.url_for('browse', uuid=uuid)
    else:
        url = request.url_for('preview', uuid=uuid)

    return {'url': url}


@router.get('/{uuid}')
async def api_get_item(
        uuid: UUID,
        user: domain.User = Depends(dep.get_current_user),
        use_case: use_cases.ReadItemUseCase = Depends(
            dep.read_item_use_case),
):
    """Get item."""
    try:
        item = await use_case.execute(user, uuid)
    except exceptions.NotFound as exc:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND,
                            detail=str(exc))
    except exceptions.Forbidden as exc:
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                            detail=str(exc))
    return item.dict()


@router.delete('/{uuid}', status_code=http.HTTPStatus.NO_CONTENT)
async def api_delete_item(
        uuid: UUID,
        user: domain.User = Depends(dep.get_current_user),
        use_case: use_cases.DeleteItemUseCase = Depends(
            dep.delete_item_use_case),
):
    """Delete item."""
    try:
        await use_case.execute(user, uuid)
    except exceptions.NotFound as exc:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND,
                            detail=str(exc))
    except exceptions.Forbidden as exc:
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                            detail=str(exc))
