from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.user_identity_version_control_response_public_dto import UserIdentityVersionControlResponsePublicDto
from ...models.user_identity_version_control_service_status_request_public_dto import (
    UserIdentityVersionControlServiceStatusRequestPublicDto,
)
from ...types import Response


def _get_kwargs(
    id: float,
    *,
    body: UserIdentityVersionControlServiceStatusRequestPublicDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/user-identities/version-control/{id}/service-account",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = UserIdentityVersionControlResponsePublicDto.from_dict(response.json())

        return response_200
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
    if response.status_code == 500:
        response_500 = ExceptionResponseDto.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
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
    body: UserIdentityVersionControlServiceStatusRequestPublicDto,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
    """Update version control user identity to a service account

     Update the target version control user identity to a service account

    Args:
        id (float):
        body (UserIdentityVersionControlServiceStatusRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]
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
    body: UserIdentityVersionControlServiceStatusRequestPublicDto,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
    """Update version control user identity to a service account

     Update the target version control user identity to a service account

    Args:
        id (float):
        body (UserIdentityVersionControlServiceStatusRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]
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
    body: UserIdentityVersionControlServiceStatusRequestPublicDto,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
    """Update version control user identity to a service account

     Update the target version control user identity to a service account

    Args:
        id (float):
        body (UserIdentityVersionControlServiceStatusRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]
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
    body: UserIdentityVersionControlServiceStatusRequestPublicDto,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]]:
    """Update version control user identity to a service account

     Update the target version control user identity to a service account

    Args:
        id (float):
        body (UserIdentityVersionControlServiceStatusRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserIdentityVersionControlResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
