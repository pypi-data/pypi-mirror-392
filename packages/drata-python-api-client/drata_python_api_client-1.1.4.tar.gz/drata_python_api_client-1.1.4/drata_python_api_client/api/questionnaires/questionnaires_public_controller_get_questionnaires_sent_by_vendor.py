from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.questionnaires_vendors_response_public_dto import QuestionnairesVendorsResponsePublicDto
from ...types import Response


def _get_kwargs(
    vendor_id: float,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/questionnaires/vendor/{vendor_id}/sent",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = QuestionnairesVendorsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    vendor_id: float,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    """Find all questionnaires sent to a vendor

     Get questionnaires sent by vendor id

    Args:
        vendor_id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        vendor_id=vendor_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    vendor_id: float,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    """Find all questionnaires sent to a vendor

     Get questionnaires sent by vendor id

    Args:
        vendor_id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]
    """

    return sync_detailed(
        vendor_id=vendor_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    vendor_id: float,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    """Find all questionnaires sent to a vendor

     Get questionnaires sent by vendor id

    Args:
        vendor_id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        vendor_id=vendor_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    vendor_id: float,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]]:
    """Find all questionnaires sent to a vendor

     Get questionnaires sent by vendor id

    Args:
        vendor_id (float):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, QuestionnairesVendorsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            vendor_id=vendor_id,
            client=client,
        )
    ).parsed
