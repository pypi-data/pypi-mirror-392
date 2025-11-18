from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.personnel_public_controller_list_personnel_employment_status import (
    PersonnelPublicControllerListPersonnelEmploymentStatus,
)
from ...models.personnel_public_controller_list_personnel_employment_statuses_item import (
    PersonnelPublicControllerListPersonnelEmploymentStatusesItem,
)
from ...models.personnel_public_controller_list_personnel_inverse_mdm_source_types_item import (
    PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem,
)
from ...models.personnel_public_controller_list_personnel_mdm_source_type import (
    PersonnelPublicControllerListPersonnelMdmSourceType,
)
from ...models.personnel_public_controller_list_personnel_multi_training_compliance_type import (
    PersonnelPublicControllerListPersonnelMultiTrainingComplianceType,
)
from ...models.personnel_public_controller_list_personnel_sort import PersonnelPublicControllerListPersonnelSort
from ...models.personnel_public_controller_list_personnel_sort_dir import PersonnelPublicControllerListPersonnelSortDir
from ...models.personnel_table_response_public_dto import PersonnelTableResponsePublicDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    employment_status: Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus] = UNSET,
    employment_statuses: Union[Unset, list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]] = UNSET,
    full_compliance: Union[Unset, bool] = UNSET,
    accepted_policies_compliance: Union[Unset, bool] = UNSET,
    identity_mfa_compliance: Union[Unset, bool] = UNSET,
    bg_check_compliance: Union[Unset, bool] = UNSET,
    agent_installed_compliance: Union[Unset, bool] = UNSET,
    password_manager_compliance: Union[Unset, bool] = UNSET,
    auto_updates_compliance: Union[Unset, bool] = UNSET,
    location_services_compliance: Union[Unset, bool] = UNSET,
    hd_encryption_compliance: Union[Unset, bool] = UNSET,
    antivirus_compliance: Union[Unset, bool] = UNSET,
    lock_screen_compliance: Union[Unset, bool] = UNSET,
    security_training_compliance: Union[Unset, bool] = UNSET,
    hipaa_training_compliance: Union[Unset, bool] = UNSET,
    nistai_training_compliance: Union[Unset, bool] = UNSET,
    device_compliance: Union[Unset, bool] = UNSET,
    multi_security_training_compliance: Union[Unset, bool] = UNSET,
    multi_training_compliance_type: Union[
        Unset, PersonnelPublicControllerListPersonnelMultiTrainingComplianceType
    ] = UNSET,
    offboarding_evidence: Union[Unset, bool] = UNSET,
    group_ids: Union[Unset, list[float]] = UNSET,
    sort: Union[Unset, PersonnelPublicControllerListPersonnelSort] = UNSET,
    sort_dir: Union[Unset, PersonnelPublicControllerListPersonnelSortDir] = UNSET,
    mdm_source_type: Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType] = UNSET,
    inverse_mdm_source_types: Union[
        Unset, list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]
    ] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_employment_status: Union[Unset, str] = UNSET
    if not isinstance(employment_status, Unset):
        json_employment_status = employment_status.value

    params["employmentStatus"] = json_employment_status

    json_employment_statuses: Union[Unset, list[str]] = UNSET
    if not isinstance(employment_statuses, Unset):
        json_employment_statuses = []
        for employment_statuses_item_data in employment_statuses:
            employment_statuses_item = employment_statuses_item_data.value
            json_employment_statuses.append(employment_statuses_item)

    params["employmentStatuses[]"] = json_employment_statuses

    params["fullCompliance"] = full_compliance

    params["acceptedPoliciesCompliance"] = accepted_policies_compliance

    params["identityMfaCompliance"] = identity_mfa_compliance

    params["bgCheckCompliance"] = bg_check_compliance

    params["agentInstalledCompliance"] = agent_installed_compliance

    params["passwordManagerCompliance"] = password_manager_compliance

    params["autoUpdatesCompliance"] = auto_updates_compliance

    params["locationServicesCompliance"] = location_services_compliance

    params["hdEncryptionCompliance"] = hd_encryption_compliance

    params["antivirusCompliance"] = antivirus_compliance

    params["lockScreenCompliance"] = lock_screen_compliance

    params["securityTrainingCompliance"] = security_training_compliance

    params["hipaaTrainingCompliance"] = hipaa_training_compliance

    params["nistaiTrainingCompliance"] = nistai_training_compliance

    params["deviceCompliance"] = device_compliance

    params["multiSecurityTrainingCompliance"] = multi_security_training_compliance

    json_multi_training_compliance_type: Union[Unset, str] = UNSET
    if not isinstance(multi_training_compliance_type, Unset):
        json_multi_training_compliance_type = multi_training_compliance_type.value

    params["multiTrainingComplianceType"] = json_multi_training_compliance_type

    params["offboardingEvidence"] = offboarding_evidence

    json_group_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(group_ids, Unset):
        json_group_ids = group_ids

    params["groupIds"] = json_group_ids

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sortDir"] = json_sort_dir

    json_mdm_source_type: Union[Unset, str] = UNSET
    if not isinstance(mdm_source_type, Unset):
        json_mdm_source_type = mdm_source_type.value

    params["mdmSourceType"] = json_mdm_source_type

    json_inverse_mdm_source_types: Union[Unset, list[str]] = UNSET
    if not isinstance(inverse_mdm_source_types, Unset):
        json_inverse_mdm_source_types = []
        for inverse_mdm_source_types_item_data in inverse_mdm_source_types:
            inverse_mdm_source_types_item = inverse_mdm_source_types_item_data.value
            json_inverse_mdm_source_types.append(inverse_mdm_source_types_item)

    params["inverseMdmSourceTypes[]"] = json_inverse_mdm_source_types

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/personnel",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = PersonnelTableResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
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
    employment_status: Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus] = UNSET,
    employment_statuses: Union[Unset, list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]] = UNSET,
    full_compliance: Union[Unset, bool] = UNSET,
    accepted_policies_compliance: Union[Unset, bool] = UNSET,
    identity_mfa_compliance: Union[Unset, bool] = UNSET,
    bg_check_compliance: Union[Unset, bool] = UNSET,
    agent_installed_compliance: Union[Unset, bool] = UNSET,
    password_manager_compliance: Union[Unset, bool] = UNSET,
    auto_updates_compliance: Union[Unset, bool] = UNSET,
    location_services_compliance: Union[Unset, bool] = UNSET,
    hd_encryption_compliance: Union[Unset, bool] = UNSET,
    antivirus_compliance: Union[Unset, bool] = UNSET,
    lock_screen_compliance: Union[Unset, bool] = UNSET,
    security_training_compliance: Union[Unset, bool] = UNSET,
    hipaa_training_compliance: Union[Unset, bool] = UNSET,
    nistai_training_compliance: Union[Unset, bool] = UNSET,
    device_compliance: Union[Unset, bool] = UNSET,
    multi_security_training_compliance: Union[Unset, bool] = UNSET,
    multi_training_compliance_type: Union[
        Unset, PersonnelPublicControllerListPersonnelMultiTrainingComplianceType
    ] = UNSET,
    offboarding_evidence: Union[Unset, bool] = UNSET,
    group_ids: Union[Unset, list[float]] = UNSET,
    sort: Union[Unset, PersonnelPublicControllerListPersonnelSort] = UNSET,
    sort_dir: Union[Unset, PersonnelPublicControllerListPersonnelSortDir] = UNSET,
    mdm_source_type: Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType] = UNSET,
    inverse_mdm_source_types: Union[
        Unset, list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]
    ] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
    """Find personnel by search terms and filters

     List personnel given the search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        employment_status (Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.
        employment_statuses (Union[Unset,
            list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]]):  Example:
            ['CURRENT_EMPLOYEE'].
        full_compliance (Union[Unset, bool]):
        accepted_policies_compliance (Union[Unset, bool]):
        identity_mfa_compliance (Union[Unset, bool]):
        bg_check_compliance (Union[Unset, bool]):
        agent_installed_compliance (Union[Unset, bool]):
        password_manager_compliance (Union[Unset, bool]):
        auto_updates_compliance (Union[Unset, bool]):
        location_services_compliance (Union[Unset, bool]):
        hd_encryption_compliance (Union[Unset, bool]):
        antivirus_compliance (Union[Unset, bool]):
        lock_screen_compliance (Union[Unset, bool]):
        security_training_compliance (Union[Unset, bool]):
        hipaa_training_compliance (Union[Unset, bool]):
        nistai_training_compliance (Union[Unset, bool]):
        device_compliance (Union[Unset, bool]):
        multi_security_training_compliance (Union[Unset, bool]):
        multi_training_compliance_type (Union[Unset,
            PersonnelPublicControllerListPersonnelMultiTrainingComplianceType]):  Example:
            SECURITY_TRAINING.
        offboarding_evidence (Union[Unset, bool]):
        group_ids (Union[Unset, list[float]]):
        sort (Union[Unset, PersonnelPublicControllerListPersonnelSort]):  Example: NAME.
        sort_dir (Union[Unset, PersonnelPublicControllerListPersonnelSortDir]):  Example: ASC.
        mdm_source_type (Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType]):
            Example: AGENT.
        inverse_mdm_source_types (Union[Unset,
            list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]]):  Example:
            ['AGENT'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        employment_status=employment_status,
        employment_statuses=employment_statuses,
        full_compliance=full_compliance,
        accepted_policies_compliance=accepted_policies_compliance,
        identity_mfa_compliance=identity_mfa_compliance,
        bg_check_compliance=bg_check_compliance,
        agent_installed_compliance=agent_installed_compliance,
        password_manager_compliance=password_manager_compliance,
        auto_updates_compliance=auto_updates_compliance,
        location_services_compliance=location_services_compliance,
        hd_encryption_compliance=hd_encryption_compliance,
        antivirus_compliance=antivirus_compliance,
        lock_screen_compliance=lock_screen_compliance,
        security_training_compliance=security_training_compliance,
        hipaa_training_compliance=hipaa_training_compliance,
        nistai_training_compliance=nistai_training_compliance,
        device_compliance=device_compliance,
        multi_security_training_compliance=multi_security_training_compliance,
        multi_training_compliance_type=multi_training_compliance_type,
        offboarding_evidence=offboarding_evidence,
        group_ids=group_ids,
        sort=sort,
        sort_dir=sort_dir,
        mdm_source_type=mdm_source_type,
        inverse_mdm_source_types=inverse_mdm_source_types,
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
    employment_status: Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus] = UNSET,
    employment_statuses: Union[Unset, list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]] = UNSET,
    full_compliance: Union[Unset, bool] = UNSET,
    accepted_policies_compliance: Union[Unset, bool] = UNSET,
    identity_mfa_compliance: Union[Unset, bool] = UNSET,
    bg_check_compliance: Union[Unset, bool] = UNSET,
    agent_installed_compliance: Union[Unset, bool] = UNSET,
    password_manager_compliance: Union[Unset, bool] = UNSET,
    auto_updates_compliance: Union[Unset, bool] = UNSET,
    location_services_compliance: Union[Unset, bool] = UNSET,
    hd_encryption_compliance: Union[Unset, bool] = UNSET,
    antivirus_compliance: Union[Unset, bool] = UNSET,
    lock_screen_compliance: Union[Unset, bool] = UNSET,
    security_training_compliance: Union[Unset, bool] = UNSET,
    hipaa_training_compliance: Union[Unset, bool] = UNSET,
    nistai_training_compliance: Union[Unset, bool] = UNSET,
    device_compliance: Union[Unset, bool] = UNSET,
    multi_security_training_compliance: Union[Unset, bool] = UNSET,
    multi_training_compliance_type: Union[
        Unset, PersonnelPublicControllerListPersonnelMultiTrainingComplianceType
    ] = UNSET,
    offboarding_evidence: Union[Unset, bool] = UNSET,
    group_ids: Union[Unset, list[float]] = UNSET,
    sort: Union[Unset, PersonnelPublicControllerListPersonnelSort] = UNSET,
    sort_dir: Union[Unset, PersonnelPublicControllerListPersonnelSortDir] = UNSET,
    mdm_source_type: Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType] = UNSET,
    inverse_mdm_source_types: Union[
        Unset, list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]
    ] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
    """Find personnel by search terms and filters

     List personnel given the search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        employment_status (Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.
        employment_statuses (Union[Unset,
            list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]]):  Example:
            ['CURRENT_EMPLOYEE'].
        full_compliance (Union[Unset, bool]):
        accepted_policies_compliance (Union[Unset, bool]):
        identity_mfa_compliance (Union[Unset, bool]):
        bg_check_compliance (Union[Unset, bool]):
        agent_installed_compliance (Union[Unset, bool]):
        password_manager_compliance (Union[Unset, bool]):
        auto_updates_compliance (Union[Unset, bool]):
        location_services_compliance (Union[Unset, bool]):
        hd_encryption_compliance (Union[Unset, bool]):
        antivirus_compliance (Union[Unset, bool]):
        lock_screen_compliance (Union[Unset, bool]):
        security_training_compliance (Union[Unset, bool]):
        hipaa_training_compliance (Union[Unset, bool]):
        nistai_training_compliance (Union[Unset, bool]):
        device_compliance (Union[Unset, bool]):
        multi_security_training_compliance (Union[Unset, bool]):
        multi_training_compliance_type (Union[Unset,
            PersonnelPublicControllerListPersonnelMultiTrainingComplianceType]):  Example:
            SECURITY_TRAINING.
        offboarding_evidence (Union[Unset, bool]):
        group_ids (Union[Unset, list[float]]):
        sort (Union[Unset, PersonnelPublicControllerListPersonnelSort]):  Example: NAME.
        sort_dir (Union[Unset, PersonnelPublicControllerListPersonnelSortDir]):  Example: ASC.
        mdm_source_type (Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType]):
            Example: AGENT.
        inverse_mdm_source_types (Union[Unset,
            list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]]):  Example:
            ['AGENT'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        employment_status=employment_status,
        employment_statuses=employment_statuses,
        full_compliance=full_compliance,
        accepted_policies_compliance=accepted_policies_compliance,
        identity_mfa_compliance=identity_mfa_compliance,
        bg_check_compliance=bg_check_compliance,
        agent_installed_compliance=agent_installed_compliance,
        password_manager_compliance=password_manager_compliance,
        auto_updates_compliance=auto_updates_compliance,
        location_services_compliance=location_services_compliance,
        hd_encryption_compliance=hd_encryption_compliance,
        antivirus_compliance=antivirus_compliance,
        lock_screen_compliance=lock_screen_compliance,
        security_training_compliance=security_training_compliance,
        hipaa_training_compliance=hipaa_training_compliance,
        nistai_training_compliance=nistai_training_compliance,
        device_compliance=device_compliance,
        multi_security_training_compliance=multi_security_training_compliance,
        multi_training_compliance_type=multi_training_compliance_type,
        offboarding_evidence=offboarding_evidence,
        group_ids=group_ids,
        sort=sort,
        sort_dir=sort_dir,
        mdm_source_type=mdm_source_type,
        inverse_mdm_source_types=inverse_mdm_source_types,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    employment_status: Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus] = UNSET,
    employment_statuses: Union[Unset, list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]] = UNSET,
    full_compliance: Union[Unset, bool] = UNSET,
    accepted_policies_compliance: Union[Unset, bool] = UNSET,
    identity_mfa_compliance: Union[Unset, bool] = UNSET,
    bg_check_compliance: Union[Unset, bool] = UNSET,
    agent_installed_compliance: Union[Unset, bool] = UNSET,
    password_manager_compliance: Union[Unset, bool] = UNSET,
    auto_updates_compliance: Union[Unset, bool] = UNSET,
    location_services_compliance: Union[Unset, bool] = UNSET,
    hd_encryption_compliance: Union[Unset, bool] = UNSET,
    antivirus_compliance: Union[Unset, bool] = UNSET,
    lock_screen_compliance: Union[Unset, bool] = UNSET,
    security_training_compliance: Union[Unset, bool] = UNSET,
    hipaa_training_compliance: Union[Unset, bool] = UNSET,
    nistai_training_compliance: Union[Unset, bool] = UNSET,
    device_compliance: Union[Unset, bool] = UNSET,
    multi_security_training_compliance: Union[Unset, bool] = UNSET,
    multi_training_compliance_type: Union[
        Unset, PersonnelPublicControllerListPersonnelMultiTrainingComplianceType
    ] = UNSET,
    offboarding_evidence: Union[Unset, bool] = UNSET,
    group_ids: Union[Unset, list[float]] = UNSET,
    sort: Union[Unset, PersonnelPublicControllerListPersonnelSort] = UNSET,
    sort_dir: Union[Unset, PersonnelPublicControllerListPersonnelSortDir] = UNSET,
    mdm_source_type: Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType] = UNSET,
    inverse_mdm_source_types: Union[
        Unset, list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]
    ] = UNSET,
) -> Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
    """Find personnel by search terms and filters

     List personnel given the search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        employment_status (Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.
        employment_statuses (Union[Unset,
            list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]]):  Example:
            ['CURRENT_EMPLOYEE'].
        full_compliance (Union[Unset, bool]):
        accepted_policies_compliance (Union[Unset, bool]):
        identity_mfa_compliance (Union[Unset, bool]):
        bg_check_compliance (Union[Unset, bool]):
        agent_installed_compliance (Union[Unset, bool]):
        password_manager_compliance (Union[Unset, bool]):
        auto_updates_compliance (Union[Unset, bool]):
        location_services_compliance (Union[Unset, bool]):
        hd_encryption_compliance (Union[Unset, bool]):
        antivirus_compliance (Union[Unset, bool]):
        lock_screen_compliance (Union[Unset, bool]):
        security_training_compliance (Union[Unset, bool]):
        hipaa_training_compliance (Union[Unset, bool]):
        nistai_training_compliance (Union[Unset, bool]):
        device_compliance (Union[Unset, bool]):
        multi_security_training_compliance (Union[Unset, bool]):
        multi_training_compliance_type (Union[Unset,
            PersonnelPublicControllerListPersonnelMultiTrainingComplianceType]):  Example:
            SECURITY_TRAINING.
        offboarding_evidence (Union[Unset, bool]):
        group_ids (Union[Unset, list[float]]):
        sort (Union[Unset, PersonnelPublicControllerListPersonnelSort]):  Example: NAME.
        sort_dir (Union[Unset, PersonnelPublicControllerListPersonnelSortDir]):  Example: ASC.
        mdm_source_type (Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType]):
            Example: AGENT.
        inverse_mdm_source_types (Union[Unset,
            list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]]):  Example:
            ['AGENT'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        employment_status=employment_status,
        employment_statuses=employment_statuses,
        full_compliance=full_compliance,
        accepted_policies_compliance=accepted_policies_compliance,
        identity_mfa_compliance=identity_mfa_compliance,
        bg_check_compliance=bg_check_compliance,
        agent_installed_compliance=agent_installed_compliance,
        password_manager_compliance=password_manager_compliance,
        auto_updates_compliance=auto_updates_compliance,
        location_services_compliance=location_services_compliance,
        hd_encryption_compliance=hd_encryption_compliance,
        antivirus_compliance=antivirus_compliance,
        lock_screen_compliance=lock_screen_compliance,
        security_training_compliance=security_training_compliance,
        hipaa_training_compliance=hipaa_training_compliance,
        nistai_training_compliance=nistai_training_compliance,
        device_compliance=device_compliance,
        multi_security_training_compliance=multi_security_training_compliance,
        multi_training_compliance_type=multi_training_compliance_type,
        offboarding_evidence=offboarding_evidence,
        group_ids=group_ids,
        sort=sort,
        sort_dir=sort_dir,
        mdm_source_type=mdm_source_type,
        inverse_mdm_source_types=inverse_mdm_source_types,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    employment_status: Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus] = UNSET,
    employment_statuses: Union[Unset, list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]] = UNSET,
    full_compliance: Union[Unset, bool] = UNSET,
    accepted_policies_compliance: Union[Unset, bool] = UNSET,
    identity_mfa_compliance: Union[Unset, bool] = UNSET,
    bg_check_compliance: Union[Unset, bool] = UNSET,
    agent_installed_compliance: Union[Unset, bool] = UNSET,
    password_manager_compliance: Union[Unset, bool] = UNSET,
    auto_updates_compliance: Union[Unset, bool] = UNSET,
    location_services_compliance: Union[Unset, bool] = UNSET,
    hd_encryption_compliance: Union[Unset, bool] = UNSET,
    antivirus_compliance: Union[Unset, bool] = UNSET,
    lock_screen_compliance: Union[Unset, bool] = UNSET,
    security_training_compliance: Union[Unset, bool] = UNSET,
    hipaa_training_compliance: Union[Unset, bool] = UNSET,
    nistai_training_compliance: Union[Unset, bool] = UNSET,
    device_compliance: Union[Unset, bool] = UNSET,
    multi_security_training_compliance: Union[Unset, bool] = UNSET,
    multi_training_compliance_type: Union[
        Unset, PersonnelPublicControllerListPersonnelMultiTrainingComplianceType
    ] = UNSET,
    offboarding_evidence: Union[Unset, bool] = UNSET,
    group_ids: Union[Unset, list[float]] = UNSET,
    sort: Union[Unset, PersonnelPublicControllerListPersonnelSort] = UNSET,
    sort_dir: Union[Unset, PersonnelPublicControllerListPersonnelSortDir] = UNSET,
    mdm_source_type: Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType] = UNSET,
    inverse_mdm_source_types: Union[
        Unset, list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]
    ] = UNSET,
) -> Optional[Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]]:
    """Find personnel by search terms and filters

     List personnel given the search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: John Doe.
        employment_status (Union[Unset, PersonnelPublicControllerListPersonnelEmploymentStatus]):
            Example: CURRENT_EMPLOYEE.
        employment_statuses (Union[Unset,
            list[PersonnelPublicControllerListPersonnelEmploymentStatusesItem]]):  Example:
            ['CURRENT_EMPLOYEE'].
        full_compliance (Union[Unset, bool]):
        accepted_policies_compliance (Union[Unset, bool]):
        identity_mfa_compliance (Union[Unset, bool]):
        bg_check_compliance (Union[Unset, bool]):
        agent_installed_compliance (Union[Unset, bool]):
        password_manager_compliance (Union[Unset, bool]):
        auto_updates_compliance (Union[Unset, bool]):
        location_services_compliance (Union[Unset, bool]):
        hd_encryption_compliance (Union[Unset, bool]):
        antivirus_compliance (Union[Unset, bool]):
        lock_screen_compliance (Union[Unset, bool]):
        security_training_compliance (Union[Unset, bool]):
        hipaa_training_compliance (Union[Unset, bool]):
        nistai_training_compliance (Union[Unset, bool]):
        device_compliance (Union[Unset, bool]):
        multi_security_training_compliance (Union[Unset, bool]):
        multi_training_compliance_type (Union[Unset,
            PersonnelPublicControllerListPersonnelMultiTrainingComplianceType]):  Example:
            SECURITY_TRAINING.
        offboarding_evidence (Union[Unset, bool]):
        group_ids (Union[Unset, list[float]]):
        sort (Union[Unset, PersonnelPublicControllerListPersonnelSort]):  Example: NAME.
        sort_dir (Union[Unset, PersonnelPublicControllerListPersonnelSortDir]):  Example: ASC.
        mdm_source_type (Union[Unset, PersonnelPublicControllerListPersonnelMdmSourceType]):
            Example: AGENT.
        inverse_mdm_source_types (Union[Unset,
            list[PersonnelPublicControllerListPersonnelInverseMdmSourceTypesItem]]):  Example:
            ['AGENT'].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExceptionResponseDto, ExceptionResponsePublicDto, PersonnelTableResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            employment_status=employment_status,
            employment_statuses=employment_statuses,
            full_compliance=full_compliance,
            accepted_policies_compliance=accepted_policies_compliance,
            identity_mfa_compliance=identity_mfa_compliance,
            bg_check_compliance=bg_check_compliance,
            agent_installed_compliance=agent_installed_compliance,
            password_manager_compliance=password_manager_compliance,
            auto_updates_compliance=auto_updates_compliance,
            location_services_compliance=location_services_compliance,
            hd_encryption_compliance=hd_encryption_compliance,
            antivirus_compliance=antivirus_compliance,
            lock_screen_compliance=lock_screen_compliance,
            security_training_compliance=security_training_compliance,
            hipaa_training_compliance=hipaa_training_compliance,
            nistai_training_compliance=nistai_training_compliance,
            device_compliance=device_compliance,
            multi_security_training_compliance=multi_security_training_compliance,
            multi_training_compliance_type=multi_training_compliance_type,
            offboarding_evidence=offboarding_evidence,
            group_ids=group_ids,
            sort=sort,
            sort_dir=sort_dir,
            mdm_source_type=mdm_source_type,
            inverse_mdm_source_types=inverse_mdm_source_types,
        )
    ).parsed
