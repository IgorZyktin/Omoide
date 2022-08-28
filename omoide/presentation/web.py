# -*- coding: utf-8 -*-
"""Internet related tools.
"""
import http
from typing import NoReturn
from typing import Optional
from typing import Type

from fastapi import HTTPException

from omoide.domain import errors

CODES_TO_ERRORS: dict[int, list[Type[errors.Error]]] = {
    # not supposed to be used, but just in case
    http.HTTPStatus.INTERNAL_SERVER_ERROR: [
        errors.Error,
    ],

    http.HTTPStatus.BAD_REQUEST: [
        errors.NoUUID,
    ],

    http.HTTPStatus.NOT_FOUND: [
        errors.ItemDoesNotExist,
        errors.EXIFDoesNotExist,
        errors.UserDoesNotExist,
        errors.MediaDoesNotExist,
    ],

    http.HTTPStatus.FORBIDDEN: [
        errors.ItemRequiresAccess,
        errors.ItemNoDeleteForRoot,
        errors.ItemModificationByAnon,
    ]
}

ERROR_TO_CODE_MAP: dict[Type[errors.Error], int] = {
    error: code
    for code, errors in CODES_TO_ERRORS.items()
    for error in errors
}


def get_corresponding_error_code(error: errors.Error) -> int:
    """Return HTTP code that corresponds to this error."""
    return ERROR_TO_CODE_MAP.get(
        type(error),
        http.HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def safe_template(template, **kwargs) -> str:
    """Try converting error as correct as possible."""
    message = template

    for kev, value in kwargs.items():
        try:
            message = message.replace('{' + str(kev) + '}', str(value))
        except KeyError:
            pass

    return message


def raise_from_error(
        error: errors.Error,
        language: Optional[str] = None,
) -> NoReturn:
    """Cast domain level Error into HTTP response."""
    code = get_corresponding_error_code(error)

    # TODO - add actual language so errors could be translated
    assert language is None

    try:
        message = error.template.format(**error.kwargs)
    except KeyError as exc:
        print(exc)  # TODO: replace with logger call
        message = safe_template(error.template, **error.kwargs)

    raise HTTPException(status_code=code, detail=message)
