from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.control_owners_response_public_dto import ControlOwnersResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: float,
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    params["frameworkSlug"] = framework_slug

    json_include_user_ids: Union[None, Unset, list[float]]
    if isinstance(include_user_ids, Unset):
        json_include_user_ids = UNSET
    elif isinstance(include_user_ids, list):
        json_include_user_ids = include_user_ids

    else:
        json_include_user_ids = include_user_ids
    params["includeUserIds[]"] = json_include_user_ids

    json_exclude_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(exclude_ids, Unset):
        json_exclude_ids = exclude_ids

    params["excludeIds"] = json_exclude_ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/controls/{id}/owners",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = ControlOwnersResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
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
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
) -> Response[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find control owners by control id

     Get control owners for a control

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        framework_slug (Union[Unset, str]):  Example: soc2.
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_ids (Union[Unset, list[float]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        include_user_ids=include_user_ids,
        exclude_ids=exclude_ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
) -> Optional[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find control owners by control id

     Get control owners for a control

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        framework_slug (Union[Unset, str]):  Example: soc2.
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_ids (Union[Unset, list[float]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        id=id,
        client=client,
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        include_user_ids=include_user_ids,
        exclude_ids=exclude_ids,
    ).parsed


async def asyncio_detailed(
    id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
) -> Response[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find control owners by control id

     Get control owners for a control

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        framework_slug (Union[Unset, str]):  Example: soc2.
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_ids (Union[Unset, list[float]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        include_user_ids=include_user_ids,
        exclude_ids=exclude_ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    include_user_ids: Union[None, Unset, list[float]] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
) -> Optional[Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find control owners by control id

     Get control owners for a control

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        framework_slug (Union[Unset, str]):  Example: soc2.
        include_user_ids (Union[None, Unset, list[float]]):  Example: [1, 2, 3].
        exclude_ids (Union[Unset, list[float]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlOwnersResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            page=page,
            limit=limit,
            q=q,
            framework_slug=framework_slug,
            include_user_ids=include_user_ids,
            exclude_ids=exclude_ids,
        )
    ).parsed
