from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.control_short_response_public_dto import ControlShortResponsePublicDto
from ...models.edit_control_request_public_dto import EditControlRequestPublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import Response


def _get_kwargs(
    workspace_id: float,
    control_id: float,
    *,
    body: EditControlRequestPublicDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/workspaces/{workspace_id}/controls/{control_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = ControlShortResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: float,
    control_id: float,
    *,
    client: AuthenticatedClient,
    body: EditControlRequestPublicDto,
) -> Response[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Edit control of the account

     Edit control

    Args:
        workspace_id (float):
        control_id (float):
        body (EditControlRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        control_id=control_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: float,
    control_id: float,
    *,
    client: AuthenticatedClient,
    body: EditControlRequestPublicDto,
) -> Optional[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Edit control of the account

     Edit control

    Args:
        workspace_id (float):
        control_id (float):
        body (EditControlRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        control_id=control_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    workspace_id: float,
    control_id: float,
    *,
    client: AuthenticatedClient,
    body: EditControlRequestPublicDto,
) -> Response[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Edit control of the account

     Edit control

    Args:
        workspace_id (float):
        control_id (float):
        body (EditControlRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        control_id=control_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: float,
    control_id: float,
    *,
    client: AuthenticatedClient,
    body: EditControlRequestPublicDto,
) -> Optional[Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Edit control of the account

     Edit control

    Args:
        workspace_id (float):
        control_id (float):
        body (EditControlRequestPublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlShortResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            control_id=control_id,
            client=client,
            body=body,
        )
    ).parsed
