from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.control_tests_paginated_response_public_dto import ControlTestsPaginatedResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.monitors_public_controller_list_monitors_check_result_status import (
    MonitorsPublicControllerListMonitorsCheckResultStatus,
)
from ...models.monitors_public_controller_list_monitors_check_result_statuses_item import (
    MonitorsPublicControllerListMonitorsCheckResultStatusesItem,
)
from ...models.monitors_public_controller_list_monitors_check_status import (
    MonitorsPublicControllerListMonitorsCheckStatus,
)
from ...models.monitors_public_controller_list_monitors_report_interval import (
    MonitorsPublicControllerListMonitorsReportInterval,
)
from ...models.monitors_public_controller_list_monitors_source import MonitorsPublicControllerListMonitorsSource
from ...models.monitors_public_controller_list_monitors_type import MonitorsPublicControllerListMonitorsType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    check_result_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus] = UNSET,
    check_result_statuses: Union[Unset, list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]] = UNSET,
    check_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus] = UNSET,
    source: Union[Unset, MonitorsPublicControllerListMonitorsSource] = UNSET,
    type_: Union[Unset, MonitorsPublicControllerListMonitorsType] = UNSET,
    control_owner: Union[Unset, float] = UNSET,
    get_all: Union[Unset, bool] = UNSET,
    include_archived_controls: Union[Unset, bool] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    exclude_test_ids: Union[Unset, list[float]] = UNSET,
    sort_by_name: Union[Unset, bool] = UNSET,
    report_interval: Union[Unset, MonitorsPublicControllerListMonitorsReportInterval] = UNSET,
    drafts: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_check_result_status: Union[Unset, str] = UNSET
    if not isinstance(check_result_status, Unset):
        json_check_result_status = check_result_status.value

    params["checkResultStatus"] = json_check_result_status

    json_check_result_statuses: Union[Unset, list[str]] = UNSET
    if not isinstance(check_result_statuses, Unset):
        json_check_result_statuses = []
        for check_result_statuses_item_data in check_result_statuses:
            check_result_statuses_item = check_result_statuses_item_data.value
            json_check_result_statuses.append(check_result_statuses_item)

    params["checkResultStatuses"] = json_check_result_statuses

    json_check_status: Union[Unset, str] = UNSET
    if not isinstance(check_status, Unset):
        json_check_status = check_status.value

    params["checkStatus"] = json_check_status

    json_source: Union[Unset, str] = UNSET
    if not isinstance(source, Unset):
        json_source = source.value

    params["source"] = json_source

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params["controlOwner"] = control_owner

    params["getAll"] = get_all

    params["includeArchivedControls"] = include_archived_controls

    params["controlId"] = control_id

    params["excludeControlId"] = exclude_control_id

    json_exclude_test_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(exclude_test_ids, Unset):
        json_exclude_test_ids = exclude_test_ids

    params["excludeTestIds"] = json_exclude_test_ids

    params["sortByName"] = sort_by_name

    json_report_interval: Union[Unset, str] = UNSET
    if not isinstance(report_interval, Unset):
        json_report_interval = report_interval.value

    params["reportInterval"] = json_report_interval

    params["drafts"] = drafts

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/monitors",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = ControlTestsPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
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
    check_result_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus] = UNSET,
    check_result_statuses: Union[Unset, list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]] = UNSET,
    check_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus] = UNSET,
    source: Union[Unset, MonitorsPublicControllerListMonitorsSource] = UNSET,
    type_: Union[Unset, MonitorsPublicControllerListMonitorsType] = UNSET,
    control_owner: Union[Unset, float] = UNSET,
    get_all: Union[Unset, bool] = UNSET,
    include_archived_controls: Union[Unset, bool] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    exclude_test_ids: Union[Unset, list[float]] = UNSET,
    sort_by_name: Union[Unset, bool] = UNSET,
    report_interval: Union[Unset, MonitorsPublicControllerListMonitorsReportInterval] = UNSET,
    drafts: Union[Unset, bool] = UNSET,
) -> Response[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find monitor by search terms and filters

     List Monitors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: SSL enforced on company website.
        check_result_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus]):
            Example: ERROR.
        check_result_statuses (Union[Unset,
            list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]]):  Example: ['PASSED',
            'FAILED'].
        check_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus]):  Example:
            ENABLED.
        source (Union[Unset, MonitorsPublicControllerListMonitorsSource]):  Example: DRATA.
        type_ (Union[Unset, MonitorsPublicControllerListMonitorsType]):  Example: INFRASTRUCTURE.
        control_owner (Union[Unset, float]):  Example: 1.
        get_all (Union[Unset, bool]):  Example: True.
        include_archived_controls (Union[Unset, bool]):  Example: True.
        control_id (Union[Unset, float]):  Example: 1.
        exclude_control_id (Union[Unset, float]):  Example: 1.
        exclude_test_ids (Union[Unset, list[float]]):
        sort_by_name (Union[Unset, bool]):  Example: True.
        report_interval (Union[Unset, MonitorsPublicControllerListMonitorsReportInterval]):
            Example: MONTHLY.
        drafts (Union[Unset, bool]):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        check_result_status=check_result_status,
        check_result_statuses=check_result_statuses,
        check_status=check_status,
        source=source,
        type_=type_,
        control_owner=control_owner,
        get_all=get_all,
        include_archived_controls=include_archived_controls,
        control_id=control_id,
        exclude_control_id=exclude_control_id,
        exclude_test_ids=exclude_test_ids,
        sort_by_name=sort_by_name,
        report_interval=report_interval,
        drafts=drafts,
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
    check_result_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus] = UNSET,
    check_result_statuses: Union[Unset, list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]] = UNSET,
    check_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus] = UNSET,
    source: Union[Unset, MonitorsPublicControllerListMonitorsSource] = UNSET,
    type_: Union[Unset, MonitorsPublicControllerListMonitorsType] = UNSET,
    control_owner: Union[Unset, float] = UNSET,
    get_all: Union[Unset, bool] = UNSET,
    include_archived_controls: Union[Unset, bool] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    exclude_test_ids: Union[Unset, list[float]] = UNSET,
    sort_by_name: Union[Unset, bool] = UNSET,
    report_interval: Union[Unset, MonitorsPublicControllerListMonitorsReportInterval] = UNSET,
    drafts: Union[Unset, bool] = UNSET,
) -> Optional[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find monitor by search terms and filters

     List Monitors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: SSL enforced on company website.
        check_result_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus]):
            Example: ERROR.
        check_result_statuses (Union[Unset,
            list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]]):  Example: ['PASSED',
            'FAILED'].
        check_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus]):  Example:
            ENABLED.
        source (Union[Unset, MonitorsPublicControllerListMonitorsSource]):  Example: DRATA.
        type_ (Union[Unset, MonitorsPublicControllerListMonitorsType]):  Example: INFRASTRUCTURE.
        control_owner (Union[Unset, float]):  Example: 1.
        get_all (Union[Unset, bool]):  Example: True.
        include_archived_controls (Union[Unset, bool]):  Example: True.
        control_id (Union[Unset, float]):  Example: 1.
        exclude_control_id (Union[Unset, float]):  Example: 1.
        exclude_test_ids (Union[Unset, list[float]]):
        sort_by_name (Union[Unset, bool]):  Example: True.
        report_interval (Union[Unset, MonitorsPublicControllerListMonitorsReportInterval]):
            Example: MONTHLY.
        drafts (Union[Unset, bool]):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        check_result_status=check_result_status,
        check_result_statuses=check_result_statuses,
        check_status=check_status,
        source=source,
        type_=type_,
        control_owner=control_owner,
        get_all=get_all,
        include_archived_controls=include_archived_controls,
        control_id=control_id,
        exclude_control_id=exclude_control_id,
        exclude_test_ids=exclude_test_ids,
        sort_by_name=sort_by_name,
        report_interval=report_interval,
        drafts=drafts,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    check_result_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus] = UNSET,
    check_result_statuses: Union[Unset, list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]] = UNSET,
    check_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus] = UNSET,
    source: Union[Unset, MonitorsPublicControllerListMonitorsSource] = UNSET,
    type_: Union[Unset, MonitorsPublicControllerListMonitorsType] = UNSET,
    control_owner: Union[Unset, float] = UNSET,
    get_all: Union[Unset, bool] = UNSET,
    include_archived_controls: Union[Unset, bool] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    exclude_test_ids: Union[Unset, list[float]] = UNSET,
    sort_by_name: Union[Unset, bool] = UNSET,
    report_interval: Union[Unset, MonitorsPublicControllerListMonitorsReportInterval] = UNSET,
    drafts: Union[Unset, bool] = UNSET,
) -> Response[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find monitor by search terms and filters

     List Monitors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: SSL enforced on company website.
        check_result_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus]):
            Example: ERROR.
        check_result_statuses (Union[Unset,
            list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]]):  Example: ['PASSED',
            'FAILED'].
        check_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus]):  Example:
            ENABLED.
        source (Union[Unset, MonitorsPublicControllerListMonitorsSource]):  Example: DRATA.
        type_ (Union[Unset, MonitorsPublicControllerListMonitorsType]):  Example: INFRASTRUCTURE.
        control_owner (Union[Unset, float]):  Example: 1.
        get_all (Union[Unset, bool]):  Example: True.
        include_archived_controls (Union[Unset, bool]):  Example: True.
        control_id (Union[Unset, float]):  Example: 1.
        exclude_control_id (Union[Unset, float]):  Example: 1.
        exclude_test_ids (Union[Unset, list[float]]):
        sort_by_name (Union[Unset, bool]):  Example: True.
        report_interval (Union[Unset, MonitorsPublicControllerListMonitorsReportInterval]):
            Example: MONTHLY.
        drafts (Union[Unset, bool]):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        check_result_status=check_result_status,
        check_result_statuses=check_result_statuses,
        check_status=check_status,
        source=source,
        type_=type_,
        control_owner=control_owner,
        get_all=get_all,
        include_archived_controls=include_archived_controls,
        control_id=control_id,
        exclude_control_id=exclude_control_id,
        exclude_test_ids=exclude_test_ids,
        sort_by_name=sort_by_name,
        report_interval=report_interval,
        drafts=drafts,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    check_result_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus] = UNSET,
    check_result_statuses: Union[Unset, list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]] = UNSET,
    check_status: Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus] = UNSET,
    source: Union[Unset, MonitorsPublicControllerListMonitorsSource] = UNSET,
    type_: Union[Unset, MonitorsPublicControllerListMonitorsType] = UNSET,
    control_owner: Union[Unset, float] = UNSET,
    get_all: Union[Unset, bool] = UNSET,
    include_archived_controls: Union[Unset, bool] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    exclude_test_ids: Union[Unset, list[float]] = UNSET,
    sort_by_name: Union[Unset, bool] = UNSET,
    report_interval: Union[Unset, MonitorsPublicControllerListMonitorsReportInterval] = UNSET,
    drafts: Union[Unset, bool] = UNSET,
) -> Optional[Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find monitor by search terms and filters

     List Monitors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: SSL enforced on company website.
        check_result_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckResultStatus]):
            Example: ERROR.
        check_result_statuses (Union[Unset,
            list[MonitorsPublicControllerListMonitorsCheckResultStatusesItem]]):  Example: ['PASSED',
            'FAILED'].
        check_status (Union[Unset, MonitorsPublicControllerListMonitorsCheckStatus]):  Example:
            ENABLED.
        source (Union[Unset, MonitorsPublicControllerListMonitorsSource]):  Example: DRATA.
        type_ (Union[Unset, MonitorsPublicControllerListMonitorsType]):  Example: INFRASTRUCTURE.
        control_owner (Union[Unset, float]):  Example: 1.
        get_all (Union[Unset, bool]):  Example: True.
        include_archived_controls (Union[Unset, bool]):  Example: True.
        control_id (Union[Unset, float]):  Example: 1.
        exclude_control_id (Union[Unset, float]):  Example: 1.
        exclude_test_ids (Union[Unset, list[float]]):
        sort_by_name (Union[Unset, bool]):  Example: True.
        report_interval (Union[Unset, MonitorsPublicControllerListMonitorsReportInterval]):
            Example: MONTHLY.
        drafts (Union[Unset, bool]):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlTestsPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            check_result_status=check_result_status,
            check_result_statuses=check_result_statuses,
            check_status=check_status,
            source=source,
            type_=type_,
            control_owner=control_owner,
            get_all=get_all,
            include_archived_controls=include_archived_controls,
            control_id=control_id,
            exclude_control_id=exclude_control_id,
            exclude_test_ids=exclude_test_ids,
            sort_by_name=sort_by_name,
            report_interval=report_interval,
            drafts=drafts,
        )
    ).parsed
