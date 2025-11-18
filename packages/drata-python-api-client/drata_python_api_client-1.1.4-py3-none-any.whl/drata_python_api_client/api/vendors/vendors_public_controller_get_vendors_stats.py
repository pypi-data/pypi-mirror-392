from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.vendors_public_controller_get_vendors_stats_exclude_scopes_type_0_item import (
    VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item,
)
from ...models.vendors_public_controller_get_vendors_stats_include_scopes_type_0_item import (
    VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item,
)
from ...models.vendors_stats_response_public_dto import VendorsStatsResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    include_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]] = UNSET,
    exclude_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_include_scopes: Union[None, Unset, list[str]]
    if isinstance(include_scopes, Unset):
        json_include_scopes = UNSET
    elif isinstance(include_scopes, list):
        json_include_scopes = []
        for include_scopes_type_0_item_data in include_scopes:
            include_scopes_type_0_item = include_scopes_type_0_item_data.value
            json_include_scopes.append(include_scopes_type_0_item)

    else:
        json_include_scopes = include_scopes
    params["includeScopes"] = json_include_scopes

    json_exclude_scopes: Union[None, Unset, list[str]]
    if isinstance(exclude_scopes, Unset):
        json_exclude_scopes = UNSET
    elif isinstance(exclude_scopes, list):
        json_exclude_scopes = []
        for exclude_scopes_type_0_item_data in exclude_scopes:
            exclude_scopes_type_0_item = exclude_scopes_type_0_item_data.value
            json_exclude_scopes.append(exclude_scopes_type_0_item)

    else:
        json_exclude_scopes = exclude_scopes
    params["excludeScopes"] = json_exclude_scopes

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/vendors/stats",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = VendorsStatsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    include_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]] = UNSET,
    exclude_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    """Get vendors statistics

     Get vendors stats given inclusion and exclusion arrays

    Args:
        include_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]]):  Example:
            ['reminder', 'passwordPolicy'].
        exclude_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]]):  Example:
            ['businessUnits', 'passwordPolicy'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        include_scopes=include_scopes,
        exclude_scopes=exclude_scopes,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    include_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]] = UNSET,
    exclude_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    """Get vendors statistics

     Get vendors stats given inclusion and exclusion arrays

    Args:
        include_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]]):  Example:
            ['reminder', 'passwordPolicy'].
        exclude_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]]):  Example:
            ['businessUnits', 'passwordPolicy'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        include_scopes=include_scopes,
        exclude_scopes=exclude_scopes,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    include_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]] = UNSET,
    exclude_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    """Get vendors statistics

     Get vendors stats given inclusion and exclusion arrays

    Args:
        include_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]]):  Example:
            ['reminder', 'passwordPolicy'].
        exclude_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]]):  Example:
            ['businessUnits', 'passwordPolicy'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        include_scopes=include_scopes,
        exclude_scopes=exclude_scopes,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    include_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]] = UNSET,
    exclude_scopes: Union[None, Unset, list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]]:
    """Get vendors statistics

     Get vendors stats given inclusion and exclusion arrays

    Args:
        include_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsIncludeScopesType0Item]]):  Example:
            ['reminder', 'passwordPolicy'].
        exclude_scopes (Union[None, Unset,
            list[VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item]]):  Example:
            ['businessUnits', 'passwordPolicy'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsStatsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            include_scopes=include_scopes,
            exclude_scopes=exclude_scopes,
        )
    ).parsed
