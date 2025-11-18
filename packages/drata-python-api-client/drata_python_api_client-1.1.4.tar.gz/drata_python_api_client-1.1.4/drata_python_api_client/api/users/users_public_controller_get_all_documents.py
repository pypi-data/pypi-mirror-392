from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.user_all_documents_response_public_dto import UserAllDocumentsResponsePublicDto
from ...models.users_public_controller_get_all_documents_type import UsersPublicControllerGetAllDocumentsType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: float,
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    type_: Union[Unset, UsersPublicControllerGetAllDocumentsType] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/users/{id}/documents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = UserAllDocumentsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
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
    type_: Union[Unset, UsersPublicControllerGetAllDocumentsType] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
    """Find user documents by user id

     List user documents given the provided search terms and filters.

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security training 2020.
        type_ (Union[Unset, UsersPublicControllerGetAllDocumentsType]):  Example: SEC_TRAINING.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        page=page,
        limit=limit,
        q=q,
        type_=type_,
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
    type_: Union[Unset, UsersPublicControllerGetAllDocumentsType] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
    """Find user documents by user id

     List user documents given the provided search terms and filters.

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security training 2020.
        type_ (Union[Unset, UsersPublicControllerGetAllDocumentsType]):  Example: SEC_TRAINING.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]
    """

    return sync_detailed(
        id=id,
        client=client,
        page=page,
        limit=limit,
        q=q,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    type_: Union[Unset, UsersPublicControllerGetAllDocumentsType] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
    """Find user documents by user id

     List user documents given the provided search terms and filters.

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security training 2020.
        type_ (Union[Unset, UsersPublicControllerGetAllDocumentsType]):  Example: SEC_TRAINING.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        page=page,
        limit=limit,
        q=q,
        type_=type_,
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
    type_: Union[Unset, UsersPublicControllerGetAllDocumentsType] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]]:
    """Find user documents by user id

     List user documents given the provided search terms and filters.

    Args:
        id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security training 2020.
        type_ (Union[Unset, UsersPublicControllerGetAllDocumentsType]):  Example: SEC_TRAINING.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, UserAllDocumentsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            page=page,
            limit=limit,
            q=q,
            type_=type_,
        )
    ).parsed
