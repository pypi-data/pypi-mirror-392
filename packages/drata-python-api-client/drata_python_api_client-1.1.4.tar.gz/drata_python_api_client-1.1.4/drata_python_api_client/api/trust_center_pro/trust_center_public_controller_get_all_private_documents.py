from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.trust_center_all_private_documents_response_public_dto import (
    TrustCenterAllPrivateDocumentsResponsePublicDto,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: Union[Unset, str] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["workspaceId"] = workspace_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/trust-center/private-documents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = TrustCenterAllPrivateDocumentsResponsePublicDto.from_dict(response.json())

        return response_200
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
) -> Response[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    """Get all private documents

     Get all the policies, compliance and security reports private documents. This endpoint is only
    available on Trust Center Pro.

    Args:
        q (Union[Unset, str]):  Example: Report 01.
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        q=q,
        workspace_id=workspace_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    """Get all private documents

     Get all the policies, compliance and security reports private documents. This endpoint is only
    available on Trust Center Pro.

    Args:
        q (Union[Unset, str]):  Example: Report 01.
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        q=q,
        workspace_id=workspace_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    """Get all private documents

     Get all the policies, compliance and security reports private documents. This endpoint is only
    available on Trust Center Pro.

    Args:
        q (Union[Unset, str]):  Example: Report 01.
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        q=q,
        workspace_id=workspace_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]]:
    """Get all private documents

     Get all the policies, compliance and security reports private documents. This endpoint is only
    available on Trust Center Pro.

    Args:
        q (Union[Unset, str]):  Example: Report 01.
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, TrustCenterAllPrivateDocumentsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            workspace_id=workspace_id,
        )
    ).parsed
