from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.connections_public_controller_update_idp_connection_with_csv_file_response_200 import (
    ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200,
)
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import Response


def _get_kwargs(
    id: float,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/connections/{id}/upload/csv",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
    if response.status_code == 200:
        response_200 = ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200.from_dict(response.json())

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
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
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
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
    """update an IdP connection with file

     Update an IdP connection that requires a file to complete the process

    Args:
        id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: float,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
    """update an IdP connection with file

     Update an IdP connection that requires a file to complete the process

    Args:
        id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: float,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
    """update an IdP connection with file

     Update an IdP connection that requires a file to complete the process

    Args:
        id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: float,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]]:
    """update an IdP connection with file

     Update an IdP connection that requires a file to complete the process

    Args:
        id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerUpdateIdpConnectionWithCsvFileResponse200, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
