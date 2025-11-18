from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.risk_management_public_controller_list_risks_sort import RiskManagementPublicControllerListRisksSort
from ...models.risk_management_public_controller_list_risks_sort_dir import (
    RiskManagementPublicControllerListRisksSortDir,
)
from ...models.risk_management_public_controller_list_risks_status import RiskManagementPublicControllerListRisksStatus
from ...models.risk_management_public_controller_list_risks_treatment_plan import (
    RiskManagementPublicControllerListRisksTreatmentPlan,
)
from ...models.risks_paginated_response_public_dto import RisksPaginatedResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskManagementPublicControllerListRisksSort] = UNSET,
    sort_dir: Union[Unset, RiskManagementPublicControllerListRisksSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    applicable: Union[Unset, bool] = UNSET,
    status: Union[Unset, RiskManagementPublicControllerListRisksStatus] = UNSET,
    is_scored: Union[Unset, bool] = UNSET,
    treatment_plan: Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    needs_attention: Union[Unset, bool] = UNSET,
    impact: Union[Unset, float] = UNSET,
    likelihood: Union[Unset, float] = UNSET,
    min_score: Union[Unset, float] = UNSET,
    max_score: Union[Unset, float] = UNSET,
    vendor_id: Union[None, Unset, float] = UNSET,
    only_vendors: Union[Unset, bool] = UNSET,
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

    params["applicable"] = applicable

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["isScored"] = is_scored

    json_treatment_plan: Union[Unset, str] = UNSET
    if not isinstance(treatment_plan, Unset):
        json_treatment_plan = treatment_plan.value

    params["treatmentPlan"] = json_treatment_plan

    json_categories_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(categories_ids, Unset):
        json_categories_ids = categories_ids

    params["categoriesIds"] = json_categories_ids

    json_owners_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(owners_ids, Unset):
        json_owners_ids = owners_ids

    params["ownersIds"] = json_owners_ids

    params["needsAttention"] = needs_attention

    params["impact"] = impact

    params["likelihood"] = likelihood

    params["minScore"] = min_score

    params["maxScore"] = max_score

    json_vendor_id: Union[None, Unset, float]
    if isinstance(vendor_id, Unset):
        json_vendor_id = UNSET
    else:
        json_vendor_id = vendor_id
    params["vendorId"] = json_vendor_id

    params["onlyVendors"] = only_vendors

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/risk-management",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = RisksPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
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
    sort: Union[Unset, RiskManagementPublicControllerListRisksSort] = UNSET,
    sort_dir: Union[Unset, RiskManagementPublicControllerListRisksSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    applicable: Union[Unset, bool] = UNSET,
    status: Union[Unset, RiskManagementPublicControllerListRisksStatus] = UNSET,
    is_scored: Union[Unset, bool] = UNSET,
    treatment_plan: Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    needs_attention: Union[Unset, bool] = UNSET,
    impact: Union[Unset, float] = UNSET,
    likelihood: Union[Unset, float] = UNSET,
    min_score: Union[Unset, float] = UNSET,
    max_score: Union[Unset, float] = UNSET,
    vendor_id: Union[None, Unset, float] = UNSET,
    only_vendors: Union[Unset, bool] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
    """Find risks by search terms and filters

     List all risks

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskManagementPublicControllerListRisksSort]):  Example: ID.
        sort_dir (Union[Unset, RiskManagementPublicControllerListRisksSortDir]):  Example: ASC.
        q (Union[Unset, str]):
        applicable (Union[Unset, bool]):
        status (Union[Unset, RiskManagementPublicControllerListRisksStatus]):  Example: ACTIVE.
        is_scored (Union[Unset, bool]):
        treatment_plan (Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan]):
            Example: UNTREATED.
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        needs_attention (Union[Unset, bool]):
        impact (Union[Unset, float]):  Example: 3.
        likelihood (Union[Unset, float]):  Example: 1.
        min_score (Union[Unset, float]):  Example: 1.
        max_score (Union[Unset, float]):  Example: 1.
        vendor_id (Union[None, Unset, float]):  Example: 1.
        only_vendors (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        applicable=applicable,
        status=status,
        is_scored=is_scored,
        treatment_plan=treatment_plan,
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        needs_attention=needs_attention,
        impact=impact,
        likelihood=likelihood,
        min_score=min_score,
        max_score=max_score,
        vendor_id=vendor_id,
        only_vendors=only_vendors,
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
    sort: Union[Unset, RiskManagementPublicControllerListRisksSort] = UNSET,
    sort_dir: Union[Unset, RiskManagementPublicControllerListRisksSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    applicable: Union[Unset, bool] = UNSET,
    status: Union[Unset, RiskManagementPublicControllerListRisksStatus] = UNSET,
    is_scored: Union[Unset, bool] = UNSET,
    treatment_plan: Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    needs_attention: Union[Unset, bool] = UNSET,
    impact: Union[Unset, float] = UNSET,
    likelihood: Union[Unset, float] = UNSET,
    min_score: Union[Unset, float] = UNSET,
    max_score: Union[Unset, float] = UNSET,
    vendor_id: Union[None, Unset, float] = UNSET,
    only_vendors: Union[Unset, bool] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
    """Find risks by search terms and filters

     List all risks

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskManagementPublicControllerListRisksSort]):  Example: ID.
        sort_dir (Union[Unset, RiskManagementPublicControllerListRisksSortDir]):  Example: ASC.
        q (Union[Unset, str]):
        applicable (Union[Unset, bool]):
        status (Union[Unset, RiskManagementPublicControllerListRisksStatus]):  Example: ACTIVE.
        is_scored (Union[Unset, bool]):
        treatment_plan (Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan]):
            Example: UNTREATED.
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        needs_attention (Union[Unset, bool]):
        impact (Union[Unset, float]):  Example: 3.
        likelihood (Union[Unset, float]):  Example: 1.
        min_score (Union[Unset, float]):  Example: 1.
        max_score (Union[Unset, float]):  Example: 1.
        vendor_id (Union[None, Unset, float]):  Example: 1.
        only_vendors (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        applicable=applicable,
        status=status,
        is_scored=is_scored,
        treatment_plan=treatment_plan,
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        needs_attention=needs_attention,
        impact=impact,
        likelihood=likelihood,
        min_score=min_score,
        max_score=max_score,
        vendor_id=vendor_id,
        only_vendors=only_vendors,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskManagementPublicControllerListRisksSort] = UNSET,
    sort_dir: Union[Unset, RiskManagementPublicControllerListRisksSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    applicable: Union[Unset, bool] = UNSET,
    status: Union[Unset, RiskManagementPublicControllerListRisksStatus] = UNSET,
    is_scored: Union[Unset, bool] = UNSET,
    treatment_plan: Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    needs_attention: Union[Unset, bool] = UNSET,
    impact: Union[Unset, float] = UNSET,
    likelihood: Union[Unset, float] = UNSET,
    min_score: Union[Unset, float] = UNSET,
    max_score: Union[Unset, float] = UNSET,
    vendor_id: Union[None, Unset, float] = UNSET,
    only_vendors: Union[Unset, bool] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
    """Find risks by search terms and filters

     List all risks

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskManagementPublicControllerListRisksSort]):  Example: ID.
        sort_dir (Union[Unset, RiskManagementPublicControllerListRisksSortDir]):  Example: ASC.
        q (Union[Unset, str]):
        applicable (Union[Unset, bool]):
        status (Union[Unset, RiskManagementPublicControllerListRisksStatus]):  Example: ACTIVE.
        is_scored (Union[Unset, bool]):
        treatment_plan (Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan]):
            Example: UNTREATED.
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        needs_attention (Union[Unset, bool]):
        impact (Union[Unset, float]):  Example: 3.
        likelihood (Union[Unset, float]):  Example: 1.
        min_score (Union[Unset, float]):  Example: 1.
        max_score (Union[Unset, float]):  Example: 1.
        vendor_id (Union[None, Unset, float]):  Example: 1.
        only_vendors (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        sort=sort,
        sort_dir=sort_dir,
        q=q,
        applicable=applicable,
        status=status,
        is_scored=is_scored,
        treatment_plan=treatment_plan,
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        needs_attention=needs_attention,
        impact=impact,
        likelihood=likelihood,
        min_score=min_score,
        max_score=max_score,
        vendor_id=vendor_id,
        only_vendors=only_vendors,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    sort: Union[Unset, RiskManagementPublicControllerListRisksSort] = UNSET,
    sort_dir: Union[Unset, RiskManagementPublicControllerListRisksSortDir] = UNSET,
    q: Union[Unset, str] = UNSET,
    applicable: Union[Unset, bool] = UNSET,
    status: Union[Unset, RiskManagementPublicControllerListRisksStatus] = UNSET,
    is_scored: Union[Unset, bool] = UNSET,
    treatment_plan: Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan] = UNSET,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    needs_attention: Union[Unset, bool] = UNSET,
    impact: Union[Unset, float] = UNSET,
    likelihood: Union[Unset, float] = UNSET,
    min_score: Union[Unset, float] = UNSET,
    max_score: Union[Unset, float] = UNSET,
    vendor_id: Union[None, Unset, float] = UNSET,
    only_vendors: Union[Unset, bool] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]]:
    """Find risks by search terms and filters

     List all risks

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        sort (Union[Unset, RiskManagementPublicControllerListRisksSort]):  Example: ID.
        sort_dir (Union[Unset, RiskManagementPublicControllerListRisksSortDir]):  Example: ASC.
        q (Union[Unset, str]):
        applicable (Union[Unset, bool]):
        status (Union[Unset, RiskManagementPublicControllerListRisksStatus]):  Example: ACTIVE.
        is_scored (Union[Unset, bool]):
        treatment_plan (Union[Unset, RiskManagementPublicControllerListRisksTreatmentPlan]):
            Example: UNTREATED.
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        needs_attention (Union[Unset, bool]):
        impact (Union[Unset, float]):  Example: 3.
        likelihood (Union[Unset, float]):  Example: 1.
        min_score (Union[Unset, float]):  Example: 1.
        max_score (Union[Unset, float]):  Example: 1.
        vendor_id (Union[None, Unset, float]):  Example: 1.
        only_vendors (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RisksPaginatedResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            sort=sort,
            sort_dir=sort_dir,
            q=q,
            applicable=applicable,
            status=status,
            is_scored=is_scored,
            treatment_plan=treatment_plan,
            categories_ids=categories_ids,
            owners_ids=owners_ids,
            needs_attention=needs_attention,
            impact=impact,
            likelihood=likelihood,
            min_score=min_score,
            max_score=max_score,
            vendor_id=vendor_id,
            only_vendors=only_vendors,
        )
    ).parsed
