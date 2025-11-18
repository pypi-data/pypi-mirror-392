from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.assets_public_controller_list_assets_asset_class_type import (
    AssetsPublicControllerListAssetsAssetClassType,
)
from ...models.assets_public_controller_list_assets_asset_provider import AssetsPublicControllerListAssetsAssetProvider
from ...models.assets_public_controller_list_assets_asset_type import AssetsPublicControllerListAssetsAssetType
from ...models.assets_public_controller_list_assets_employment_status import (
    AssetsPublicControllerListAssetsEmploymentStatus,
)
from ...models.assets_public_controller_list_assets_sort import AssetsPublicControllerListAssetsSort
from ...models.assets_public_controller_list_assets_sort_dir import AssetsPublicControllerListAssetsSortDir
from ...models.assets_response_public_dto import AssetsResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, AssetsPublicControllerListAssetsSort] = UNSET,
    sort_dir: Union[Unset, AssetsPublicControllerListAssetsSortDir] = UNSET,
    asset_class_type: Union[Unset, AssetsPublicControllerListAssetsAssetClassType] = UNSET,
    asset_type: Union[Unset, AssetsPublicControllerListAssetsAssetType] = UNSET,
    asset_provider: Union[Unset, AssetsPublicControllerListAssetsAssetProvider] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    employment_status: Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus] = UNSET,
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

    json_asset_class_type: Union[Unset, str] = UNSET
    if not isinstance(asset_class_type, Unset):
        json_asset_class_type = asset_class_type.value

    params["assetClassType"] = json_asset_class_type

    json_asset_type: Union[Unset, str] = UNSET
    if not isinstance(asset_type, Unset):
        json_asset_type = asset_type.value

    params["assetType"] = json_asset_type

    json_asset_provider: Union[Unset, str] = UNSET
    if not isinstance(asset_provider, Unset):
        json_asset_provider = asset_provider.value

    params["assetProvider"] = json_asset_provider

    params["userId"] = user_id

    json_employment_status: Union[Unset, str] = UNSET
    if not isinstance(employment_status, Unset):
        json_employment_status = employment_status.value

    params["employmentStatus"] = json_employment_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/assets",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
    if response.status_code == 200:
        response_200 = AssetsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
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
    sort: Union[Unset, AssetsPublicControllerListAssetsSort] = UNSET,
    sort_dir: Union[Unset, AssetsPublicControllerListAssetsSortDir] = UNSET,
    asset_class_type: Union[Unset, AssetsPublicControllerListAssetsAssetClassType] = UNSET,
    asset_type: Union[Unset, AssetsPublicControllerListAssetsAssetType] = UNSET,
    asset_provider: Union[Unset, AssetsPublicControllerListAssetsAssetProvider] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    employment_status: Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus] = UNSET,
) -> Response[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
    """List all the assets

     Find assets by search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security Program Overview.
        sort (Union[Unset, AssetsPublicControllerListAssetsSort]):  Example: NAME.
        sort_dir (Union[Unset, AssetsPublicControllerListAssetsSortDir]):  Example: ASC.
        asset_class_type (Union[Unset, AssetsPublicControllerListAssetsAssetClassType]):  Example:
            DOCUMENT.
        asset_type (Union[Unset, AssetsPublicControllerListAssetsAssetType]):  Example: PHYSICAL.
        asset_provider (Union[Unset, AssetsPublicControllerListAssetsAssetProvider]):  Example:
            AGENT.
        user_id (Union[Unset, float]):  Example: 1.
        employment_status (Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AssetsResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        asset_class_type=asset_class_type,
        asset_type=asset_type,
        asset_provider=asset_provider,
        user_id=user_id,
        employment_status=employment_status,
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
    sort: Union[Unset, AssetsPublicControllerListAssetsSort] = UNSET,
    sort_dir: Union[Unset, AssetsPublicControllerListAssetsSortDir] = UNSET,
    asset_class_type: Union[Unset, AssetsPublicControllerListAssetsAssetClassType] = UNSET,
    asset_type: Union[Unset, AssetsPublicControllerListAssetsAssetType] = UNSET,
    asset_provider: Union[Unset, AssetsPublicControllerListAssetsAssetProvider] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    employment_status: Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus] = UNSET,
) -> Optional[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
    """List all the assets

     Find assets by search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security Program Overview.
        sort (Union[Unset, AssetsPublicControllerListAssetsSort]):  Example: NAME.
        sort_dir (Union[Unset, AssetsPublicControllerListAssetsSortDir]):  Example: ASC.
        asset_class_type (Union[Unset, AssetsPublicControllerListAssetsAssetClassType]):  Example:
            DOCUMENT.
        asset_type (Union[Unset, AssetsPublicControllerListAssetsAssetType]):  Example: PHYSICAL.
        asset_provider (Union[Unset, AssetsPublicControllerListAssetsAssetProvider]):  Example:
            AGENT.
        user_id (Union[Unset, float]):  Example: 1.
        employment_status (Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AssetsResponsePublicDto, ExceptionResponseDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        asset_class_type=asset_class_type,
        asset_type=asset_type,
        asset_provider=asset_provider,
        user_id=user_id,
        employment_status=employment_status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, AssetsPublicControllerListAssetsSort] = UNSET,
    sort_dir: Union[Unset, AssetsPublicControllerListAssetsSortDir] = UNSET,
    asset_class_type: Union[Unset, AssetsPublicControllerListAssetsAssetClassType] = UNSET,
    asset_type: Union[Unset, AssetsPublicControllerListAssetsAssetType] = UNSET,
    asset_provider: Union[Unset, AssetsPublicControllerListAssetsAssetProvider] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    employment_status: Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus] = UNSET,
) -> Response[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
    """List all the assets

     Find assets by search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security Program Overview.
        sort (Union[Unset, AssetsPublicControllerListAssetsSort]):  Example: NAME.
        sort_dir (Union[Unset, AssetsPublicControllerListAssetsSortDir]):  Example: ASC.
        asset_class_type (Union[Unset, AssetsPublicControllerListAssetsAssetClassType]):  Example:
            DOCUMENT.
        asset_type (Union[Unset, AssetsPublicControllerListAssetsAssetType]):  Example: PHYSICAL.
        asset_provider (Union[Unset, AssetsPublicControllerListAssetsAssetProvider]):  Example:
            AGENT.
        user_id (Union[Unset, float]):  Example: 1.
        employment_status (Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AssetsResponsePublicDto, ExceptionResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        asset_class_type=asset_class_type,
        asset_type=asset_type,
        asset_provider=asset_provider,
        user_id=user_id,
        employment_status=employment_status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, AssetsPublicControllerListAssetsSort] = UNSET,
    sort_dir: Union[Unset, AssetsPublicControllerListAssetsSortDir] = UNSET,
    asset_class_type: Union[Unset, AssetsPublicControllerListAssetsAssetClassType] = UNSET,
    asset_type: Union[Unset, AssetsPublicControllerListAssetsAssetType] = UNSET,
    asset_provider: Union[Unset, AssetsPublicControllerListAssetsAssetProvider] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    employment_status: Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus] = UNSET,
) -> Optional[Union[AssetsResponsePublicDto, ExceptionResponseDto]]:
    """List all the assets

     Find assets by search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Security Program Overview.
        sort (Union[Unset, AssetsPublicControllerListAssetsSort]):  Example: NAME.
        sort_dir (Union[Unset, AssetsPublicControllerListAssetsSortDir]):  Example: ASC.
        asset_class_type (Union[Unset, AssetsPublicControllerListAssetsAssetClassType]):  Example:
            DOCUMENT.
        asset_type (Union[Unset, AssetsPublicControllerListAssetsAssetType]):  Example: PHYSICAL.
        asset_provider (Union[Unset, AssetsPublicControllerListAssetsAssetProvider]):  Example:
            AGENT.
        user_id (Union[Unset, float]):  Example: 1.
        employment_status (Union[Unset, AssetsPublicControllerListAssetsEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AssetsResponsePublicDto, ExceptionResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            sort=sort,
            sort_dir=sort_dir,
            asset_class_type=asset_class_type,
            asset_type=asset_type,
            asset_provider=asset_provider,
            user_id=user_id,
            employment_status=employment_status,
        )
    ).parsed
