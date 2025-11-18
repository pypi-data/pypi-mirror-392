from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.vendors_public_controller_list_vendors_category import VendorsPublicControllerListVendorsCategory
from ...models.vendors_public_controller_list_vendors_impact_level import VendorsPublicControllerListVendorsImpactLevel
from ...models.vendors_public_controller_list_vendors_next_review_deadline_status import (
    VendorsPublicControllerListVendorsNextReviewDeadlineStatus,
)
from ...models.vendors_public_controller_list_vendors_password_policy import (
    VendorsPublicControllerListVendorsPasswordPolicy,
)
from ...models.vendors_public_controller_list_vendors_renewal_date_status import (
    VendorsPublicControllerListVendorsRenewalDateStatus,
)
from ...models.vendors_public_controller_list_vendors_renewal_schedule_type import (
    VendorsPublicControllerListVendorsRenewalScheduleType,
)
from ...models.vendors_public_controller_list_vendors_risk import VendorsPublicControllerListVendorsRisk
from ...models.vendors_public_controller_list_vendors_scheduled_questionnaire_status import (
    VendorsPublicControllerListVendorsScheduledQuestionnaireStatus,
)
from ...models.vendors_public_controller_list_vendors_security_review_status import (
    VendorsPublicControllerListVendorsSecurityReviewStatus,
)
from ...models.vendors_public_controller_list_vendors_sort import VendorsPublicControllerListVendorsSort
from ...models.vendors_public_controller_list_vendors_sort_dir import VendorsPublicControllerListVendorsSortDir
from ...models.vendors_public_controller_list_vendors_status import VendorsPublicControllerListVendorsStatus
from ...models.vendors_public_controller_list_vendors_type import VendorsPublicControllerListVendorsType
from ...models.vendors_response_public_dto import VendorsResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, VendorsPublicControllerListVendorsSort] = UNSET,
    sort_dir: Union[Unset, VendorsPublicControllerListVendorsSortDir] = UNSET,
    category: Union[Unset, VendorsPublicControllerListVendorsCategory] = UNSET,
    risk: Union[Unset, VendorsPublicControllerListVendorsRisk] = UNSET,
    status: Union[Unset, VendorsPublicControllerListVendorsStatus] = UNSET,
    contact_email: Union[Unset, str] = UNSET,
    contact_name: Union[Unset, str] = UNSET,
    critical: Union[Unset, bool] = UNSET,
    password_policy: Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    with_last_questionnaires: Union[Unset, bool] = UNSET,
    type_: Union[Unset, VendorsPublicControllerListVendorsType] = UNSET,
    impact_level: Union[Unset, VendorsPublicControllerListVendorsImpactLevel] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    renewal_date: Union[Unset, str] = UNSET,
    renewal_schedule_type: Union[Unset, VendorsPublicControllerListVendorsRenewalScheduleType] = UNSET,
    renewal_date_status: Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus] = UNSET,
    next_review_deadline_status: Union[Unset, VendorsPublicControllerListVendorsNextReviewDeadlineStatus] = UNSET,
    scheduled_questionnaire_status: Union[
        Unset, VendorsPublicControllerListVendorsScheduledQuestionnaireStatus
    ] = UNSET,
    security_review_status: Union[Unset, VendorsPublicControllerListVendorsSecurityReviewStatus] = UNSET,
    shared_account_id: Union[Unset, str] = UNSET,
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

    json_category: Union[Unset, str] = UNSET
    if not isinstance(category, Unset):
        json_category = category.value

    params["category"] = json_category

    json_risk: Union[Unset, str] = UNSET
    if not isinstance(risk, Unset):
        json_risk = risk.value

    params["risk"] = json_risk

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["contactEmail"] = contact_email

    params["contactName"] = contact_name

    params["critical"] = critical

    json_password_policy: Union[Unset, str] = UNSET
    if not isinstance(password_policy, Unset):
        json_password_policy = password_policy.value

    params["passwordPolicy"] = json_password_policy

    params["userId"] = user_id

    params["withLastQuestionnaires"] = with_last_questionnaires

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    json_impact_level: Union[Unset, str] = UNSET
    if not isinstance(impact_level, Unset):
        json_impact_level = impact_level.value

    params["impactLevel"] = json_impact_level

    params["isArchived"] = is_archived

    params["renewalDate"] = renewal_date

    json_renewal_schedule_type: Union[Unset, str] = UNSET
    if not isinstance(renewal_schedule_type, Unset):
        json_renewal_schedule_type = renewal_schedule_type.value

    params["renewalScheduleType"] = json_renewal_schedule_type

    json_renewal_date_status: Union[Unset, str] = UNSET
    if not isinstance(renewal_date_status, Unset):
        json_renewal_date_status = renewal_date_status.value

    params["renewalDateStatus"] = json_renewal_date_status

    json_next_review_deadline_status: Union[Unset, str] = UNSET
    if not isinstance(next_review_deadline_status, Unset):
        json_next_review_deadline_status = next_review_deadline_status.value

    params["nextReviewDeadlineStatus"] = json_next_review_deadline_status

    json_scheduled_questionnaire_status: Union[Unset, str] = UNSET
    if not isinstance(scheduled_questionnaire_status, Unset):
        json_scheduled_questionnaire_status = scheduled_questionnaire_status.value

    params["scheduledQuestionnaireStatus"] = json_scheduled_questionnaire_status

    json_security_review_status: Union[Unset, str] = UNSET
    if not isinstance(security_review_status, Unset):
        json_security_review_status = security_review_status.value

    params["securityReviewStatus"] = json_security_review_status

    params["sharedAccountId"] = shared_account_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/vendors",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = VendorsResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
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
    sort: Union[Unset, VendorsPublicControllerListVendorsSort] = UNSET,
    sort_dir: Union[Unset, VendorsPublicControllerListVendorsSortDir] = UNSET,
    category: Union[Unset, VendorsPublicControllerListVendorsCategory] = UNSET,
    risk: Union[Unset, VendorsPublicControllerListVendorsRisk] = UNSET,
    status: Union[Unset, VendorsPublicControllerListVendorsStatus] = UNSET,
    contact_email: Union[Unset, str] = UNSET,
    contact_name: Union[Unset, str] = UNSET,
    critical: Union[Unset, bool] = UNSET,
    password_policy: Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    with_last_questionnaires: Union[Unset, bool] = UNSET,
    type_: Union[Unset, VendorsPublicControllerListVendorsType] = UNSET,
    impact_level: Union[Unset, VendorsPublicControllerListVendorsImpactLevel] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    renewal_date: Union[Unset, str] = UNSET,
    renewal_schedule_type: Union[Unset, VendorsPublicControllerListVendorsRenewalScheduleType] = UNSET,
    renewal_date_status: Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus] = UNSET,
    next_review_deadline_status: Union[Unset, VendorsPublicControllerListVendorsNextReviewDeadlineStatus] = UNSET,
    scheduled_questionnaire_status: Union[
        Unset, VendorsPublicControllerListVendorsScheduledQuestionnaireStatus
    ] = UNSET,
    security_review_status: Union[Unset, VendorsPublicControllerListVendorsSecurityReviewStatus] = UNSET,
    shared_account_id: Union[Unset, str] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
    """Find vendors by search terms and filters

     List vendors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acme.
        sort (Union[Unset, VendorsPublicControllerListVendorsSort]):  Example: NAME.
        sort_dir (Union[Unset, VendorsPublicControllerListVendorsSortDir]):  Example: ASC.
        category (Union[Unset, VendorsPublicControllerListVendorsCategory]):  Example:
            ENGINEERING.
        risk (Union[Unset, VendorsPublicControllerListVendorsRisk]):  Example: MODERATE.
        status (Union[Unset, VendorsPublicControllerListVendorsStatus]):  Example: UNDER_REVIEW.
        contact_email (Union[Unset, str]):  Example: user@vendor.com.
        contact_name (Union[Unset, str]):  Example: John Doe.
        critical (Union[Unset, bool]):
        password_policy (Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy]):
            Example: USERNAME_PASSWORD.
        user_id (Union[Unset, float]):  Example: 1.
        with_last_questionnaires (Union[Unset, bool]):
        type_ (Union[Unset, VendorsPublicControllerListVendorsType]):  Example: CONTRACTOR.
        impact_level (Union[Unset, VendorsPublicControllerListVendorsImpactLevel]):  Example:
            INSIGNIFICANT.
        is_archived (Union[Unset, bool]):
        renewal_date (Union[Unset, str]):  Example: 2025-07-01T16:45:55.246Z.
        renewal_schedule_type (Union[Unset,
            VendorsPublicControllerListVendorsRenewalScheduleType]):  Example: ONE_YEAR.
        renewal_date_status (Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus]):
            Example: COMPLETED.
        next_review_deadline_status (Union[Unset,
            VendorsPublicControllerListVendorsNextReviewDeadlineStatus]):  Example: NO_RENEWAL.
        scheduled_questionnaire_status (Union[Unset,
            VendorsPublicControllerListVendorsScheduledQuestionnaireStatus]):  Example: ENABLED.
        security_review_status (Union[Unset,
            VendorsPublicControllerListVendorsSecurityReviewStatus]):  Example: NO_SECURITY.
        shared_account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        category=category,
        risk=risk,
        status=status,
        contact_email=contact_email,
        contact_name=contact_name,
        critical=critical,
        password_policy=password_policy,
        user_id=user_id,
        with_last_questionnaires=with_last_questionnaires,
        type_=type_,
        impact_level=impact_level,
        is_archived=is_archived,
        renewal_date=renewal_date,
        renewal_schedule_type=renewal_schedule_type,
        renewal_date_status=renewal_date_status,
        next_review_deadline_status=next_review_deadline_status,
        scheduled_questionnaire_status=scheduled_questionnaire_status,
        security_review_status=security_review_status,
        shared_account_id=shared_account_id,
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
    sort: Union[Unset, VendorsPublicControllerListVendorsSort] = UNSET,
    sort_dir: Union[Unset, VendorsPublicControllerListVendorsSortDir] = UNSET,
    category: Union[Unset, VendorsPublicControllerListVendorsCategory] = UNSET,
    risk: Union[Unset, VendorsPublicControllerListVendorsRisk] = UNSET,
    status: Union[Unset, VendorsPublicControllerListVendorsStatus] = UNSET,
    contact_email: Union[Unset, str] = UNSET,
    contact_name: Union[Unset, str] = UNSET,
    critical: Union[Unset, bool] = UNSET,
    password_policy: Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    with_last_questionnaires: Union[Unset, bool] = UNSET,
    type_: Union[Unset, VendorsPublicControllerListVendorsType] = UNSET,
    impact_level: Union[Unset, VendorsPublicControllerListVendorsImpactLevel] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    renewal_date: Union[Unset, str] = UNSET,
    renewal_schedule_type: Union[Unset, VendorsPublicControllerListVendorsRenewalScheduleType] = UNSET,
    renewal_date_status: Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus] = UNSET,
    next_review_deadline_status: Union[Unset, VendorsPublicControllerListVendorsNextReviewDeadlineStatus] = UNSET,
    scheduled_questionnaire_status: Union[
        Unset, VendorsPublicControllerListVendorsScheduledQuestionnaireStatus
    ] = UNSET,
    security_review_status: Union[Unset, VendorsPublicControllerListVendorsSecurityReviewStatus] = UNSET,
    shared_account_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
    """Find vendors by search terms and filters

     List vendors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acme.
        sort (Union[Unset, VendorsPublicControllerListVendorsSort]):  Example: NAME.
        sort_dir (Union[Unset, VendorsPublicControllerListVendorsSortDir]):  Example: ASC.
        category (Union[Unset, VendorsPublicControllerListVendorsCategory]):  Example:
            ENGINEERING.
        risk (Union[Unset, VendorsPublicControllerListVendorsRisk]):  Example: MODERATE.
        status (Union[Unset, VendorsPublicControllerListVendorsStatus]):  Example: UNDER_REVIEW.
        contact_email (Union[Unset, str]):  Example: user@vendor.com.
        contact_name (Union[Unset, str]):  Example: John Doe.
        critical (Union[Unset, bool]):
        password_policy (Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy]):
            Example: USERNAME_PASSWORD.
        user_id (Union[Unset, float]):  Example: 1.
        with_last_questionnaires (Union[Unset, bool]):
        type_ (Union[Unset, VendorsPublicControllerListVendorsType]):  Example: CONTRACTOR.
        impact_level (Union[Unset, VendorsPublicControllerListVendorsImpactLevel]):  Example:
            INSIGNIFICANT.
        is_archived (Union[Unset, bool]):
        renewal_date (Union[Unset, str]):  Example: 2025-07-01T16:45:55.246Z.
        renewal_schedule_type (Union[Unset,
            VendorsPublicControllerListVendorsRenewalScheduleType]):  Example: ONE_YEAR.
        renewal_date_status (Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus]):
            Example: COMPLETED.
        next_review_deadline_status (Union[Unset,
            VendorsPublicControllerListVendorsNextReviewDeadlineStatus]):  Example: NO_RENEWAL.
        scheduled_questionnaire_status (Union[Unset,
            VendorsPublicControllerListVendorsScheduledQuestionnaireStatus]):  Example: ENABLED.
        security_review_status (Union[Unset,
            VendorsPublicControllerListVendorsSecurityReviewStatus]):  Example: NO_SECURITY.
        shared_account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        category=category,
        risk=risk,
        status=status,
        contact_email=contact_email,
        contact_name=contact_name,
        critical=critical,
        password_policy=password_policy,
        user_id=user_id,
        with_last_questionnaires=with_last_questionnaires,
        type_=type_,
        impact_level=impact_level,
        is_archived=is_archived,
        renewal_date=renewal_date,
        renewal_schedule_type=renewal_schedule_type,
        renewal_date_status=renewal_date_status,
        next_review_deadline_status=next_review_deadline_status,
        scheduled_questionnaire_status=scheduled_questionnaire_status,
        security_review_status=security_review_status,
        shared_account_id=shared_account_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, VendorsPublicControllerListVendorsSort] = UNSET,
    sort_dir: Union[Unset, VendorsPublicControllerListVendorsSortDir] = UNSET,
    category: Union[Unset, VendorsPublicControllerListVendorsCategory] = UNSET,
    risk: Union[Unset, VendorsPublicControllerListVendorsRisk] = UNSET,
    status: Union[Unset, VendorsPublicControllerListVendorsStatus] = UNSET,
    contact_email: Union[Unset, str] = UNSET,
    contact_name: Union[Unset, str] = UNSET,
    critical: Union[Unset, bool] = UNSET,
    password_policy: Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    with_last_questionnaires: Union[Unset, bool] = UNSET,
    type_: Union[Unset, VendorsPublicControllerListVendorsType] = UNSET,
    impact_level: Union[Unset, VendorsPublicControllerListVendorsImpactLevel] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    renewal_date: Union[Unset, str] = UNSET,
    renewal_schedule_type: Union[Unset, VendorsPublicControllerListVendorsRenewalScheduleType] = UNSET,
    renewal_date_status: Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus] = UNSET,
    next_review_deadline_status: Union[Unset, VendorsPublicControllerListVendorsNextReviewDeadlineStatus] = UNSET,
    scheduled_questionnaire_status: Union[
        Unset, VendorsPublicControllerListVendorsScheduledQuestionnaireStatus
    ] = UNSET,
    security_review_status: Union[Unset, VendorsPublicControllerListVendorsSecurityReviewStatus] = UNSET,
    shared_account_id: Union[Unset, str] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
    """Find vendors by search terms and filters

     List vendors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acme.
        sort (Union[Unset, VendorsPublicControllerListVendorsSort]):  Example: NAME.
        sort_dir (Union[Unset, VendorsPublicControllerListVendorsSortDir]):  Example: ASC.
        category (Union[Unset, VendorsPublicControllerListVendorsCategory]):  Example:
            ENGINEERING.
        risk (Union[Unset, VendorsPublicControllerListVendorsRisk]):  Example: MODERATE.
        status (Union[Unset, VendorsPublicControllerListVendorsStatus]):  Example: UNDER_REVIEW.
        contact_email (Union[Unset, str]):  Example: user@vendor.com.
        contact_name (Union[Unset, str]):  Example: John Doe.
        critical (Union[Unset, bool]):
        password_policy (Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy]):
            Example: USERNAME_PASSWORD.
        user_id (Union[Unset, float]):  Example: 1.
        with_last_questionnaires (Union[Unset, bool]):
        type_ (Union[Unset, VendorsPublicControllerListVendorsType]):  Example: CONTRACTOR.
        impact_level (Union[Unset, VendorsPublicControllerListVendorsImpactLevel]):  Example:
            INSIGNIFICANT.
        is_archived (Union[Unset, bool]):
        renewal_date (Union[Unset, str]):  Example: 2025-07-01T16:45:55.246Z.
        renewal_schedule_type (Union[Unset,
            VendorsPublicControllerListVendorsRenewalScheduleType]):  Example: ONE_YEAR.
        renewal_date_status (Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus]):
            Example: COMPLETED.
        next_review_deadline_status (Union[Unset,
            VendorsPublicControllerListVendorsNextReviewDeadlineStatus]):  Example: NO_RENEWAL.
        scheduled_questionnaire_status (Union[Unset,
            VendorsPublicControllerListVendorsScheduledQuestionnaireStatus]):  Example: ENABLED.
        security_review_status (Union[Unset,
            VendorsPublicControllerListVendorsSecurityReviewStatus]):  Example: NO_SECURITY.
        shared_account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        category=category,
        risk=risk,
        status=status,
        contact_email=contact_email,
        contact_name=contact_name,
        critical=critical,
        password_policy=password_policy,
        user_id=user_id,
        with_last_questionnaires=with_last_questionnaires,
        type_=type_,
        impact_level=impact_level,
        is_archived=is_archived,
        renewal_date=renewal_date,
        renewal_schedule_type=renewal_schedule_type,
        renewal_date_status=renewal_date_status,
        next_review_deadline_status=next_review_deadline_status,
        scheduled_questionnaire_status=scheduled_questionnaire_status,
        security_review_status=security_review_status,
        shared_account_id=shared_account_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    sort: Union[Unset, VendorsPublicControllerListVendorsSort] = UNSET,
    sort_dir: Union[Unset, VendorsPublicControllerListVendorsSortDir] = UNSET,
    category: Union[Unset, VendorsPublicControllerListVendorsCategory] = UNSET,
    risk: Union[Unset, VendorsPublicControllerListVendorsRisk] = UNSET,
    status: Union[Unset, VendorsPublicControllerListVendorsStatus] = UNSET,
    contact_email: Union[Unset, str] = UNSET,
    contact_name: Union[Unset, str] = UNSET,
    critical: Union[Unset, bool] = UNSET,
    password_policy: Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy] = UNSET,
    user_id: Union[Unset, float] = UNSET,
    with_last_questionnaires: Union[Unset, bool] = UNSET,
    type_: Union[Unset, VendorsPublicControllerListVendorsType] = UNSET,
    impact_level: Union[Unset, VendorsPublicControllerListVendorsImpactLevel] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    renewal_date: Union[Unset, str] = UNSET,
    renewal_schedule_type: Union[Unset, VendorsPublicControllerListVendorsRenewalScheduleType] = UNSET,
    renewal_date_status: Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus] = UNSET,
    next_review_deadline_status: Union[Unset, VendorsPublicControllerListVendorsNextReviewDeadlineStatus] = UNSET,
    scheduled_questionnaire_status: Union[
        Unset, VendorsPublicControllerListVendorsScheduledQuestionnaireStatus
    ] = UNSET,
    security_review_status: Union[Unset, VendorsPublicControllerListVendorsSecurityReviewStatus] = UNSET,
    shared_account_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]]:
    """Find vendors by search terms and filters

     List vendors given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Acme.
        sort (Union[Unset, VendorsPublicControllerListVendorsSort]):  Example: NAME.
        sort_dir (Union[Unset, VendorsPublicControllerListVendorsSortDir]):  Example: ASC.
        category (Union[Unset, VendorsPublicControllerListVendorsCategory]):  Example:
            ENGINEERING.
        risk (Union[Unset, VendorsPublicControllerListVendorsRisk]):  Example: MODERATE.
        status (Union[Unset, VendorsPublicControllerListVendorsStatus]):  Example: UNDER_REVIEW.
        contact_email (Union[Unset, str]):  Example: user@vendor.com.
        contact_name (Union[Unset, str]):  Example: John Doe.
        critical (Union[Unset, bool]):
        password_policy (Union[Unset, VendorsPublicControllerListVendorsPasswordPolicy]):
            Example: USERNAME_PASSWORD.
        user_id (Union[Unset, float]):  Example: 1.
        with_last_questionnaires (Union[Unset, bool]):
        type_ (Union[Unset, VendorsPublicControllerListVendorsType]):  Example: CONTRACTOR.
        impact_level (Union[Unset, VendorsPublicControllerListVendorsImpactLevel]):  Example:
            INSIGNIFICANT.
        is_archived (Union[Unset, bool]):
        renewal_date (Union[Unset, str]):  Example: 2025-07-01T16:45:55.246Z.
        renewal_schedule_type (Union[Unset,
            VendorsPublicControllerListVendorsRenewalScheduleType]):  Example: ONE_YEAR.
        renewal_date_status (Union[Unset, VendorsPublicControllerListVendorsRenewalDateStatus]):
            Example: COMPLETED.
        next_review_deadline_status (Union[Unset,
            VendorsPublicControllerListVendorsNextReviewDeadlineStatus]):  Example: NO_RENEWAL.
        scheduled_questionnaire_status (Union[Unset,
            VendorsPublicControllerListVendorsScheduledQuestionnaireStatus]):  Example: ENABLED.
        security_review_status (Union[Unset,
            VendorsPublicControllerListVendorsSecurityReviewStatus]):  Example: NO_SECURITY.
        shared_account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, VendorsResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            sort=sort,
            sort_dir=sort_dir,
            category=category,
            risk=risk,
            status=status,
            contact_email=contact_email,
            contact_name=contact_name,
            critical=critical,
            password_policy=password_policy,
            user_id=user_id,
            with_last_questionnaires=with_last_questionnaires,
            type_=type_,
            impact_level=impact_level,
            is_archived=is_archived,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            renewal_date_status=renewal_date_status,
            next_review_deadline_status=next_review_deadline_status,
            scheduled_questionnaire_status=scheduled_questionnaire_status,
            security_review_status=security_review_status,
            shared_account_id=shared_account_id,
        )
    ).parsed
