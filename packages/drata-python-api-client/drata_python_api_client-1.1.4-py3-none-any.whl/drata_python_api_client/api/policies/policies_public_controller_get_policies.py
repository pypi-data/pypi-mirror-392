from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.policies_response_public_dto import PoliciesResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    has_published_version: Union[Unset, bool] = UNSET,
    has_approved_version: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    params["userId"] = user_id

    params["hasPublishedVersion"] = has_published_version

    params["hasApprovedVersion"] = has_approved_version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/policies",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = PoliciesResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
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
    user_id: Union[Unset, float] = UNSET,
    has_published_version: Union[Unset, bool] = UNSET,
    has_approved_version: Union[Unset, bool] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
    """Get policies

     Returns the list of policies and their metadata

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acceptable Use Policy.
        user_id (Union[Unset, float]):  Example: 1.
        has_published_version (Union[Unset, bool]):
        has_approved_version (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        user_id=user_id,
        has_published_version=has_published_version,
        has_approved_version=has_approved_version,
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
    user_id: Union[Unset, float] = UNSET,
    has_published_version: Union[Unset, bool] = UNSET,
    has_approved_version: Union[Unset, bool] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
    """Get policies

     Returns the list of policies and their metadata

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acceptable Use Policy.
        user_id (Union[Unset, float]):  Example: 1.
        has_published_version (Union[Unset, bool]):
        has_approved_version (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        user_id=user_id,
        has_published_version=has_published_version,
        has_approved_version=has_approved_version,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    has_published_version: Union[Unset, bool] = UNSET,
    has_approved_version: Union[Unset, bool] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
    """Get policies

     Returns the list of policies and their metadata

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acceptable Use Policy.
        user_id (Union[Unset, float]):  Example: 1.
        has_published_version (Union[Unset, bool]):
        has_approved_version (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        user_id=user_id,
        has_published_version=has_published_version,
        has_approved_version=has_approved_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    has_published_version: Union[Unset, bool] = UNSET,
    has_approved_version: Union[Unset, bool] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]]:
    """Get policies

     Returns the list of policies and their metadata

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acceptable Use Policy.
        user_id (Union[Unset, float]):  Example: 1.
        has_published_version (Union[Unset, bool]):
        has_approved_version (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, PoliciesResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            user_id=user_id,
            has_published_version=has_published_version,
            has_approved_version=has_approved_version,
        )
    ).parsed
