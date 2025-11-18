from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.risk_library_public_controller_get_risks_library_list_risk_filter import (
    RiskLibraryPublicControllerGetRisksLibraryListRiskFilter,
)
from ...models.risk_library_public_controller_get_risks_library_list_sort import (
    RiskLibraryPublicControllerGetRisksLibraryListSort,
)
from ...models.risk_library_public_controller_get_risks_library_list_sort_dir import (
    RiskLibraryPublicControllerGetRisksLibraryListSortDir,
)
from ...models.risks_library_paginated_response_public_dto import RisksLibraryPaginatedResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort] = UNSET,
    sort_dir: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter] = UNSET,
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

    params["q"] = q

    json_categories_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(categories_ids, Unset):
        json_categories_ids = categories_ids

    params["categoriesIds"] = json_categories_ids

    json_risk_filter: Union[Unset, str] = UNSET
    if not isinstance(risk_filter, Unset):
        json_risk_filter = risk_filter.value

    params["riskFilter"] = json_risk_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/risk-library",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = RisksLibraryPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
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
    sort: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort] = UNSET,
    sort_dir: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
    """Find library risks by search terms and filters

     List all risks in library

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort]):  Example: ID.
        sort_dir (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir]):  Example:
            ASC.
        q (Union[Unset, str]):
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter]):
            Example: NEEDS_ATTENTION.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        categories_ids=categories_ids,
        risk_filter=risk_filter,
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
    sort: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort] = UNSET,
    sort_dir: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
    """Find library risks by search terms and filters

     List all risks in library

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort]):  Example: ID.
        sort_dir (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir]):  Example:
            ASC.
        q (Union[Unset, str]):
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter]):
            Example: NEEDS_ATTENTION.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        categories_ids=categories_ids,
        risk_filter=risk_filter,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort] = UNSET,
    sort_dir: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
    """Find library risks by search terms and filters

     List all risks in library

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort]):  Example: ID.
        sort_dir (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir]):  Example:
            ASC.
        q (Union[Unset, str]):
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter]):
            Example: NEEDS_ATTENTION.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        categories_ids=categories_ids,
        risk_filter=risk_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort] = UNSET,
    sort_dir: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]]:
    """Find library risks by search terms and filters

     List all risks in library

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSort]):  Example: ID.
        sort_dir (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListSortDir]):  Example:
            ASC.
        q (Union[Unset, str]):
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskLibraryPublicControllerGetRisksLibraryListRiskFilter]):
            Example: NEEDS_ATTENTION.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksLibraryPaginatedResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            sort=sort,
            sort_dir=sort_dir,
            q=q,
            categories_ids=categories_ids,
            risk_filter=risk_filter,
        )
    ).parsed
