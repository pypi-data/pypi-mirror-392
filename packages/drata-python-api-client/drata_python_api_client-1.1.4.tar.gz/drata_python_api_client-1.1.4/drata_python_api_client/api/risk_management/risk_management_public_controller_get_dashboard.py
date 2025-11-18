from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.dashboard_response_public_dto import DashboardResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.risk_management_public_controller_get_dashboard_risk_filter import (
    RiskManagementPublicControllerGetDashboardRiskFilter,
)
from ...models.risk_management_public_controller_get_dashboard_status_item import (
    RiskManagementPublicControllerGetDashboardStatusItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter] = UNSET,
    status: Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_categories_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(categories_ids, Unset):
        json_categories_ids = categories_ids

    params["categoriesIds"] = json_categories_ids

    json_owners_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(owners_ids, Unset):
        json_owners_ids = owners_ids

    params["ownersIds"] = json_owners_ids

    json_risk_filter: Union[Unset, str] = UNSET
    if not isinstance(risk_filter, Unset):
        json_risk_filter = risk_filter.value

    params["riskFilter"] = json_risk_filter

    json_status: Union[Unset, list[str]] = UNSET
    if not isinstance(status, Unset):
        json_status = []
        for status_item_data in status:
            status_item = status_item_data.value
            json_status.append(status_item)

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/risk-management-insights",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = DashboardResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter] = UNSET,
    status: Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]] = UNSET,
) -> Response[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get risk management insights

     Get risk management insights

    Args:
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter]):
            Example: INTERNAL_ONLY.
        status (Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]]):
            Example: ['ACTIVE'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        risk_filter=risk_filter,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter] = UNSET,
    status: Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]] = UNSET,
) -> Optional[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get risk management insights

     Get risk management insights

    Args:
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter]):
            Example: INTERNAL_ONLY.
        status (Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]]):
            Example: ['ACTIVE'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        risk_filter=risk_filter,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter] = UNSET,
    status: Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]] = UNSET,
) -> Response[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get risk management insights

     Get risk management insights

    Args:
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter]):
            Example: INTERNAL_ONLY.
        status (Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]]):
            Example: ['ACTIVE'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        categories_ids=categories_ids,
        owners_ids=owners_ids,
        risk_filter=risk_filter,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    categories_ids: Union[Unset, list[float]] = UNSET,
    owners_ids: Union[Unset, list[float]] = UNSET,
    risk_filter: Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter] = UNSET,
    status: Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]] = UNSET,
) -> Optional[Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Get risk management insights

     Get risk management insights

    Args:
        categories_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        owners_ids (Union[Unset, list[float]]):  Example: [1, 2, 3].
        risk_filter (Union[Unset, RiskManagementPublicControllerGetDashboardRiskFilter]):
            Example: INTERNAL_ONLY.
        status (Union[Unset, list[RiskManagementPublicControllerGetDashboardStatusItem]]):
            Example: ['ACTIVE'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DashboardResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            categories_ids=categories_ids,
            owners_ids=owners_ids,
            risk_filter=risk_filter,
            status=status,
        )
    ).parsed
