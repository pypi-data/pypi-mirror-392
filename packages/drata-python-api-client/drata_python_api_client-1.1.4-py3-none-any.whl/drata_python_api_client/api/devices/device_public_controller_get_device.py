from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.device_public_controller_get_device_expand_item import DevicePublicControllerGetDeviceExpandItem
from ...models.device_response_id_public_dto import DeviceResponseIdPublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    device_id: float,
    *,
    expand: Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_expand: Union[Unset, list[str]] = UNSET
    if not isinstance(expand, Unset):
        json_expand = []
        for expand_item_data in expand:
            expand_item = expand_item_data.value
            json_expand.append(expand_item)

    params["expand[]"] = json_expand

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/devices/{device_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = DeviceResponseIdPublicDto.from_dict(response.json())

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
) -> Response[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    device_id: float,
    *,
    client: AuthenticatedClient,
    expand: Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]] = UNSET,
) -> Response[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a specific device

    Args:
        device_id (float):
        expand (Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]]):  Example:
            COMPLIANCE_CHECKS.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        expand=expand,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    device_id: float,
    *,
    client: AuthenticatedClient,
    expand: Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]] = UNSET,
) -> Optional[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a specific device

    Args:
        device_id (float):
        expand (Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]]):  Example:
            COMPLIANCE_CHECKS.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        device_id=device_id,
        client=client,
        expand=expand,
    ).parsed


async def asyncio_detailed(
    device_id: float,
    *,
    client: AuthenticatedClient,
    expand: Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]] = UNSET,
) -> Response[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a specific device

    Args:
        device_id (float):
        expand (Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]]):  Example:
            COMPLIANCE_CHECKS.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        expand=expand,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    device_id: float,
    *,
    client: AuthenticatedClient,
    expand: Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]] = UNSET,
) -> Optional[Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get a specific device

    Args:
        device_id (float):
        expand (Union[Unset, list[DevicePublicControllerGetDeviceExpandItem]]):  Example:
            COMPLIANCE_CHECKS.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceResponseIdPublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            device_id=device_id,
            client=client,
            expand=expand,
        )
    ).parsed
