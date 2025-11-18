from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.frameworks_public_controller_get_all_requirements_category_type_0_item import (
    FrameworksPublicControllerGetAllRequirementsCategoryType0Item,
)
from ...models.frameworks_public_controller_get_all_requirements_level import (
    FrameworksPublicControllerGetAllRequirementsLevel,
)
from ...models.frameworks_public_controller_get_all_requirements_sub_category_type_0_item import (
    FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item,
)
from ...models.frameworks_public_controller_get_all_requirements_topic_type_0_item import (
    FrameworksPublicControllerGetAllRequirementsTopicType0Item,
)
from ...models.requirement_paginated_response_public_dto import RequirementPaginatedResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    is_in_scope: Union[None, Unset, bool] = UNSET,
    is_ready: Union[None, Unset, bool] = UNSET,
    is_in_scope_controls: Union[None, Unset, bool] = UNSET,
    topic: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]] = UNSET,
    category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]] = UNSET,
    sub_category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]] = UNSET,
    level: Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel] = UNSET,
    custom_category: Union[None, Unset, str] = UNSET,
    framework_id: float,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    params["frameworkSlug"] = framework_slug

    json_exclude_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(exclude_ids, Unset):
        json_exclude_ids = exclude_ids

    params["excludeIds"] = json_exclude_ids

    params["excludeControlId"] = exclude_control_id

    json_is_in_scope: Union[None, Unset, bool]
    if isinstance(is_in_scope, Unset):
        json_is_in_scope = UNSET
    else:
        json_is_in_scope = is_in_scope
    params["isInScope"] = json_is_in_scope

    json_is_ready: Union[None, Unset, bool]
    if isinstance(is_ready, Unset):
        json_is_ready = UNSET
    else:
        json_is_ready = is_ready
    params["isReady"] = json_is_ready

    json_is_in_scope_controls: Union[None, Unset, bool]
    if isinstance(is_in_scope_controls, Unset):
        json_is_in_scope_controls = UNSET
    else:
        json_is_in_scope_controls = is_in_scope_controls
    params["isInScopeControls"] = json_is_in_scope_controls

    json_topic: Union[None, Unset, list[str]]
    if isinstance(topic, Unset):
        json_topic = UNSET
    elif isinstance(topic, list):
        json_topic = []
        for topic_type_0_item_data in topic:
            topic_type_0_item = topic_type_0_item_data.value
            json_topic.append(topic_type_0_item)

    else:
        json_topic = topic
    params["topic"] = json_topic

    json_category: Union[None, Unset, list[str]]
    if isinstance(category, Unset):
        json_category = UNSET
    elif isinstance(category, list):
        json_category = []
        for category_type_0_item_data in category:
            category_type_0_item = category_type_0_item_data.value
            json_category.append(category_type_0_item)

    else:
        json_category = category
    params["category"] = json_category

    json_sub_category: Union[None, Unset, list[str]]
    if isinstance(sub_category, Unset):
        json_sub_category = UNSET
    elif isinstance(sub_category, list):
        json_sub_category = []
        for sub_category_type_0_item_data in sub_category:
            sub_category_type_0_item = sub_category_type_0_item_data.value
            json_sub_category.append(sub_category_type_0_item)

    else:
        json_sub_category = sub_category
    params["subCategory"] = json_sub_category

    json_level: Union[Unset, str] = UNSET
    if not isinstance(level, Unset):
        json_level = level.value

    params["level"] = json_level

    json_custom_category: Union[None, Unset, str]
    if isinstance(custom_category, Unset):
        json_custom_category = UNSET
    else:
        json_custom_category = custom_category
    params["customCategory"] = json_custom_category

    params["frameworkId"] = framework_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/frameworks/requirements",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = RequirementPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
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
    framework_slug: Union[Unset, str] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    is_in_scope: Union[None, Unset, bool] = UNSET,
    is_ready: Union[None, Unset, bool] = UNSET,
    is_in_scope_controls: Union[None, Unset, bool] = UNSET,
    topic: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]] = UNSET,
    category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]] = UNSET,
    sub_category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]] = UNSET,
    level: Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel] = UNSET,
    custom_category: Union[None, Unset, str] = UNSET,
    framework_id: float,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
    """Find framework requirements by search terms and filters

     List framework requirements for the primary workspace, given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: A1.1.
        framework_slug (Union[Unset, str]):  Example: soc2.
        exclude_ids (Union[Unset, list[float]]):  Example: [1, 2].
        exclude_control_id (Union[Unset, float]):  Example: 1.
        is_in_scope (Union[None, Unset, bool]):
        is_ready (Union[None, Unset, bool]):
        is_in_scope_controls (Union[None, Unset, bool]):
        topic (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]]):  Example:
            ['ADMINISTRATIVE_SAFEGUARDS', 'AVAILABILITY'].
        category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'SOC_2_CONTROL_ACTIVITIES'].
        sub_category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]]):  Example:
            ['CODES_OF_CONDUCT_AND_CERTIFICATION',
            'ISO_COMPLIANCE_WITH_LEGAL_AND_CONTRACTUAL_REQUIREMENTS'].
        level (Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel]):  Example:
            SECURITY_HIGH.
        custom_category (Union[None, Unset, str]):  Example: Custom Category 1.
        framework_id (float):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        is_in_scope=is_in_scope,
        is_ready=is_ready,
        is_in_scope_controls=is_in_scope_controls,
        topic=topic,
        category=category,
        sub_category=sub_category,
        level=level,
        custom_category=custom_category,
        framework_id=framework_id,
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
    framework_slug: Union[Unset, str] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    is_in_scope: Union[None, Unset, bool] = UNSET,
    is_ready: Union[None, Unset, bool] = UNSET,
    is_in_scope_controls: Union[None, Unset, bool] = UNSET,
    topic: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]] = UNSET,
    category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]] = UNSET,
    sub_category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]] = UNSET,
    level: Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel] = UNSET,
    custom_category: Union[None, Unset, str] = UNSET,
    framework_id: float,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
    """Find framework requirements by search terms and filters

     List framework requirements for the primary workspace, given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: A1.1.
        framework_slug (Union[Unset, str]):  Example: soc2.
        exclude_ids (Union[Unset, list[float]]):  Example: [1, 2].
        exclude_control_id (Union[Unset, float]):  Example: 1.
        is_in_scope (Union[None, Unset, bool]):
        is_ready (Union[None, Unset, bool]):
        is_in_scope_controls (Union[None, Unset, bool]):
        topic (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]]):  Example:
            ['ADMINISTRATIVE_SAFEGUARDS', 'AVAILABILITY'].
        category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'SOC_2_CONTROL_ACTIVITIES'].
        sub_category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]]):  Example:
            ['CODES_OF_CONDUCT_AND_CERTIFICATION',
            'ISO_COMPLIANCE_WITH_LEGAL_AND_CONTRACTUAL_REQUIREMENTS'].
        level (Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel]):  Example:
            SECURITY_HIGH.
        custom_category (Union[None, Unset, str]):  Example: Custom Category 1.
        framework_id (float):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        is_in_scope=is_in_scope,
        is_ready=is_ready,
        is_in_scope_controls=is_in_scope_controls,
        topic=topic,
        category=category,
        sub_category=sub_category,
        level=level,
        custom_category=custom_category,
        framework_id=framework_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    is_in_scope: Union[None, Unset, bool] = UNSET,
    is_ready: Union[None, Unset, bool] = UNSET,
    is_in_scope_controls: Union[None, Unset, bool] = UNSET,
    topic: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]] = UNSET,
    category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]] = UNSET,
    sub_category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]] = UNSET,
    level: Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel] = UNSET,
    custom_category: Union[None, Unset, str] = UNSET,
    framework_id: float,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
    """Find framework requirements by search terms and filters

     List framework requirements for the primary workspace, given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: A1.1.
        framework_slug (Union[Unset, str]):  Example: soc2.
        exclude_ids (Union[Unset, list[float]]):  Example: [1, 2].
        exclude_control_id (Union[Unset, float]):  Example: 1.
        is_in_scope (Union[None, Unset, bool]):
        is_ready (Union[None, Unset, bool]):
        is_in_scope_controls (Union[None, Unset, bool]):
        topic (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]]):  Example:
            ['ADMINISTRATIVE_SAFEGUARDS', 'AVAILABILITY'].
        category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'SOC_2_CONTROL_ACTIVITIES'].
        sub_category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]]):  Example:
            ['CODES_OF_CONDUCT_AND_CERTIFICATION',
            'ISO_COMPLIANCE_WITH_LEGAL_AND_CONTRACTUAL_REQUIREMENTS'].
        level (Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel]):  Example:
            SECURITY_HIGH.
        custom_category (Union[None, Unset, str]):  Example: Custom Category 1.
        framework_id (float):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        framework_slug=framework_slug,
        exclude_ids=exclude_ids,
        exclude_control_id=exclude_control_id,
        is_in_scope=is_in_scope,
        is_ready=is_ready,
        is_in_scope_controls=is_in_scope_controls,
        topic=topic,
        category=category,
        sub_category=sub_category,
        level=level,
        custom_category=custom_category,
        framework_id=framework_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_control_id: Union[Unset, float] = UNSET,
    is_in_scope: Union[None, Unset, bool] = UNSET,
    is_ready: Union[None, Unset, bool] = UNSET,
    is_in_scope_controls: Union[None, Unset, bool] = UNSET,
    topic: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]] = UNSET,
    category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]] = UNSET,
    sub_category: Union[None, Unset, list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]] = UNSET,
    level: Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel] = UNSET,
    custom_category: Union[None, Unset, str] = UNSET,
    framework_id: float,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]]:
    """Find framework requirements by search terms and filters

     List framework requirements for the primary workspace, given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: A1.1.
        framework_slug (Union[Unset, str]):  Example: soc2.
        exclude_ids (Union[Unset, list[float]]):  Example: [1, 2].
        exclude_control_id (Union[Unset, float]):  Example: 1.
        is_in_scope (Union[None, Unset, bool]):
        is_ready (Union[None, Unset, bool]):
        is_in_scope_controls (Union[None, Unset, bool]):
        topic (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsTopicType0Item]]):  Example:
            ['ADMINISTRATIVE_SAFEGUARDS', 'AVAILABILITY'].
        category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsCategoryType0Item]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'SOC_2_CONTROL_ACTIVITIES'].
        sub_category (Union[None, Unset,
            list[FrameworksPublicControllerGetAllRequirementsSubCategoryType0Item]]):  Example:
            ['CODES_OF_CONDUCT_AND_CERTIFICATION',
            'ISO_COMPLIANCE_WITH_LEGAL_AND_CONTRACTUAL_REQUIREMENTS'].
        level (Union[Unset, FrameworksPublicControllerGetAllRequirementsLevel]):  Example:
            SECURITY_HIGH.
        custom_category (Union[None, Unset, str]):  Example: Custom Category 1.
        framework_id (float):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, RequirementPaginatedResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            framework_slug=framework_slug,
            exclude_ids=exclude_ids,
            exclude_control_id=exclude_control_id,
            is_in_scope=is_in_scope,
            is_ready=is_ready,
            is_in_scope_controls=is_in_scope_controls,
            topic=topic,
            category=category,
            sub_category=sub_category,
            level=level,
            custom_category=custom_category,
            framework_id=framework_id,
        )
    ).parsed
