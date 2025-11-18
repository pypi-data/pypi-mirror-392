import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.events_public_controller_list_events_category import EventsPublicControllerListEventsCategory
from ...models.events_public_controller_list_events_sort import EventsPublicControllerListEventsSort
from ...models.events_public_controller_list_events_sort_dir import EventsPublicControllerListEventsSortDir
from ...models.events_public_controller_list_events_source import EventsPublicControllerListEventsSource
from ...models.events_public_controller_list_events_status import EventsPublicControllerListEventsStatus
from ...models.events_public_controller_list_events_type import EventsPublicControllerListEventsType
from ...models.events_response_public_dto import EventsResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, EventsPublicControllerListEventsSort] = UNSET,
    sort_dir: Union[Unset, EventsPublicControllerListEventsSortDir] = UNSET,
    type_: Union[Unset, EventsPublicControllerListEventsType] = UNSET,
    source: Union[Unset, EventsPublicControllerListEventsSource] = UNSET,
    category: Union[Unset, EventsPublicControllerListEventsCategory] = UNSET,
    status: Union[Unset, EventsPublicControllerListEventsStatus] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
    most_recent: Union[Unset, bool] = UNSET,
    event_error_status: Union[Unset, bool] = UNSET,
    created_at_start_date: Union[Unset, datetime.datetime] = UNSET,
    created_at_end_date: Union[Unset, datetime.datetime] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sortDir"] = json_sort_dir

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    json_source: Union[Unset, str] = UNSET
    if not isinstance(source, Unset):
        json_source = source.value

    params["source"] = json_source

    json_category: Union[Unset, str] = UNSET
    if not isinstance(category, Unset):
        json_category = category.value

    params["category"] = json_category

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["userId"] = user_id

    params["controlId"] = control_id

    params["testId"] = test_id

    params["workspaceId"] = workspace_id

    params["mostRecent"] = most_recent

    params["eventErrorStatus"] = event_error_status

    json_created_at_start_date: Union[Unset, str] = UNSET
    if not isinstance(created_at_start_date, Unset):
        json_created_at_start_date = created_at_start_date.isoformat()
    params["createdAtStartDate"] = json_created_at_start_date

    json_created_at_end_date: Union[Unset, str] = UNSET
    if not isinstance(created_at_end_date, Unset):
        json_created_at_end_date = created_at_end_date.isoformat()
    params["createdAtEndDate"] = json_created_at_end_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/events",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = EventsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
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
    sort: Union[Unset, EventsPublicControllerListEventsSort] = UNSET,
    sort_dir: Union[Unset, EventsPublicControllerListEventsSortDir] = UNSET,
    type_: Union[Unset, EventsPublicControllerListEventsType] = UNSET,
    source: Union[Unset, EventsPublicControllerListEventsSource] = UNSET,
    category: Union[Unset, EventsPublicControllerListEventsCategory] = UNSET,
    status: Union[Unset, EventsPublicControllerListEventsStatus] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
    most_recent: Union[Unset, bool] = UNSET,
    event_error_status: Union[Unset, bool] = UNSET,
    created_at_start_date: Union[Unset, datetime.datetime] = UNSET,
    created_at_end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find events by search terms and filters

     List events given the provided search terms and filters.

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        sort (Union[Unset, EventsPublicControllerListEventsSort]):  Example: CREATED.
        sort_dir (Union[Unset, EventsPublicControllerListEventsSortDir]):  Example: DESC.
        type_ (Union[Unset, EventsPublicControllerListEventsType]):  Example:
            COMPANY_DATA_UPDATED.
        source (Union[Unset, EventsPublicControllerListEventsSource]):  Example:
            UPLOAD_EXTERNAL_EVIDENCE.
        category (Union[Unset, EventsPublicControllerListEventsCategory]):  Example: COMPANY.
        status (Union[Unset, EventsPublicControllerListEventsStatus]):  Example: PASSED.
        user_id (Union[Unset, float]):  Example: 1.
        control_id (Union[Unset, float]):  Example: 1.
        test_id (Union[Unset, float]):  Example: 1.
        workspace_id (Union[Unset, float]):  Example: 1.
        most_recent (Union[Unset, bool]):
        event_error_status (Union[Unset, bool]):
        created_at_start_date (Union[Unset, datetime.datetime]):  Example:
            2025-04-07T01:15:20.289Z.
        created_at_end_date (Union[Unset, datetime.datetime]):  Example: 2025-04-10T01:15:20.281Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        type_=type_,
        source=source,
        category=category,
        status=status,
        user_id=user_id,
        control_id=control_id,
        test_id=test_id,
        workspace_id=workspace_id,
        most_recent=most_recent,
        event_error_status=event_error_status,
        created_at_start_date=created_at_start_date,
        created_at_end_date=created_at_end_date,
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
    sort: Union[Unset, EventsPublicControllerListEventsSort] = UNSET,
    sort_dir: Union[Unset, EventsPublicControllerListEventsSortDir] = UNSET,
    type_: Union[Unset, EventsPublicControllerListEventsType] = UNSET,
    source: Union[Unset, EventsPublicControllerListEventsSource] = UNSET,
    category: Union[Unset, EventsPublicControllerListEventsCategory] = UNSET,
    status: Union[Unset, EventsPublicControllerListEventsStatus] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
    most_recent: Union[Unset, bool] = UNSET,
    event_error_status: Union[Unset, bool] = UNSET,
    created_at_start_date: Union[Unset, datetime.datetime] = UNSET,
    created_at_end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find events by search terms and filters

     List events given the provided search terms and filters.

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        sort (Union[Unset, EventsPublicControllerListEventsSort]):  Example: CREATED.
        sort_dir (Union[Unset, EventsPublicControllerListEventsSortDir]):  Example: DESC.
        type_ (Union[Unset, EventsPublicControllerListEventsType]):  Example:
            COMPANY_DATA_UPDATED.
        source (Union[Unset, EventsPublicControllerListEventsSource]):  Example:
            UPLOAD_EXTERNAL_EVIDENCE.
        category (Union[Unset, EventsPublicControllerListEventsCategory]):  Example: COMPANY.
        status (Union[Unset, EventsPublicControllerListEventsStatus]):  Example: PASSED.
        user_id (Union[Unset, float]):  Example: 1.
        control_id (Union[Unset, float]):  Example: 1.
        test_id (Union[Unset, float]):  Example: 1.
        workspace_id (Union[Unset, float]):  Example: 1.
        most_recent (Union[Unset, bool]):
        event_error_status (Union[Unset, bool]):
        created_at_start_date (Union[Unset, datetime.datetime]):  Example:
            2025-04-07T01:15:20.289Z.
        created_at_end_date (Union[Unset, datetime.datetime]):  Example: 2025-04-10T01:15:20.281Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        type_=type_,
        source=source,
        category=category,
        status=status,
        user_id=user_id,
        control_id=control_id,
        test_id=test_id,
        workspace_id=workspace_id,
        most_recent=most_recent,
        event_error_status=event_error_status,
        created_at_start_date=created_at_start_date,
        created_at_end_date=created_at_end_date,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, EventsPublicControllerListEventsSort] = UNSET,
    sort_dir: Union[Unset, EventsPublicControllerListEventsSortDir] = UNSET,
    type_: Union[Unset, EventsPublicControllerListEventsType] = UNSET,
    source: Union[Unset, EventsPublicControllerListEventsSource] = UNSET,
    category: Union[Unset, EventsPublicControllerListEventsCategory] = UNSET,
    status: Union[Unset, EventsPublicControllerListEventsStatus] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
    most_recent: Union[Unset, bool] = UNSET,
    event_error_status: Union[Unset, bool] = UNSET,
    created_at_start_date: Union[Unset, datetime.datetime] = UNSET,
    created_at_end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find events by search terms and filters

     List events given the provided search terms and filters.

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        sort (Union[Unset, EventsPublicControllerListEventsSort]):  Example: CREATED.
        sort_dir (Union[Unset, EventsPublicControllerListEventsSortDir]):  Example: DESC.
        type_ (Union[Unset, EventsPublicControllerListEventsType]):  Example:
            COMPANY_DATA_UPDATED.
        source (Union[Unset, EventsPublicControllerListEventsSource]):  Example:
            UPLOAD_EXTERNAL_EVIDENCE.
        category (Union[Unset, EventsPublicControllerListEventsCategory]):  Example: COMPANY.
        status (Union[Unset, EventsPublicControllerListEventsStatus]):  Example: PASSED.
        user_id (Union[Unset, float]):  Example: 1.
        control_id (Union[Unset, float]):  Example: 1.
        test_id (Union[Unset, float]):  Example: 1.
        workspace_id (Union[Unset, float]):  Example: 1.
        most_recent (Union[Unset, bool]):
        event_error_status (Union[Unset, bool]):
        created_at_start_date (Union[Unset, datetime.datetime]):  Example:
            2025-04-07T01:15:20.289Z.
        created_at_end_date (Union[Unset, datetime.datetime]):  Example: 2025-04-10T01:15:20.281Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        type_=type_,
        source=source,
        category=category,
        status=status,
        user_id=user_id,
        control_id=control_id,
        test_id=test_id,
        workspace_id=workspace_id,
        most_recent=most_recent,
        event_error_status=event_error_status,
        created_at_start_date=created_at_start_date,
        created_at_end_date=created_at_end_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, EventsPublicControllerListEventsSort] = UNSET,
    sort_dir: Union[Unset, EventsPublicControllerListEventsSortDir] = UNSET,
    type_: Union[Unset, EventsPublicControllerListEventsType] = UNSET,
    source: Union[Unset, EventsPublicControllerListEventsSource] = UNSET,
    category: Union[Unset, EventsPublicControllerListEventsCategory] = UNSET,
    status: Union[Unset, EventsPublicControllerListEventsStatus] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    control_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
    most_recent: Union[Unset, bool] = UNSET,
    event_error_status: Union[Unset, bool] = UNSET,
    created_at_start_date: Union[Unset, datetime.datetime] = UNSET,
    created_at_end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find events by search terms and filters

     List events given the provided search terms and filters.

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        sort (Union[Unset, EventsPublicControllerListEventsSort]):  Example: CREATED.
        sort_dir (Union[Unset, EventsPublicControllerListEventsSortDir]):  Example: DESC.
        type_ (Union[Unset, EventsPublicControllerListEventsType]):  Example:
            COMPANY_DATA_UPDATED.
        source (Union[Unset, EventsPublicControllerListEventsSource]):  Example:
            UPLOAD_EXTERNAL_EVIDENCE.
        category (Union[Unset, EventsPublicControllerListEventsCategory]):  Example: COMPANY.
        status (Union[Unset, EventsPublicControllerListEventsStatus]):  Example: PASSED.
        user_id (Union[Unset, float]):  Example: 1.
        control_id (Union[Unset, float]):  Example: 1.
        test_id (Union[Unset, float]):  Example: 1.
        workspace_id (Union[Unset, float]):  Example: 1.
        most_recent (Union[Unset, bool]):
        event_error_status (Union[Unset, bool]):
        created_at_start_date (Union[Unset, datetime.datetime]):  Example:
            2025-04-07T01:15:20.289Z.
        created_at_end_date (Union[Unset, datetime.datetime]):  Example: 2025-04-10T01:15:20.281Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EventsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            sort=sort,
            sort_dir=sort_dir,
            type_=type_,
            source=source,
            category=category,
            status=status,
            user_id=user_id,
            control_id=control_id,
            test_id=test_id,
            workspace_id=workspace_id,
            most_recent=most_recent,
            event_error_status=event_error_status,
            created_at_start_date=created_at_start_date,
            created_at_end_date=created_at_end_date,
        )
    ).parsed
