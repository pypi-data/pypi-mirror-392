from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.evidence_library_public_controller_list_evidence_sort import (
    EvidenceLibraryPublicControllerListEvidenceSort,
)
from ...models.evidence_library_public_controller_list_evidence_sort_dir import (
    EvidenceLibraryPublicControllerListEvidenceSortDir,
)
from ...models.evidence_library_public_controller_list_evidence_status_item import (
    EvidenceLibraryPublicControllerListEvidenceStatusItem,
)
from ...models.evidence_library_public_controller_list_evidence_version_source_types_item import (
    EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem,
)
from ...models.evidence_library_response_public_dto import EvidenceLibraryResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: float,
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[None, Unset, str] = UNSET,
    file_key: Union[Unset, str] = UNSET,
    sort: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort] = UNSET,
    sort_dir: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    status: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]] = UNSET,
    version_source_types: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    json_q: Union[None, Unset, str]
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    params["fileKey"] = file_key

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sortDir"] = json_sort_dir

    json_exclude_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(exclude_ids, Unset):
        json_exclude_ids = exclude_ids

    params["excludeIds"] = json_exclude_ids

    params["excludeControlId"] = exclude_control_id

    json_status: Union[Unset, list[str]] = UNSET
    if not isinstance(status, Unset):
        json_status = []
        for status_item_data in status:
            status_item = status_item_data.value
            json_status.append(status_item)

    params["status"] = json_status

    json_version_source_types: Union[Unset, list[str]] = UNSET
    if not isinstance(version_source_types, Unset):
        json_version_source_types = []
        for version_source_types_item_data in version_source_types:
            version_source_types_item = version_source_types_item_data.value
            json_version_source_types.append(version_source_types_item)

    params["versionSourceTypes[]"] = json_version_source_types

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/evidence-library",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = EvidenceLibraryResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[None, Unset, str] = UNSET,
    file_key: Union[Unset, str] = UNSET,
    sort: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort] = UNSET,
    sort_dir: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    status: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]] = UNSET,
    version_source_types: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]] = UNSET,
) -> Response[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find evidence by workspace id

     List evidence given the provided search terms and filters

    Args:
        workspace_id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[None, Unset, str]):  Example: Evidence 1.
        file_key (Union[Unset, str]):  Example: UUID-FOLDER/reports/UUID-FOLDER/TestReport.pdf.
        sort (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort]):  Example:
            RENEWAL_DATE.
        sort_dir (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir]):  Example:
            ASC.
        exclude_ids (Union[Unset, list[float]]):
        exclude_control_id (Union[Unset, float]):  Example: 1.
        status (Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]]):
            Example: ['EXPIRED', 'READY'].
        version_source_types (Union[Unset,
            list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]]):  Example: FILE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        page=page,
        limit=limit,
        q=q,
        file_key=file_key,
        sort=sort,
        sort_dir=sort_dir,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        status=status,
        version_source_types=version_source_types,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[None, Unset, str] = UNSET,
    file_key: Union[Unset, str] = UNSET,
    sort: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort] = UNSET,
    sort_dir: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    status: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]] = UNSET,
    version_source_types: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]] = UNSET,
) -> Optional[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find evidence by workspace id

     List evidence given the provided search terms and filters

    Args:
        workspace_id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[None, Unset, str]):  Example: Evidence 1.
        file_key (Union[Unset, str]):  Example: UUID-FOLDER/reports/UUID-FOLDER/TestReport.pdf.
        sort (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort]):  Example:
            RENEWAL_DATE.
        sort_dir (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir]):  Example:
            ASC.
        exclude_ids (Union[Unset, list[float]]):
        exclude_control_id (Union[Unset, float]):  Example: 1.
        status (Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]]):
            Example: ['EXPIRED', 'READY'].
        version_source_types (Union[Unset,
            list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]]):  Example: FILE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        page=page,
        limit=limit,
        q=q,
        file_key=file_key,
        sort=sort,
        sort_dir=sort_dir,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        status=status,
        version_source_types=version_source_types,
    ).parsed


async def asyncio_detailed(
    workspace_id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[None, Unset, str] = UNSET,
    file_key: Union[Unset, str] = UNSET,
    sort: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort] = UNSET,
    sort_dir: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    status: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]] = UNSET,
    version_source_types: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]] = UNSET,
) -> Response[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find evidence by workspace id

     List evidence given the provided search terms and filters

    Args:
        workspace_id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[None, Unset, str]):  Example: Evidence 1.
        file_key (Union[Unset, str]):  Example: UUID-FOLDER/reports/UUID-FOLDER/TestReport.pdf.
        sort (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort]):  Example:
            RENEWAL_DATE.
        sort_dir (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir]):  Example:
            ASC.
        exclude_ids (Union[Unset, list[float]]):
        exclude_control_id (Union[Unset, float]):  Example: 1.
        status (Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]]):
            Example: ['EXPIRED', 'READY'].
        version_source_types (Union[Unset,
            list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]]):  Example: FILE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        page=page,
        limit=limit,
        q=q,
        file_key=file_key,
        sort=sort,
        sort_dir=sort_dir,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        status=status,
        version_source_types=version_source_types,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: float,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[None, Unset, str] = UNSET,
    file_key: Union[Unset, str] = UNSET,
    sort: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort] = UNSET,
    sort_dir: Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    status: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]] = UNSET,
    version_source_types: Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]] = UNSET,
) -> Optional[Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find evidence by workspace id

     List evidence given the provided search terms and filters

    Args:
        workspace_id (float):
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[None, Unset, str]):  Example: Evidence 1.
        file_key (Union[Unset, str]):  Example: UUID-FOLDER/reports/UUID-FOLDER/TestReport.pdf.
        sort (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSort]):  Example:
            RENEWAL_DATE.
        sort_dir (Union[Unset, EvidenceLibraryPublicControllerListEvidenceSortDir]):  Example:
            ASC.
        exclude_ids (Union[Unset, list[float]]):
        exclude_control_id (Union[Unset, float]):  Example: 1.
        status (Union[Unset, list[EvidenceLibraryPublicControllerListEvidenceStatusItem]]):
            Example: ['EXPIRED', 'READY'].
        version_source_types (Union[Unset,
            list[EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem]]):  Example: FILE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EvidenceLibraryResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            page=page,
            limit=limit,
            q=q,
            file_key=file_key,
            sort=sort,
            sort_dir=sort_dir,
            exclude_ids=exclude_ids,
            exclude_control_id=exclude_control_id,
            status=status,
            version_source_types=version_source_types,
        )
    ).parsed
