from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.company_info_private_access_request_public_dto import CompanyInfoPrivateAccessRequestPublicDto
from ...models.company_info_response_public_dto import CompanyInfoResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CompanyInfoPrivateAccessRequestPublicDto,
    workspace_id: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["workspaceId"] = workspace_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/trust-center/company-info/private-access",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    if response.status_code == 200:
        response_200 = CompanyInfoResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CompanyInfoPrivateAccessRequestPublicDto,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    """Edit the company information private access section

     Update the company information private access section. This endpoint is only available on Trust
    Center Pro.

    Args:
        workspace_id (Union[Unset, float]):
        body (CompanyInfoPrivateAccessRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
        workspace_id=workspace_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CompanyInfoPrivateAccessRequestPublicDto,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    """Edit the company information private access section

     Update the company information private access section. This endpoint is only available on Trust
    Center Pro.

    Args:
        workspace_id (Union[Unset, float]):
        body (CompanyInfoPrivateAccessRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]
    """

    return sync_detailed(
        client=client,
        body=body,
        workspace_id=workspace_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CompanyInfoPrivateAccessRequestPublicDto,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    """Edit the company information private access section

     Update the company information private access section. This endpoint is only available on Trust
    Center Pro.

    Args:
        workspace_id (Union[Unset, float]):
        body (CompanyInfoPrivateAccessRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
        workspace_id=workspace_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CompanyInfoPrivateAccessRequestPublicDto,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]]:
    """Edit the company information private access section

     Update the company information private access section. This endpoint is only available on Trust
    Center Pro.

    Args:
        workspace_id (Union[Unset, float]):
        body (CompanyInfoPrivateAccessRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CompanyInfoResponsePublicDto, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            workspace_id=workspace_id,
        )
    ).parsed
