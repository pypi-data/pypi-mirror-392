from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.mapped_external_evidence_response_public_dto import MappedExternalEvidenceResponsePublicDto
from ...models.upload_evidence_public_dto import UploadEvidencePublicDto
from ...types import Response


def _get_kwargs(
    workspace_id: float,
    id: float,
    *,
    body: Union[
        UploadEvidencePublicDto,
        UploadEvidencePublicDto,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/workspaces/{workspace_id}/controls/{id}/external-evidence",
    }

    if isinstance(body, UploadEvidencePublicDto):
        _files_body = body.to_multipart()

        _kwargs["files"] = _files_body
        headers["Content-Type"] = "multipart/form-data"
    if isinstance(body, UploadEvidencePublicDto):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    if response.status_code == 201:
        response_201 = MappedExternalEvidenceResponsePublicDto.from_dict(response.json())

        return response_201
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
    if response.status_code == 413:
        response_413 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_413
    if response.status_code == 500:
        response_500 = ExceptionResponseDto.from_dict(response.json())

        return response_500
    if response.status_code == 503:
        response_503 = ExceptionResponsePublicDto.from_dict(response.json())

        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: float,
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UploadEvidencePublicDto,
        UploadEvidencePublicDto,
    ],
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    """Upload external evidence document by control id

     Upload external evidence to map to a control

    Args:
        workspace_id (float):
        id (float):
        body (UploadEvidencePublicDto):
        body (UploadEvidencePublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: float,
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UploadEvidencePublicDto,
        UploadEvidencePublicDto,
    ],
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    """Upload external evidence document by control id

     Upload external evidence to map to a control

    Args:
        workspace_id (float):
        id (float):
        body (UploadEvidencePublicDto):
        body (UploadEvidencePublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    workspace_id: float,
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UploadEvidencePublicDto,
        UploadEvidencePublicDto,
    ],
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    """Upload external evidence document by control id

     Upload external evidence to map to a control

    Args:
        workspace_id (float):
        id (float):
        body (UploadEvidencePublicDto):
        body (UploadEvidencePublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: float,
    id: float,
    *,
    client: AuthenticatedClient,
    body: Union[
        UploadEvidencePublicDto,
        UploadEvidencePublicDto,
    ],
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]]:
    """Upload external evidence document by control id

     Upload external evidence to map to a control

    Args:
        workspace_id (float):
        id (float):
        body (UploadEvidencePublicDto):
        body (UploadEvidencePublicDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, MappedExternalEvidenceResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
