from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.create_device_request_public_dto import CreateDeviceRequestPublicDto
from ...models.device_response_v11_public_dto import DeviceResponseV11PublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import Response


def _get_kwargs(
    connection_id: float,
    *,
    body: CreateDeviceRequestPublicDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/custom-connections/{connection_id}/devices",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 201:
        response_201 = DeviceResponseV11PublicDto.from_dict(response.json())

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
) -> Response[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: float,
    *,
    client: AuthenticatedClient,
    body: CreateDeviceRequestPublicDto,
) -> Response[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Create a new device or update an existing device for a custom connection


    🧪 **BETA:** Create a new device or update an existing device for a custom connection.

    An existing device is searched for based upon matching one or more of these supplied properties in
    the request payload:
    * `serialNumber`
    * `macAddress`
    * `externalId`

    If an existing device is found, the existing device is updated.
    Otherwise a new device is created.


    Args:
        connection_id (float):
        body (CreateDeviceRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: float,
    *,
    client: AuthenticatedClient,
    body: CreateDeviceRequestPublicDto,
) -> Optional[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Create a new device or update an existing device for a custom connection


    🧪 **BETA:** Create a new device or update an existing device for a custom connection.

    An existing device is searched for based upon matching one or more of these supplied properties in
    the request payload:
    * `serialNumber`
    * `macAddress`
    * `externalId`

    If an existing device is found, the existing device is updated.
    Otherwise a new device is created.


    Args:
        connection_id (float):
        body (CreateDeviceRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        connection_id=connection_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    connection_id: float,
    *,
    client: AuthenticatedClient,
    body: CreateDeviceRequestPublicDto,
) -> Response[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Create a new device or update an existing device for a custom connection


    🧪 **BETA:** Create a new device or update an existing device for a custom connection.

    An existing device is searched for based upon matching one or more of these supplied properties in
    the request payload:
    * `serialNumber`
    * `macAddress`
    * `externalId`

    If an existing device is found, the existing device is updated.
    Otherwise a new device is created.


    Args:
        connection_id (float):
        body (CreateDeviceRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: float,
    *,
    client: AuthenticatedClient,
    body: CreateDeviceRequestPublicDto,
) -> Optional[Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Create a new device or update an existing device for a custom connection


    🧪 **BETA:** Create a new device or update an existing device for a custom connection.

    An existing device is searched for based upon matching one or more of these supplied properties in
    the request payload:
    * `serialNumber`
    * `macAddress`
    * `externalId`

    If an existing device is found, the existing device is updated.
    Otherwise a new device is created.


    Args:
        connection_id (float):
        body (CreateDeviceRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceResponseV11PublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            client=client,
            body=body,
        )
    ).parsed
