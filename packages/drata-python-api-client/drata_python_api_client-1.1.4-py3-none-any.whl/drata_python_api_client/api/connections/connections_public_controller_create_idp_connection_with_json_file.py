from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.connections_public_controller_create_idp_connection_with_json_file_response_201 import (
    ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201,
)
from ...models.create_connection_json_idp_request_public_dto import CreateConnectionJsonIdpRequestPublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import Response


def _get_kwargs(
    *,
    body: CreateConnectionJsonIdpRequestPublicDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/connections/upload/json",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    if response.status_code == 201:
        response_201 = ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201.from_dict(response.json())

        return response_201
    if response.status_code == 401:
        response_401 = ExceptionResponseDto.from_dict(response.json())

        return response_401
    if response.status_code == 402:
        response_402 = ExceptionResponseDto.from_dict(response.json())

        return response_402
    if response.status_code == 403:
        response_403 = ExceptionResponseDto.from_dict(response.json())

        return response_403
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
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateConnectionJsonIdpRequestPublicDto,
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with personnel list

     Create an IdP connection that requires personnel list to complete the process

    Args:
        body (CreateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CreateConnectionJsonIdpRequestPublicDto,
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with personnel list

     Create an IdP connection that requires personnel list to complete the process

    Args:
        body (CreateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateConnectionJsonIdpRequestPublicDto,
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with personnel list

     Create an IdP connection that requires personnel list to complete the process

    Args:
        body (CreateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateConnectionJsonIdpRequestPublicDto,
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with personnel list

     Create an IdP connection that requires personnel list to complete the process

    Args:
        body (CreateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerCreateIdpConnectionWithJsonFileResponse201, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
