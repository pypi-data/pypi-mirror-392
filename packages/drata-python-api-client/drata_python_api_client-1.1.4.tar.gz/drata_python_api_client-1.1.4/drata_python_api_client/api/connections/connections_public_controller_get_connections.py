from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.connections_compact_response_public_dto import ConnectionsCompactResponsePublicDto
from ...models.connections_public_controller_get_connections_provider_types_item import (
    ConnectionsPublicControllerGetConnectionsProviderTypesItem,
)
from ...models.connections_public_controller_get_connections_sort import ConnectionsPublicControllerGetConnectionsSort
from ...models.connections_public_controller_get_connections_sort_dir import (
    ConnectionsPublicControllerGetConnectionsSortDir,
)
from ...models.connections_public_controller_get_connections_state import ConnectionsPublicControllerGetConnectionsState
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, ConnectionsPublicControllerGetConnectionsSort] = UNSET,
    sort_dir: Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir] = UNSET,
    provider_types: Union[Unset, list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]] = UNSET,
    state: Union[Unset, ConnectionsPublicControllerGetConnectionsState] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sortDir"] = json_sort_dir

    json_provider_types: Union[Unset, list[str]] = UNSET
    if not isinstance(provider_types, Unset):
        json_provider_types = []
        for provider_types_item_data in provider_types:
            provider_types_item = provider_types_item_data.value
            json_provider_types.append(provider_types_item)

    params["providerTypes"] = json_provider_types

    json_state: Union[Unset, str] = UNSET
    if not isinstance(state, Unset):
        json_state = state.value

    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/connections",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
    if response.status_code == 200:
        response_200 = ConnectionsCompactResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
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
    sort: Union[Unset, ConnectionsPublicControllerGetConnectionsSort] = UNSET,
    sort_dir: Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir] = UNSET,
    provider_types: Union[Unset, list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]] = UNSET,
    state: Union[Unset, ConnectionsPublicControllerGetConnectionsState] = UNSET,
) -> Response[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
    """List managed connections given the provided filters

     Find managed connections by provider type and current state

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, ConnectionsPublicControllerGetConnectionsSort]):
        sort_dir (Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir]):
        provider_types (Union[Unset,
            list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]]):
        state (Union[Unset, ConnectionsPublicControllerGetConnectionsState]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        provider_types=provider_types,
        state=state,
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
    sort: Union[Unset, ConnectionsPublicControllerGetConnectionsSort] = UNSET,
    sort_dir: Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir] = UNSET,
    provider_types: Union[Unset, list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]] = UNSET,
    state: Union[Unset, ConnectionsPublicControllerGetConnectionsState] = UNSET,
) -> Optional[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
    """List managed connections given the provided filters

     Find managed connections by provider type and current state

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, ConnectionsPublicControllerGetConnectionsSort]):
        sort_dir (Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir]):
        provider_types (Union[Unset,
            list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]]):
        state (Union[Unset, ConnectionsPublicControllerGetConnectionsState]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        provider_types=provider_types,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, ConnectionsPublicControllerGetConnectionsSort] = UNSET,
    sort_dir: Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir] = UNSET,
    provider_types: Union[Unset, list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]] = UNSET,
    state: Union[Unset, ConnectionsPublicControllerGetConnectionsState] = UNSET,
) -> Response[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
    """List managed connections given the provided filters

     Find managed connections by provider type and current state

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, ConnectionsPublicControllerGetConnectionsSort]):
        sort_dir (Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir]):
        provider_types (Union[Unset,
            list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]]):
        state (Union[Unset, ConnectionsPublicControllerGetConnectionsState]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        provider_types=provider_types,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, ConnectionsPublicControllerGetConnectionsSort] = UNSET,
    sort_dir: Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir] = UNSET,
    provider_types: Union[Unset, list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]] = UNSET,
    state: Union[Unset, ConnectionsPublicControllerGetConnectionsState] = UNSET,
) -> Optional[Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]]:
    """List managed connections given the provided filters

     Find managed connections by provider type and current state

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, ConnectionsPublicControllerGetConnectionsSort]):
        sort_dir (Union[Unset, ConnectionsPublicControllerGetConnectionsSortDir]):
        provider_types (Union[Unset,
            list[ConnectionsPublicControllerGetConnectionsProviderTypesItem]]):
        state (Union[Unset, ConnectionsPublicControllerGetConnectionsState]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsCompactResponsePublicDto, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            sort=sort,
            sort_dir=sort_dir,
            provider_types=provider_types,
            state=state,
        )
    ).parsed
