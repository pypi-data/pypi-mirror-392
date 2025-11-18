from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.connections_public_controller_create_idp_connection_with_csv_file_response_201 import (
    ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201,
)
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/connections/upload/csv",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    if response.status_code == 201:
        response_201 = ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201.from_dict(response.json())

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
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with file

     Create an IdP connection requires a file to complete the process

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with file

     Create an IdP connection requires a file to complete the process

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with file

     Create an IdP connection requires a file to complete the process

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]]:
    """Create an IdP connection with file

     Create an IdP connection requires a file to complete the process

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsPublicControllerCreateIdpConnectionWithCsvFileResponse201, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
