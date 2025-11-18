from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.customer_request_public_controller_get_customer_request_list_status import (
    CustomerRequestPublicControllerGetCustomerRequestListStatus,
)
from ...models.customer_requests_response_public_dto import CustomerRequestsResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    framework: str,
    status: Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus] = UNSET,
    only_with_new_messages: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_user_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(user_ids, Unset):
        json_user_ids = user_ids

    params["userIds"] = json_user_ids

    params["isOwned"] = is_owned

    params["framework"] = framework

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["onlyWithNewMessages"] = only_with_new_messages

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/customer-request",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = CustomerRequestsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
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
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    framework: str,
    status: Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus] = UNSET,
    only_with_new_messages: Union[Unset, bool] = UNSET,
) -> Response[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find customer requests by search terms and filters

     Get customer request list

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        framework (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        status (Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus]):
            Example: OUTSTANDING.
        only_with_new_messages (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        user_ids=user_ids,
        is_owned=is_owned,
        framework=framework,
        status=status,
        only_with_new_messages=only_with_new_messages,
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
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    framework: str,
    status: Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus] = UNSET,
    only_with_new_messages: Union[Unset, bool] = UNSET,
) -> Optional[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find customer requests by search terms and filters

     Get customer request list

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        framework (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        status (Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus]):
            Example: OUTSTANDING.
        only_with_new_messages (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        user_ids=user_ids,
        is_owned=is_owned,
        framework=framework,
        status=status,
        only_with_new_messages=only_with_new_messages,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    framework: str,
    status: Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus] = UNSET,
    only_with_new_messages: Union[Unset, bool] = UNSET,
) -> Response[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find customer requests by search terms and filters

     Get customer request list

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        framework (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        status (Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus]):
            Example: OUTSTANDING.
        only_with_new_messages (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        user_ids=user_ids,
        is_owned=is_owned,
        framework=framework,
        status=status,
        only_with_new_messages=only_with_new_messages,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    framework: str,
    status: Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus] = UNSET,
    only_with_new_messages: Union[Unset, bool] = UNSET,
) -> Optional[Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find customer requests by search terms and filters

     Get customer request list

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        framework (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        status (Union[Unset, CustomerRequestPublicControllerGetCustomerRequestListStatus]):
            Example: OUTSTANDING.
        only_with_new_messages (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CustomerRequestsResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            user_ids=user_ids,
            is_owned=is_owned,
            framework=framework,
            status=status,
            only_with_new_messages=only_with_new_messages,
        )
    ).parsed
