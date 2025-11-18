from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.user_document_request_public_dto import UserDocumentRequestPublicDto
from ...models.user_document_response_public_dto import UserDocumentResponsePublicDto
from ...types import Response


def _get_kwargs(
    id: float,
    *,
    body: Union[
        UserDocumentRequestPublicDto,
        UserDocumentRequestPublicDto,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/users/{id}/documents",
    }

    if isinstance(body, UserDocumentRequestPublicDto):
        _files_body = body.to_multipart()

        _kwargs["files"] = _files_body
        headers["Content-Type"] = "multipart/form-data"
    if isinstance(body, UserDocumentRequestPublicDto):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    if response.status_code == 201:
        response_201 = UserDocumentResponsePublicDto.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = ExceptionResponseDto.from_dict(response.json())

        return response_401
    if response.status_code == 402:
        response_402 = ExceptionResponseDto.from_dict(response.json())

        return response_402
    if response.status_code == 403:
        response_403 = ExceptionResponseDto.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_404
    if response.status_code == 412:
        response_412 = ExceptionResponseDto.from_dict(response.json())

        return response_412
    if response.status_code == 413:
        response_413 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_413
    if response.status_code == 500:
        response_500 = ExceptionResponseDto.from_dict(response.json())

        return response_500
    if response.status_code == 503:
        response_503 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UserDocumentRequestPublicDto,
        UserDocumentRequestPublicDto,
    ],
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    """Upload a document for user by user id

     Upload document for user.

    Args:
        id (float):
        body (UserDocumentRequestPublicDto):
        body (UserDocumentRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UserDocumentRequestPublicDto,
        UserDocumentRequestPublicDto,
    ],
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    """Upload a document for user by user id

     Upload document for user.

    Args:
        id (float):
        body (UserDocumentRequestPublicDto):
        body (UserDocumentRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UserDocumentRequestPublicDto,
        UserDocumentRequestPublicDto,
    ],
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    """Upload a document for user by user id

     Upload document for user.

    Args:
        id (float):
        body (UserDocumentRequestPublicDto):
        body (UserDocumentRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UserDocumentRequestPublicDto,
        UserDocumentRequestPublicDto,
    ],
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]]:
    """Upload a document for user by user id

     Upload document for user.

    Args:
        id (float):
        body (UserDocumentRequestPublicDto):
        body (UserDocumentRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserDocumentResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
