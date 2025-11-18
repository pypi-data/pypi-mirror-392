from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.users_public_controller_list_users_exclude_roles_type_0_item import (
    UsersPublicControllerListUsersExcludeRolesType0Item,
)
from ...models.users_public_controller_list_users_roles_item import UsersPublicControllerListUsersRolesItem
from ...models.users_response_public_dto import UsersResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    roles: Union[Unset, list[UsersPublicControllerListUsersRolesItem]] = UNSET,
    exclude_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_roles: Union[None, Unset, list[UsersPublicControllerListUsersExcludeRolesType0Item]] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_roles: Union[Unset, list[str]] = UNSET
    if not isinstance(roles, Unset):
        json_roles = []
        for roles_item_data in roles:
            roles_item = roles_item_data.value
            json_roles.append(roles_item)

    params["roles[]"] = json_roles

    json_exclude_user_ids: Union[None, Unset, list[float]]
    if isinstance(exclude_user_ids, Unset):
        json_exclude_user_ids = UNSET
    elif isinstance(exclude_user_ids, list):
        json_exclude_user_ids = exclude_user_ids

    else:
        json_exclude_user_ids = exclude_user_ids
    params["excludeUserIds[]"] = json_exclude_user_ids

    json_exclude_roles: Union[None, Unset, list[str]]
    if isinstance(exclude_roles, Unset):
        json_exclude_roles = UNSET
    elif isinstance(exclude_roles, list):
        json_exclude_roles = []
        for exclude_roles_type_0_item_data in exclude_roles:
            exclude_roles_type_0_item = exclude_roles_type_0_item_data.value
            json_exclude_roles.append(exclude_roles_type_0_item)

    else:
        json_exclude_roles = exclude_roles
    params["excludeRoles[]"] = json_exclude_roles

    json_include_user_ids: Union[None, Unset, list[float]]
    if isinstance(include_user_ids, Unset):
        json_include_user_ids = UNSET
    elif isinstance(include_user_ids, list):
        json_include_user_ids = include_user_ids

    else:
        json_include_user_ids = include_user_ids
    params["includeUserIds[]"] = json_include_user_ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = UsersResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
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
    q: Union[Unset, str] = UNSET,
    roles: Union[Unset, list[UsersPublicControllerListUsersRolesItem]] = UNSET,
    exclude_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_roles: Union[None, Unset, list[UsersPublicControllerListUsersExcludeRolesType0Item]] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
    """Find users by search terms and filters

     List users given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        roles (Union[Unset, list[UsersPublicControllerListUsersRolesItem]]):  Example: ['ADMIN',
            'TECHGOV'].
        exclude_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_roles (Union[None, Unset,
            list[UsersPublicControllerListUsersExcludeRolesType0Item]]):  Example:
            ['WORKSPACE_ADMINISTRATOR', 'TECHGOV'].
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        roles=roles,
        exclude_user_ids=exclude_user_ids,
        exclude_roles=exclude_roles,
        include_user_ids=include_user_ids,
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
    q: Union[Unset, str] = UNSET,
    roles: Union[Unset, list[UsersPublicControllerListUsersRolesItem]] = UNSET,
    exclude_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_roles: Union[None, Unset, list[UsersPublicControllerListUsersExcludeRolesType0Item]] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
    """Find users by search terms and filters

     List users given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        roles (Union[Unset, list[UsersPublicControllerListUsersRolesItem]]):  Example: ['ADMIN',
            'TECHGOV'].
        exclude_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_roles (Union[None, Unset,
            list[UsersPublicControllerListUsersExcludeRolesType0Item]]):  Example:
            ['WORKSPACE_ADMINISTRATOR', 'TECHGOV'].
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        roles=roles,
        exclude_user_ids=exclude_user_ids,
        exclude_roles=exclude_roles,
        include_user_ids=include_user_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    roles: Union[Unset, list[UsersPublicControllerListUsersRolesItem]] = UNSET,
    exclude_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_roles: Union[None, Unset, list[UsersPublicControllerListUsersExcludeRolesType0Item]] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
    """Find users by search terms and filters

     List users given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        roles (Union[Unset, list[UsersPublicControllerListUsersRolesItem]]):  Example: ['ADMIN',
            'TECHGOV'].
        exclude_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_roles (Union[None, Unset,
            list[UsersPublicControllerListUsersExcludeRolesType0Item]]):  Example:
            ['WORKSPACE_ADMINISTRATOR', 'TECHGOV'].
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        roles=roles,
        exclude_user_ids=exclude_user_ids,
        exclude_roles=exclude_roles,
        include_user_ids=include_user_ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    roles: Union[Unset, list[UsersPublicControllerListUsersRolesItem]] = UNSET,
    exclude_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_roles: Union[None, Unset, list[UsersPublicControllerListUsersExcludeRolesType0Item]] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]]:
    """Find users by search terms and filters

     List users given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        roles (Union[Unset, list[UsersPublicControllerListUsersRolesItem]]):  Example: ['ADMIN',
            'TECHGOV'].
        exclude_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_roles (Union[None, Unset,
            list[UsersPublicControllerListUsersExcludeRolesType0Item]]):  Example:
            ['WORKSPACE_ADMINISTRATOR', 'TECHGOV'].
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UsersResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            roles=roles,
            exclude_user_ids=exclude_user_ids,
            exclude_roles=exclude_roles,
            include_user_ids=include_user_ids,
        )
    ).parsed
