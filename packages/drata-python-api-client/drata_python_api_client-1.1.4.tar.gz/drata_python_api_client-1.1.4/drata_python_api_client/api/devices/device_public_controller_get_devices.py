from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.device_public_controller_get_devices_expand_item import DevicePublicControllerGetDevicesExpandItem
from ...models.device_public_controller_get_devices_source_type import DevicePublicControllerGetDevicesSourceType
from ...models.devices_paginated_response_public_dto import DevicesPaginatedResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    external_id: Union[Unset, str] = UNSET,
    expand: Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]] = UNSET,
    mac_address: Union[Unset, str] = UNSET,
    serial_number: Union[Unset, str] = UNSET,
    source_type: Union[Unset, DevicePublicControllerGetDevicesSourceType] = UNSET,
    personnel_id: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["externalId"] = external_id

    json_expand: Union[Unset, list[str]] = UNSET
    if not isinstance(expand, Unset):
        json_expand = []
        for expand_item_data in expand:
            expand_item = expand_item_data.value
            json_expand.append(expand_item)

    params["expand[]"] = json_expand

    params["macAddress"] = mac_address

    params["serialNumber"] = serial_number

    json_source_type: Union[Unset, str] = UNSET
    if not isinstance(source_type, Unset):
        json_source_type = source_type.value

    params["sourceType"] = json_source_type

    params["personnelId"] = personnel_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/devices",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = DevicesPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    external_id: Union[Unset, str] = UNSET,
    expand: Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]] = UNSET,
    mac_address: Union[Unset, str] = UNSET,
    serial_number: Union[Unset, str] = UNSET,
    source_type: Union[Unset, DevicePublicControllerGetDevicesSourceType] = UNSET,
    personnel_id: Union[Unset, float] = UNSET,
) -> Response[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a list of devices

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        external_id (Union[Unset, str]):
        expand (Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]]):  Example:
            COMPLIANCE_CHECKS.
        mac_address (Union[Unset, str]):  Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        serial_number (Union[Unset, str]):  Example: NKRTSPY456.
        source_type (Union[Unset, DevicePublicControllerGetDevicesSourceType]):  Example: AGENT.
        personnel_id (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        external_id=external_id,
        expand=expand,
        mac_address=mac_address,
        serial_number=serial_number,
        source_type=source_type,
        personnel_id=personnel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    external_id: Union[Unset, str] = UNSET,
    expand: Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]] = UNSET,
    mac_address: Union[Unset, str] = UNSET,
    serial_number: Union[Unset, str] = UNSET,
    source_type: Union[Unset, DevicePublicControllerGetDevicesSourceType] = UNSET,
    personnel_id: Union[Unset, float] = UNSET,
) -> Optional[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a list of devices

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        external_id (Union[Unset, str]):
        expand (Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]]):  Example:
            COMPLIANCE_CHECKS.
        mac_address (Union[Unset, str]):  Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        serial_number (Union[Unset, str]):  Example: NKRTSPY456.
        source_type (Union[Unset, DevicePublicControllerGetDevicesSourceType]):  Example: AGENT.
        personnel_id (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        external_id=external_id,
        expand=expand,
        mac_address=mac_address,
        serial_number=serial_number,
        source_type=source_type,
        personnel_id=personnel_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    external_id: Union[Unset, str] = UNSET,
    expand: Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]] = UNSET,
    mac_address: Union[Unset, str] = UNSET,
    serial_number: Union[Unset, str] = UNSET,
    source_type: Union[Unset, DevicePublicControllerGetDevicesSourceType] = UNSET,
    personnel_id: Union[Unset, float] = UNSET,
) -> Response[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a list of devices

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        external_id (Union[Unset, str]):
        expand (Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]]):  Example:
            COMPLIANCE_CHECKS.
        mac_address (Union[Unset, str]):  Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        serial_number (Union[Unset, str]):  Example: NKRTSPY456.
        source_type (Union[Unset, DevicePublicControllerGetDevicesSourceType]):  Example: AGENT.
        personnel_id (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        external_id=external_id,
        expand=expand,
        mac_address=mac_address,
        serial_number=serial_number,
        source_type=source_type,
        personnel_id=personnel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    external_id: Union[Unset, str] = UNSET,
    expand: Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]] = UNSET,
    mac_address: Union[Unset, str] = UNSET,
    serial_number: Union[Unset, str] = UNSET,
    source_type: Union[Unset, DevicePublicControllerGetDevicesSourceType] = UNSET,
    personnel_id: Union[Unset, float] = UNSET,
) -> Optional[Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a list of devices

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        external_id (Union[Unset, str]):
        expand (Union[Unset, list[DevicePublicControllerGetDevicesExpandItem]]):  Example:
            COMPLIANCE_CHECKS.
        mac_address (Union[Unset, str]):  Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        serial_number (Union[Unset, str]):  Example: NKRTSPY456.
        source_type (Union[Unset, DevicePublicControllerGetDevicesSourceType]):  Example: AGENT.
        personnel_id (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DevicesPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            external_id=external_id,
            expand=expand,
            mac_address=mac_address,
            serial_number=serial_number,
            source_type=source_type,
            personnel_id=personnel_id,
        )
    ).parsed
