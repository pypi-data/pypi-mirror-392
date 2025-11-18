from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.trust_center_public_controller_get_trust_center_requests_sort_dir import (
    TrustCenterPublicControllerGetTrustCenterRequestsSortDir,
)
from ...models.trust_center_public_controller_get_trust_center_requests_status import (
    TrustCenterPublicControllerGetTrustCenterRequestsStatus,
)
from ...models.trust_center_requests_response_public_dto import TrustCenterRequestsResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort_dir: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    status: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sortDir"] = json_sort_dir

    params["q"] = q

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/trust-center/requests",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = TrustCenterRequestsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
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
    sort_dir: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    status: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
    r"""Get trust center access requests

     This endpoint returns requests of all statuses except \"pending\" by default

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort_dir (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir]):
            Example: ASC.
        q (Union[Unset, str]):  Example: Drata.
        status (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus]):  Example:
            APPROVED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort_dir=sort_dir,
        q=q,
        status=status,
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
    sort_dir: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    status: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
    r"""Get trust center access requests

     This endpoint returns requests of all statuses except \"pending\" by default

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort_dir (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir]):
            Example: ASC.
        q (Union[Unset, str]):  Example: Drata.
        status (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus]):  Example:
            APPROVED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        sort_dir=sort_dir,
        q=q,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort_dir: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    status: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
    r"""Get trust center access requests

     This endpoint returns requests of all statuses except \"pending\" by default

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort_dir (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir]):
            Example: ASC.
        q (Union[Unset, str]):  Example: Drata.
        status (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus]):  Example:
            APPROVED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort_dir=sort_dir,
        q=q,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort_dir: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    status: Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]]:
    r"""Get trust center access requests

     This endpoint returns requests of all statuses except \"pending\" by default

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort_dir (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsSortDir]):
            Example: ASC.
        q (Union[Unset, str]):  Example: Drata.
        status (Union[Unset, TrustCenterPublicControllerGetTrustCenterRequestsStatus]):  Example:
            APPROVED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, TrustCenterRequestsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            sort_dir=sort_dir,
            q=q,
            status=status,
        )
    ).parsed
