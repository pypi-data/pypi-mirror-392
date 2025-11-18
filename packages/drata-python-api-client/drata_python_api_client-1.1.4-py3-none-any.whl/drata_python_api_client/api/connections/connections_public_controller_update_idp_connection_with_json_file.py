from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.connections_public_controller_update_idp_connection_with_json_file_response_200 import (
    ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200,
)
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.update_connection_json_idp_request_public_dto import UpdateConnectionJsonIdpRequestPublicDto
from ...types import Response


def _get_kwargs(
    id: float,
    *,
    body: UpdateConnectionJsonIdpRequestPublicDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/connections/{id}/upload/json",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
    if response.status_code == 200:
        response_200 = ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200.from_dict(response.json())

        return response_200
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
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
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
    body: UpdateConnectionJsonIdpRequestPublicDto,
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
    """Update an IdP connection with personnel list

     Update an IdP connection that requires personnel list to complete the process

    Args:
        id (float):
        body (UpdateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]
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
    body: UpdateConnectionJsonIdpRequestPublicDto,
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
    """Update an IdP connection with personnel list

     Update an IdP connection that requires personnel list to complete the process

    Args:
        id (float):
        body (UpdateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]
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
    body: UpdateConnectionJsonIdpRequestPublicDto,
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
    """Update an IdP connection with personnel list

     Update an IdP connection that requires personnel list to complete the process

    Args:
        id (float):
        body (UpdateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]
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
    body: UpdateConnectionJsonIdpRequestPublicDto,
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]]:
    """Update an IdP connection with personnel list

     Update an IdP connection that requires personnel list to complete the process

    Args:
        id (float):
        body (UpdateConnectionJsonIdpRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerUpdateIdpConnectionWithJsonFileResponse200, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
