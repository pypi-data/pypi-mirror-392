from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...models.control_paginated_response_public_dto import ControlPaginatedResponsePublicDto
from ...models.exception_response_dto import ExceptionResponseDto
from ...models.exception_response_public_dto import ExceptionResponsePublicDto
from ...models.grc_public_controller_get_controls_articles_item import GRCPublicControllerGetControlsArticlesItem
from ...models.grc_public_controller_get_controls_assessment_factors_item import (
    GRCPublicControllerGetControlsAssessmentFactorsItem,
)
from ...models.grc_public_controller_get_controls_chapters_item import GRCPublicControllerGetControlsChaptersItem
from ...models.grc_public_controller_get_controls_cmmc_classes_item import GRCPublicControllerGetControlsCmmcClassesItem
from ...models.grc_public_controller_get_controls_cobit_item import GRCPublicControllerGetControlsCobitItem
from ...models.grc_public_controller_get_controls_control_baselines_item import (
    GRCPublicControllerGetControlsControlBaselinesItem,
)
from ...models.grc_public_controller_get_controls_control_classes_item import (
    GRCPublicControllerGetControlsControlClassesItem,
)
from ...models.grc_public_controller_get_controls_control_families_item import (
    GRCPublicControllerGetControlsControlFamiliesItem,
)
from ...models.grc_public_controller_get_controls_domains_item import GRCPublicControllerGetControlsDomainsItem
from ...models.grc_public_controller_get_controls_dora_chapters_item import (
    GRCPublicControllerGetControlsDoraChaptersItem,
)
from ...models.grc_public_controller_get_controls_drata_functions_item import (
    GRCPublicControllerGetControlsDrataFunctionsItem,
)
from ...models.grc_public_controller_get_controls_framework_tags_item import (
    GRCPublicControllerGetControlsFrameworkTagsItem,
)
from ...models.grc_public_controller_get_controls_functions_2_item import GRCPublicControllerGetControlsFunctions2Item
from ...models.grc_public_controller_get_controls_functions_item import GRCPublicControllerGetControlsFunctionsItem
from ...models.grc_public_controller_get_controls_has_ticket import GRCPublicControllerGetControlsHasTicket
from ...models.grc_public_controller_get_controls_isms_2022_category_item import (
    GRCPublicControllerGetControlsIsms2022CategoryItem,
)
from ...models.grc_public_controller_get_controls_isms_category_item import (
    GRCPublicControllerGetControlsIsmsCategoryItem,
)
from ...models.grc_public_controller_get_controls_iso_27701_item import GRCPublicControllerGetControlsIso27701Item
from ...models.grc_public_controller_get_controls_iso_420012023_item import (
    GRCPublicControllerGetControlsIso420012023Item,
)
from ...models.grc_public_controller_get_controls_nist_800171r3_control_classes_item import (
    GRCPublicControllerGetControlsNist800171R3ControlClassesItem,
)
from ...models.grc_public_controller_get_controls_nist_800171r3_control_families_item import (
    GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem,
)
from ...models.grc_public_controller_get_controls_pci_requirements_item import (
    GRCPublicControllerGetControlsPciRequirementsItem,
)
from ...models.grc_public_controller_get_controls_regulations_item import GRCPublicControllerGetControlsRegulationsItem
from ...models.grc_public_controller_get_controls_rules_item import GRCPublicControllerGetControlsRulesItem
from ...models.grc_public_controller_get_controls_sections_item import GRCPublicControllerGetControlsSectionsItem
from ...models.grc_public_controller_get_controls_soxitgc_item import GRCPublicControllerGetControlsSoxitgcItem
from ...models.grc_public_controller_get_controls_statutes_item import GRCPublicControllerGetControlsStatutesItem
from ...models.grc_public_controller_get_controls_sub_rules_item import GRCPublicControllerGetControlsSubRulesItem
from ...models.grc_public_controller_get_controls_trust_service_criteria_item import (
    GRCPublicControllerGetControlsTrustServiceCriteriaItem,
)
from ...models.grc_public_controller_get_controls_trust_service_criterion import (
    GRCPublicControllerGetControlsTrustServiceCriterion,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_tags: Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    trust_service_criterion: Union[Unset, GRCPublicControllerGetControlsTrustServiceCriterion] = UNSET,
    trust_service_criteria: Union[Unset, list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]] = UNSET,
    isms_category: Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]] = UNSET,
    isms_2022_category: Union[Unset, list[GRCPublicControllerGetControlsIsms2022CategoryItem]] = UNSET,
    is_annex_a2022: Union[Unset, bool] = UNSET,
    rules: Union[Unset, list[GRCPublicControllerGetControlsRulesItem]] = UNSET,
    sub_rules: Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]] = UNSET,
    pci_requirements: Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]] = UNSET,
    chapters: Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]] = UNSET,
    statutes: Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]] = UNSET,
    regulations: Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]] = UNSET,
    functions: Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]] = UNSET,
    functions2: Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]] = UNSET,
    sections: Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]] = UNSET,
    control_families: Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]] = UNSET,
    control_classes: Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]] = UNSET,
    iso27701: Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]] = UNSET,
    cobit: Union[Unset, list[GRCPublicControllerGetControlsCobitItem]] = UNSET,
    soxitgc: Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]] = UNSET,
    control_baselines: Union[Unset, list[GRCPublicControllerGetControlsControlBaselinesItem]] = UNSET,
    cmmc_classes: Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]] = UNSET,
    domains: Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]] = UNSET,
    assessment_factors: Union[Unset, list[GRCPublicControllerGetControlsAssessmentFactorsItem]] = UNSET,
    articles: Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]] = UNSET,
    dora_chapters: Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]] = UNSET,
    drata_functions: Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]] = UNSET,
    iso420012023: Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]] = UNSET,
    nist_800171_r_3_control_families: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]
    ] = UNSET,
    nist_800171_r_3_control_classes: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]
    ] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    is_ready: Union[Unset, bool] = UNSET,
    is_annex_a: Union[Unset, bool] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    is_monitored: Union[Unset, bool] = UNSET,
    has_evidence: Union[Unset, bool] = UNSET,
    has_policy: Union[Unset, bool] = UNSET,
    has_passing_test: Union[Unset, bool] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_requirement_id: Union[Unset, float] = UNSET,
    requirement_id: Union[Unset, float] = UNSET,
    exclude_test_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    has_ticket: Union[Unset, GRCPublicControllerGetControlsHasTicket] = UNSET,
    connection_id: Union[Unset, float] = UNSET,
    reviewers_ids: Union[Unset, list[float]] = UNSET,
    task_owners_ids: Union[Unset, list[float]] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["q"] = q

    json_framework_tags: Union[Unset, list[str]] = UNSET
    if not isinstance(framework_tags, Unset):
        json_framework_tags = []
        for framework_tags_item_data in framework_tags:
            framework_tags_item = framework_tags_item_data.value
            json_framework_tags.append(framework_tags_item)

    params["frameworkTags"] = json_framework_tags

    params["frameworkSlug"] = framework_slug

    json_trust_service_criterion: Union[Unset, str] = UNSET
    if not isinstance(trust_service_criterion, Unset):
        json_trust_service_criterion = trust_service_criterion.value

    params["trustServiceCriterion"] = json_trust_service_criterion

    json_trust_service_criteria: Union[Unset, list[str]] = UNSET
    if not isinstance(trust_service_criteria, Unset):
        json_trust_service_criteria = []
        for trust_service_criteria_item_data in trust_service_criteria:
            trust_service_criteria_item = trust_service_criteria_item_data.value
            json_trust_service_criteria.append(trust_service_criteria_item)

    params["trustServiceCriteria"] = json_trust_service_criteria

    json_isms_category: Union[Unset, list[str]] = UNSET
    if not isinstance(isms_category, Unset):
        json_isms_category = []
        for isms_category_item_data in isms_category:
            isms_category_item = isms_category_item_data.value
            json_isms_category.append(isms_category_item)

    params["ismsCategory"] = json_isms_category

    json_isms_2022_category: Union[Unset, list[str]] = UNSET
    if not isinstance(isms_2022_category, Unset):
        json_isms_2022_category = []
        for isms_2022_category_item_data in isms_2022_category:
            isms_2022_category_item = isms_2022_category_item_data.value
            json_isms_2022_category.append(isms_2022_category_item)

    params["isms2022Category"] = json_isms_2022_category

    params["isAnnexA2022"] = is_annex_a2022

    json_rules: Union[Unset, list[str]] = UNSET
    if not isinstance(rules, Unset):
        json_rules = []
        for rules_item_data in rules:
            rules_item = rules_item_data.value
            json_rules.append(rules_item)

    params["rules"] = json_rules

    json_sub_rules: Union[Unset, list[str]] = UNSET
    if not isinstance(sub_rules, Unset):
        json_sub_rules = []
        for sub_rules_item_data in sub_rules:
            sub_rules_item = sub_rules_item_data.value
            json_sub_rules.append(sub_rules_item)

    params["subRules"] = json_sub_rules

    json_pci_requirements: Union[Unset, list[str]] = UNSET
    if not isinstance(pci_requirements, Unset):
        json_pci_requirements = []
        for pci_requirements_item_data in pci_requirements:
            pci_requirements_item = pci_requirements_item_data.value
            json_pci_requirements.append(pci_requirements_item)

    params["pciRequirements"] = json_pci_requirements

    json_chapters: Union[Unset, list[str]] = UNSET
    if not isinstance(chapters, Unset):
        json_chapters = []
        for chapters_item_data in chapters:
            chapters_item = chapters_item_data.value
            json_chapters.append(chapters_item)

    params["chapters"] = json_chapters

    json_statutes: Union[Unset, list[str]] = UNSET
    if not isinstance(statutes, Unset):
        json_statutes = []
        for statutes_item_data in statutes:
            statutes_item = statutes_item_data.value
            json_statutes.append(statutes_item)

    params["statutes"] = json_statutes

    json_regulations: Union[Unset, list[str]] = UNSET
    if not isinstance(regulations, Unset):
        json_regulations = []
        for regulations_item_data in regulations:
            regulations_item = regulations_item_data.value
            json_regulations.append(regulations_item)

    params["regulations"] = json_regulations

    json_functions: Union[Unset, list[str]] = UNSET
    if not isinstance(functions, Unset):
        json_functions = []
        for functions_item_data in functions:
            functions_item = functions_item_data.value
            json_functions.append(functions_item)

    params["functions"] = json_functions

    json_functions2: Union[Unset, list[str]] = UNSET
    if not isinstance(functions2, Unset):
        json_functions2 = []
        for functions2_item_data in functions2:
            functions2_item = functions2_item_data.value
            json_functions2.append(functions2_item)

    params["functions2"] = json_functions2

    json_sections: Union[Unset, list[str]] = UNSET
    if not isinstance(sections, Unset):
        json_sections = []
        for sections_item_data in sections:
            sections_item = sections_item_data.value
            json_sections.append(sections_item)

    params["sections"] = json_sections

    json_control_families: Union[Unset, list[str]] = UNSET
    if not isinstance(control_families, Unset):
        json_control_families = []
        for control_families_item_data in control_families:
            control_families_item = control_families_item_data.value
            json_control_families.append(control_families_item)

    params["controlFamilies"] = json_control_families

    json_control_classes: Union[Unset, list[str]] = UNSET
    if not isinstance(control_classes, Unset):
        json_control_classes = []
        for control_classes_item_data in control_classes:
            control_classes_item = control_classes_item_data.value
            json_control_classes.append(control_classes_item)

    params["controlClasses"] = json_control_classes

    json_iso27701: Union[Unset, list[str]] = UNSET
    if not isinstance(iso27701, Unset):
        json_iso27701 = []
        for iso27701_item_data in iso27701:
            iso27701_item = iso27701_item_data.value
            json_iso27701.append(iso27701_item)

    params["iso27701"] = json_iso27701

    json_cobit: Union[Unset, list[str]] = UNSET
    if not isinstance(cobit, Unset):
        json_cobit = []
        for cobit_item_data in cobit:
            cobit_item = cobit_item_data.value
            json_cobit.append(cobit_item)

    params["cobit"] = json_cobit

    json_soxitgc: Union[Unset, list[str]] = UNSET
    if not isinstance(soxitgc, Unset):
        json_soxitgc = []
        for soxitgc_item_data in soxitgc:
            soxitgc_item = soxitgc_item_data.value
            json_soxitgc.append(soxitgc_item)

    params["soxitgc"] = json_soxitgc

    json_control_baselines: Union[Unset, list[str]] = UNSET
    if not isinstance(control_baselines, Unset):
        json_control_baselines = []
        for control_baselines_item_data in control_baselines:
            control_baselines_item = control_baselines_item_data.value
            json_control_baselines.append(control_baselines_item)

    params["controlBaselines"] = json_control_baselines

    json_cmmc_classes: Union[Unset, list[str]] = UNSET
    if not isinstance(cmmc_classes, Unset):
        json_cmmc_classes = []
        for cmmc_classes_item_data in cmmc_classes:
            cmmc_classes_item = cmmc_classes_item_data.value
            json_cmmc_classes.append(cmmc_classes_item)

    params["cmmcClasses"] = json_cmmc_classes

    json_domains: Union[Unset, list[str]] = UNSET
    if not isinstance(domains, Unset):
        json_domains = []
        for domains_item_data in domains:
            domains_item = domains_item_data.value
            json_domains.append(domains_item)

    params["domains"] = json_domains

    json_assessment_factors: Union[Unset, list[str]] = UNSET
    if not isinstance(assessment_factors, Unset):
        json_assessment_factors = []
        for assessment_factors_item_data in assessment_factors:
            assessment_factors_item = assessment_factors_item_data.value
            json_assessment_factors.append(assessment_factors_item)

    params["assessmentFactors"] = json_assessment_factors

    json_articles: Union[Unset, list[str]] = UNSET
    if not isinstance(articles, Unset):
        json_articles = []
        for articles_item_data in articles:
            articles_item = articles_item_data.value
            json_articles.append(articles_item)

    params["articles"] = json_articles

    json_dora_chapters: Union[Unset, list[str]] = UNSET
    if not isinstance(dora_chapters, Unset):
        json_dora_chapters = []
        for dora_chapters_item_data in dora_chapters:
            dora_chapters_item = dora_chapters_item_data.value
            json_dora_chapters.append(dora_chapters_item)

    params["doraChapters"] = json_dora_chapters

    json_drata_functions: Union[Unset, list[str]] = UNSET
    if not isinstance(drata_functions, Unset):
        json_drata_functions = []
        for drata_functions_item_data in drata_functions:
            drata_functions_item = drata_functions_item_data.value
            json_drata_functions.append(drata_functions_item)

    params["drataFunctions"] = json_drata_functions

    json_iso420012023: Union[Unset, list[str]] = UNSET
    if not isinstance(iso420012023, Unset):
        json_iso420012023 = []
        for iso420012023_item_data in iso420012023:
            iso420012023_item = iso420012023_item_data.value
            json_iso420012023.append(iso420012023_item)

    params["iso420012023"] = json_iso420012023

    json_nist_800171_r_3_control_families: Union[Unset, list[str]] = UNSET
    if not isinstance(nist_800171_r_3_control_families, Unset):
        json_nist_800171_r_3_control_families = []
        for nist_800171_r_3_control_families_item_data in nist_800171_r_3_control_families:
            nist_800171_r_3_control_families_item = nist_800171_r_3_control_families_item_data.value
            json_nist_800171_r_3_control_families.append(nist_800171_r_3_control_families_item)

    params["nist800171r3ControlFamilies"] = json_nist_800171_r_3_control_families

    json_nist_800171_r_3_control_classes: Union[Unset, list[str]] = UNSET
    if not isinstance(nist_800171_r_3_control_classes, Unset):
        json_nist_800171_r_3_control_classes = []
        for nist_800171_r_3_control_classes_item_data in nist_800171_r_3_control_classes:
            nist_800171_r_3_control_classes_item = nist_800171_r_3_control_classes_item_data.value
            json_nist_800171_r_3_control_classes.append(nist_800171_r_3_control_classes_item)

    params["nist800171r3ControlClasses"] = json_nist_800171_r_3_control_classes

    json_user_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(user_ids, Unset):
        json_user_ids = user_ids

    params["userIds"] = json_user_ids

    params["isOwned"] = is_owned

    params["isReady"] = is_ready

    params["isAnnexA"] = is_annex_a

    params["isArchived"] = is_archived

    params["isMonitored"] = is_monitored

    params["hasEvidence"] = has_evidence

    params["hasPolicy"] = has_policy

    params["hasPassingTest"] = has_passing_test

    json_exclude_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(exclude_ids, Unset):
        json_exclude_ids = exclude_ids

    params["excludeIds"] = json_exclude_ids

    params["excludeRequirementId"] = exclude_requirement_id

    params["requirementId"] = requirement_id

    params["excludeTestId"] = exclude_test_id

    params["testId"] = test_id

    json_has_ticket: Union[Unset, str] = UNSET
    if not isinstance(has_ticket, Unset):
        json_has_ticket = has_ticket.value

    params["hasTicket"] = json_has_ticket

    params["connectionId"] = connection_id

    json_reviewers_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(reviewers_ids, Unset):
        json_reviewers_ids = reviewers_ids

    params["reviewersIds"] = json_reviewers_ids

    json_task_owners_ids: Union[Unset, list[float]] = UNSET
    if not isinstance(task_owners_ids, Unset):
        json_task_owners_ids = task_owners_ids

    params["taskOwnersIds"] = json_task_owners_ids

    params["workspaceId"] = workspace_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/controls",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient, response: httpx.Response
) -> Optional[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    if response.status_code == 200:
        response_200 = ControlPaginatedResponsePublicDto.from_dict(response.json())

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
) -> Response[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
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
    framework_tags: Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    trust_service_criterion: Union[Unset, GRCPublicControllerGetControlsTrustServiceCriterion] = UNSET,
    trust_service_criteria: Union[Unset, list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]] = UNSET,
    isms_category: Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]] = UNSET,
    isms_2022_category: Union[Unset, list[GRCPublicControllerGetControlsIsms2022CategoryItem]] = UNSET,
    is_annex_a2022: Union[Unset, bool] = UNSET,
    rules: Union[Unset, list[GRCPublicControllerGetControlsRulesItem]] = UNSET,
    sub_rules: Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]] = UNSET,
    pci_requirements: Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]] = UNSET,
    chapters: Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]] = UNSET,
    statutes: Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]] = UNSET,
    regulations: Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]] = UNSET,
    functions: Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]] = UNSET,
    functions2: Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]] = UNSET,
    sections: Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]] = UNSET,
    control_families: Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]] = UNSET,
    control_classes: Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]] = UNSET,
    iso27701: Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]] = UNSET,
    cobit: Union[Unset, list[GRCPublicControllerGetControlsCobitItem]] = UNSET,
    soxitgc: Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]] = UNSET,
    control_baselines: Union[Unset, list[GRCPublicControllerGetControlsControlBaselinesItem]] = UNSET,
    cmmc_classes: Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]] = UNSET,
    domains: Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]] = UNSET,
    assessment_factors: Union[Unset, list[GRCPublicControllerGetControlsAssessmentFactorsItem]] = UNSET,
    articles: Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]] = UNSET,
    dora_chapters: Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]] = UNSET,
    drata_functions: Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]] = UNSET,
    iso420012023: Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]] = UNSET,
    nist_800171_r_3_control_families: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]
    ] = UNSET,
    nist_800171_r_3_control_classes: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]
    ] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    is_ready: Union[Unset, bool] = UNSET,
    is_annex_a: Union[Unset, bool] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    is_monitored: Union[Unset, bool] = UNSET,
    has_evidence: Union[Unset, bool] = UNSET,
    has_policy: Union[Unset, bool] = UNSET,
    has_passing_test: Union[Unset, bool] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_requirement_id: Union[Unset, float] = UNSET,
    requirement_id: Union[Unset, float] = UNSET,
    exclude_test_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    has_ticket: Union[Unset, GRCPublicControllerGetControlsHasTicket] = UNSET,
    connection_id: Union[Unset, float] = UNSET,
    reviewers_ids: Union[Unset, list[float]] = UNSET,
    task_owners_ids: Union[Unset, list[float]] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find controls by search terms and filters

     List Controls given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Least-Privileged Policy for Customer Data Access.
        framework_tags (Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]]):
            Example: ['SOC_2', 'ISO27001'].
        framework_slug (Union[Unset, str]):  Example: soc2.
        trust_service_criterion (Union[Unset,
            GRCPublicControllerGetControlsTrustServiceCriterion]):  Example: ['AVAILABILITY'].
        trust_service_criteria (Union[Unset,
            list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]]):  Example: ['AVAILABILITY',
            'CONFIDENTIALITY'].
        isms_category (Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]]):
            Example: ['ISO27001_CONTEXT_OF_THE_ORGANIZATION', 'ISO27001_LEADERSHIP'].
        isms_2022_category (Union[Unset,
            list[GRCPublicControllerGetControlsIsms2022CategoryItem]]):  Example:
            ['ISO270012022_CONTEXT_OF_THE_ORGANIZATION', 'ISO270012022_LEADERSHIP'].
        is_annex_a2022 (Union[Unset, bool]):  Example: True.
        rules (Union[Unset, list[GRCPublicControllerGetControlsRulesItem]]):  Example:
            ['HIPAA_BREACH_NOTIFICATION', 'HIPAA_PRIVACY'].
        sub_rules (Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]]):  Example:
            ['GENERAL_RULES', 'ADMINISTRATIVE_SAFEGUARDS'].
        pci_requirements (Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]]):
            Example: ['PCI_FIREWALL', 'PCI_ACCESS_RESTRICTION'].
        chapters (Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'GDPR_PRINCIPLES'].
        statutes (Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]]):  Example:
            ['CCPA_INDIVIDUAL_RIGHTS', 'CCPA_SERVICE_PROVIDER'].
        regulations (Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]]):  Example:
            ['CCPA_BUSINESS_PRACTICES_FOR_HANDLING_CONSUMER_REQUESTS', 'CCPA_NON_DISCRIMINATION'].
        functions (Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]]):  Example:
            ['NISTCSF_RECOVER', 'NISTCSF_RESPOND'].
        functions2 (Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]]):  Example:
            ['NISTCSF2_GOVERN_GV', 'NISTCSF2_IDENTIFY_ID'].
        sections (Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]]):  Example:
            ['MSSSPA_DATA_SUBJECTS', 'MSSSPA_CHOICE_AND_CONSENT'].
        control_families (Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]]):
            Example: ['NIST800171R2_ACCESS_CONTROL', 'NIST800171R2_PERSONNEL_SECURITY'].
        control_classes (Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]]):
            Example: ['NIST800171R2_TECHNICAL'].
        iso27701 (Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]]):  Example:
            ['ISO277012019_ANNEX_B_CONDITIONS_FOR_COLLECTION_AND_PROCESSING'].
        cobit (Union[Unset, list[GRCPublicControllerGetControlsCobitItem]]):  Example:
            ['COBIT_ALIGN_PLAN_AND_ORGANIZE'].
        soxitgc (Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]]):  Example:
            ['SOX_ITGC_PROGRAM_DEVELOPMENT'].
        control_baselines (Union[Unset,
            list[GRCPublicControllerGetControlsControlBaselinesItem]]):  Example:
            ['NISTSP80053_OPERATIONAL'].
        cmmc_classes (Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]]):
            Example: ['CMMC_MANAGEMENT'].
        domains (Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]]):  Example:
            ['FFIEC_CYBERSECURITY_CONTROLS'].
        assessment_factors (Union[Unset,
            list[GRCPublicControllerGetControlsAssessmentFactorsItem]]):  Example:
            ['FFIEC_GOVERNANCE'].
        articles (Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]]):  Example:
            ['NIS2_GOVERNANCE'].
        dora_chapters (Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]]):
            Example: ['DORA_ICT_RMF_RTS'].
        drata_functions (Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]]):
            Example: ['DRATA_ESSENTIALS_DETECT'].
        iso420012023 (Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]]):
            Example: ['ISO420012023_AI_SYSTEM_LIFE_CYCLE'].
        nist_800171_r_3_control_families (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]]):  Example:
            ['NIST800171R3_ACCESS_CONTROL', 'NIST800171R3_PERSONNEL_SECURITY'].
        nist_800171_r_3_control_classes (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]]):  Example:
            ['NIST800171R3_TECHNICAL'].
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        is_ready (Union[Unset, bool]):  Example: True.
        is_annex_a (Union[Unset, bool]):  Example: True.
        is_archived (Union[Unset, bool]):
        is_monitored (Union[Unset, bool]):
        has_evidence (Union[Unset, bool]):  Example: True.
        has_policy (Union[Unset, bool]):  Example: True.
        has_passing_test (Union[Unset, bool]):  Example: True.
        exclude_ids (Union[Unset, list[float]]):
        exclude_requirement_id (Union[Unset, float]):
        requirement_id (Union[Unset, float]):
        exclude_test_id (Union[Unset, float]):
        test_id (Union[Unset, float]):
        has_ticket (Union[Unset, GRCPublicControllerGetControlsHasTicket]):
        connection_id (Union[Unset, float]):
        reviewers_ids (Union[Unset, list[float]]):  Example: [1].
        task_owners_ids (Union[Unset, list[float]]):  Example: [1].
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        framework_tags=framework_tags,
        framework_slug=framework_slug,
        trust_service_criterion=trust_service_criterion,
        trust_service_criteria=trust_service_criteria,
        isms_category=isms_category,
        isms_2022_category=isms_2022_category,
        is_annex_a2022=is_annex_a2022,
        rules=rules,
        sub_rules=sub_rules,
        pci_requirements=pci_requirements,
        chapters=chapters,
        statutes=statutes,
        regulations=regulations,
        functions=functions,
        functions2=functions2,
        sections=sections,
        control_families=control_families,
        control_classes=control_classes,
        iso27701=iso27701,
        cobit=cobit,
        soxitgc=soxitgc,
        control_baselines=control_baselines,
        cmmc_classes=cmmc_classes,
        domains=domains,
        assessment_factors=assessment_factors,
        articles=articles,
        dora_chapters=dora_chapters,
        drata_functions=drata_functions,
        iso420012023=iso420012023,
        nist_800171_r_3_control_families=nist_800171_r_3_control_families,
        nist_800171_r_3_control_classes=nist_800171_r_3_control_classes,
        user_ids=user_ids,
        is_owned=is_owned,
        is_ready=is_ready,
        is_annex_a=is_annex_a,
        is_archived=is_archived,
        is_monitored=is_monitored,
        has_evidence=has_evidence,
        has_policy=has_policy,
        has_passing_test=has_passing_test,
        exclude_ids=exclude_ids,
        exclude_requirement_id=exclude_requirement_id,
        requirement_id=requirement_id,
        exclude_test_id=exclude_test_id,
        test_id=test_id,
        has_ticket=has_ticket,
        connection_id=connection_id,
        reviewers_ids=reviewers_ids,
        task_owners_ids=task_owners_ids,
        workspace_id=workspace_id,
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
    framework_tags: Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    trust_service_criterion: Union[Unset, GRCPublicControllerGetControlsTrustServiceCriterion] = UNSET,
    trust_service_criteria: Union[Unset, list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]] = UNSET,
    isms_category: Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]] = UNSET,
    isms_2022_category: Union[Unset, list[GRCPublicControllerGetControlsIsms2022CategoryItem]] = UNSET,
    is_annex_a2022: Union[Unset, bool] = UNSET,
    rules: Union[Unset, list[GRCPublicControllerGetControlsRulesItem]] = UNSET,
    sub_rules: Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]] = UNSET,
    pci_requirements: Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]] = UNSET,
    chapters: Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]] = UNSET,
    statutes: Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]] = UNSET,
    regulations: Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]] = UNSET,
    functions: Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]] = UNSET,
    functions2: Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]] = UNSET,
    sections: Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]] = UNSET,
    control_families: Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]] = UNSET,
    control_classes: Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]] = UNSET,
    iso27701: Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]] = UNSET,
    cobit: Union[Unset, list[GRCPublicControllerGetControlsCobitItem]] = UNSET,
    soxitgc: Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]] = UNSET,
    control_baselines: Union[Unset, list[GRCPublicControllerGetControlsControlBaselinesItem]] = UNSET,
    cmmc_classes: Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]] = UNSET,
    domains: Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]] = UNSET,
    assessment_factors: Union[Unset, list[GRCPublicControllerGetControlsAssessmentFactorsItem]] = UNSET,
    articles: Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]] = UNSET,
    dora_chapters: Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]] = UNSET,
    drata_functions: Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]] = UNSET,
    iso420012023: Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]] = UNSET,
    nist_800171_r_3_control_families: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]
    ] = UNSET,
    nist_800171_r_3_control_classes: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]
    ] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    is_ready: Union[Unset, bool] = UNSET,
    is_annex_a: Union[Unset, bool] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    is_monitored: Union[Unset, bool] = UNSET,
    has_evidence: Union[Unset, bool] = UNSET,
    has_policy: Union[Unset, bool] = UNSET,
    has_passing_test: Union[Unset, bool] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_requirement_id: Union[Unset, float] = UNSET,
    requirement_id: Union[Unset, float] = UNSET,
    exclude_test_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    has_ticket: Union[Unset, GRCPublicControllerGetControlsHasTicket] = UNSET,
    connection_id: Union[Unset, float] = UNSET,
    reviewers_ids: Union[Unset, list[float]] = UNSET,
    task_owners_ids: Union[Unset, list[float]] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find controls by search terms and filters

     List Controls given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Least-Privileged Policy for Customer Data Access.
        framework_tags (Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]]):
            Example: ['SOC_2', 'ISO27001'].
        framework_slug (Union[Unset, str]):  Example: soc2.
        trust_service_criterion (Union[Unset,
            GRCPublicControllerGetControlsTrustServiceCriterion]):  Example: ['AVAILABILITY'].
        trust_service_criteria (Union[Unset,
            list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]]):  Example: ['AVAILABILITY',
            'CONFIDENTIALITY'].
        isms_category (Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]]):
            Example: ['ISO27001_CONTEXT_OF_THE_ORGANIZATION', 'ISO27001_LEADERSHIP'].
        isms_2022_category (Union[Unset,
            list[GRCPublicControllerGetControlsIsms2022CategoryItem]]):  Example:
            ['ISO270012022_CONTEXT_OF_THE_ORGANIZATION', 'ISO270012022_LEADERSHIP'].
        is_annex_a2022 (Union[Unset, bool]):  Example: True.
        rules (Union[Unset, list[GRCPublicControllerGetControlsRulesItem]]):  Example:
            ['HIPAA_BREACH_NOTIFICATION', 'HIPAA_PRIVACY'].
        sub_rules (Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]]):  Example:
            ['GENERAL_RULES', 'ADMINISTRATIVE_SAFEGUARDS'].
        pci_requirements (Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]]):
            Example: ['PCI_FIREWALL', 'PCI_ACCESS_RESTRICTION'].
        chapters (Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'GDPR_PRINCIPLES'].
        statutes (Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]]):  Example:
            ['CCPA_INDIVIDUAL_RIGHTS', 'CCPA_SERVICE_PROVIDER'].
        regulations (Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]]):  Example:
            ['CCPA_BUSINESS_PRACTICES_FOR_HANDLING_CONSUMER_REQUESTS', 'CCPA_NON_DISCRIMINATION'].
        functions (Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]]):  Example:
            ['NISTCSF_RECOVER', 'NISTCSF_RESPOND'].
        functions2 (Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]]):  Example:
            ['NISTCSF2_GOVERN_GV', 'NISTCSF2_IDENTIFY_ID'].
        sections (Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]]):  Example:
            ['MSSSPA_DATA_SUBJECTS', 'MSSSPA_CHOICE_AND_CONSENT'].
        control_families (Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]]):
            Example: ['NIST800171R2_ACCESS_CONTROL', 'NIST800171R2_PERSONNEL_SECURITY'].
        control_classes (Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]]):
            Example: ['NIST800171R2_TECHNICAL'].
        iso27701 (Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]]):  Example:
            ['ISO277012019_ANNEX_B_CONDITIONS_FOR_COLLECTION_AND_PROCESSING'].
        cobit (Union[Unset, list[GRCPublicControllerGetControlsCobitItem]]):  Example:
            ['COBIT_ALIGN_PLAN_AND_ORGANIZE'].
        soxitgc (Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]]):  Example:
            ['SOX_ITGC_PROGRAM_DEVELOPMENT'].
        control_baselines (Union[Unset,
            list[GRCPublicControllerGetControlsControlBaselinesItem]]):  Example:
            ['NISTSP80053_OPERATIONAL'].
        cmmc_classes (Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]]):
            Example: ['CMMC_MANAGEMENT'].
        domains (Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]]):  Example:
            ['FFIEC_CYBERSECURITY_CONTROLS'].
        assessment_factors (Union[Unset,
            list[GRCPublicControllerGetControlsAssessmentFactorsItem]]):  Example:
            ['FFIEC_GOVERNANCE'].
        articles (Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]]):  Example:
            ['NIS2_GOVERNANCE'].
        dora_chapters (Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]]):
            Example: ['DORA_ICT_RMF_RTS'].
        drata_functions (Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]]):
            Example: ['DRATA_ESSENTIALS_DETECT'].
        iso420012023 (Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]]):
            Example: ['ISO420012023_AI_SYSTEM_LIFE_CYCLE'].
        nist_800171_r_3_control_families (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]]):  Example:
            ['NIST800171R3_ACCESS_CONTROL', 'NIST800171R3_PERSONNEL_SECURITY'].
        nist_800171_r_3_control_classes (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]]):  Example:
            ['NIST800171R3_TECHNICAL'].
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        is_ready (Union[Unset, bool]):  Example: True.
        is_annex_a (Union[Unset, bool]):  Example: True.
        is_archived (Union[Unset, bool]):
        is_monitored (Union[Unset, bool]):
        has_evidence (Union[Unset, bool]):  Example: True.
        has_policy (Union[Unset, bool]):  Example: True.
        has_passing_test (Union[Unset, bool]):  Example: True.
        exclude_ids (Union[Unset, list[float]]):
        exclude_requirement_id (Union[Unset, float]):
        requirement_id (Union[Unset, float]):
        exclude_test_id (Union[Unset, float]):
        test_id (Union[Unset, float]):
        has_ticket (Union[Unset, GRCPublicControllerGetControlsHasTicket]):
        connection_id (Union[Unset, float]):
        reviewers_ids (Union[Unset, list[float]]):  Example: [1].
        task_owners_ids (Union[Unset, list[float]]):  Example: [1].
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        q=q,
        framework_tags=framework_tags,
        framework_slug=framework_slug,
        trust_service_criterion=trust_service_criterion,
        trust_service_criteria=trust_service_criteria,
        isms_category=isms_category,
        isms_2022_category=isms_2022_category,
        is_annex_a2022=is_annex_a2022,
        rules=rules,
        sub_rules=sub_rules,
        pci_requirements=pci_requirements,
        chapters=chapters,
        statutes=statutes,
        regulations=regulations,
        functions=functions,
        functions2=functions2,
        sections=sections,
        control_families=control_families,
        control_classes=control_classes,
        iso27701=iso27701,
        cobit=cobit,
        soxitgc=soxitgc,
        control_baselines=control_baselines,
        cmmc_classes=cmmc_classes,
        domains=domains,
        assessment_factors=assessment_factors,
        articles=articles,
        dora_chapters=dora_chapters,
        drata_functions=drata_functions,
        iso420012023=iso420012023,
        nist_800171_r_3_control_families=nist_800171_r_3_control_families,
        nist_800171_r_3_control_classes=nist_800171_r_3_control_classes,
        user_ids=user_ids,
        is_owned=is_owned,
        is_ready=is_ready,
        is_annex_a=is_annex_a,
        is_archived=is_archived,
        is_monitored=is_monitored,
        has_evidence=has_evidence,
        has_policy=has_policy,
        has_passing_test=has_passing_test,
        exclude_ids=exclude_ids,
        exclude_requirement_id=exclude_requirement_id,
        requirement_id=requirement_id,
        exclude_test_id=exclude_test_id,
        test_id=test_id,
        has_ticket=has_ticket,
        connection_id=connection_id,
        reviewers_ids=reviewers_ids,
        task_owners_ids=task_owners_ids,
        workspace_id=workspace_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_tags: Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    trust_service_criterion: Union[Unset, GRCPublicControllerGetControlsTrustServiceCriterion] = UNSET,
    trust_service_criteria: Union[Unset, list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]] = UNSET,
    isms_category: Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]] = UNSET,
    isms_2022_category: Union[Unset, list[GRCPublicControllerGetControlsIsms2022CategoryItem]] = UNSET,
    is_annex_a2022: Union[Unset, bool] = UNSET,
    rules: Union[Unset, list[GRCPublicControllerGetControlsRulesItem]] = UNSET,
    sub_rules: Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]] = UNSET,
    pci_requirements: Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]] = UNSET,
    chapters: Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]] = UNSET,
    statutes: Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]] = UNSET,
    regulations: Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]] = UNSET,
    functions: Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]] = UNSET,
    functions2: Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]] = UNSET,
    sections: Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]] = UNSET,
    control_families: Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]] = UNSET,
    control_classes: Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]] = UNSET,
    iso27701: Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]] = UNSET,
    cobit: Union[Unset, list[GRCPublicControllerGetControlsCobitItem]] = UNSET,
    soxitgc: Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]] = UNSET,
    control_baselines: Union[Unset, list[GRCPublicControllerGetControlsControlBaselinesItem]] = UNSET,
    cmmc_classes: Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]] = UNSET,
    domains: Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]] = UNSET,
    assessment_factors: Union[Unset, list[GRCPublicControllerGetControlsAssessmentFactorsItem]] = UNSET,
    articles: Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]] = UNSET,
    dora_chapters: Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]] = UNSET,
    drata_functions: Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]] = UNSET,
    iso420012023: Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]] = UNSET,
    nist_800171_r_3_control_families: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]
    ] = UNSET,
    nist_800171_r_3_control_classes: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]
    ] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    is_ready: Union[Unset, bool] = UNSET,
    is_annex_a: Union[Unset, bool] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    is_monitored: Union[Unset, bool] = UNSET,
    has_evidence: Union[Unset, bool] = UNSET,
    has_policy: Union[Unset, bool] = UNSET,
    has_passing_test: Union[Unset, bool] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_requirement_id: Union[Unset, float] = UNSET,
    requirement_id: Union[Unset, float] = UNSET,
    exclude_test_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    has_ticket: Union[Unset, GRCPublicControllerGetControlsHasTicket] = UNSET,
    connection_id: Union[Unset, float] = UNSET,
    reviewers_ids: Union[Unset, list[float]] = UNSET,
    task_owners_ids: Union[Unset, list[float]] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Response[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find controls by search terms and filters

     List Controls given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Least-Privileged Policy for Customer Data Access.
        framework_tags (Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]]):
            Example: ['SOC_2', 'ISO27001'].
        framework_slug (Union[Unset, str]):  Example: soc2.
        trust_service_criterion (Union[Unset,
            GRCPublicControllerGetControlsTrustServiceCriterion]):  Example: ['AVAILABILITY'].
        trust_service_criteria (Union[Unset,
            list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]]):  Example: ['AVAILABILITY',
            'CONFIDENTIALITY'].
        isms_category (Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]]):
            Example: ['ISO27001_CONTEXT_OF_THE_ORGANIZATION', 'ISO27001_LEADERSHIP'].
        isms_2022_category (Union[Unset,
            list[GRCPublicControllerGetControlsIsms2022CategoryItem]]):  Example:
            ['ISO270012022_CONTEXT_OF_THE_ORGANIZATION', 'ISO270012022_LEADERSHIP'].
        is_annex_a2022 (Union[Unset, bool]):  Example: True.
        rules (Union[Unset, list[GRCPublicControllerGetControlsRulesItem]]):  Example:
            ['HIPAA_BREACH_NOTIFICATION', 'HIPAA_PRIVACY'].
        sub_rules (Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]]):  Example:
            ['GENERAL_RULES', 'ADMINISTRATIVE_SAFEGUARDS'].
        pci_requirements (Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]]):
            Example: ['PCI_FIREWALL', 'PCI_ACCESS_RESTRICTION'].
        chapters (Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'GDPR_PRINCIPLES'].
        statutes (Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]]):  Example:
            ['CCPA_INDIVIDUAL_RIGHTS', 'CCPA_SERVICE_PROVIDER'].
        regulations (Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]]):  Example:
            ['CCPA_BUSINESS_PRACTICES_FOR_HANDLING_CONSUMER_REQUESTS', 'CCPA_NON_DISCRIMINATION'].
        functions (Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]]):  Example:
            ['NISTCSF_RECOVER', 'NISTCSF_RESPOND'].
        functions2 (Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]]):  Example:
            ['NISTCSF2_GOVERN_GV', 'NISTCSF2_IDENTIFY_ID'].
        sections (Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]]):  Example:
            ['MSSSPA_DATA_SUBJECTS', 'MSSSPA_CHOICE_AND_CONSENT'].
        control_families (Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]]):
            Example: ['NIST800171R2_ACCESS_CONTROL', 'NIST800171R2_PERSONNEL_SECURITY'].
        control_classes (Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]]):
            Example: ['NIST800171R2_TECHNICAL'].
        iso27701 (Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]]):  Example:
            ['ISO277012019_ANNEX_B_CONDITIONS_FOR_COLLECTION_AND_PROCESSING'].
        cobit (Union[Unset, list[GRCPublicControllerGetControlsCobitItem]]):  Example:
            ['COBIT_ALIGN_PLAN_AND_ORGANIZE'].
        soxitgc (Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]]):  Example:
            ['SOX_ITGC_PROGRAM_DEVELOPMENT'].
        control_baselines (Union[Unset,
            list[GRCPublicControllerGetControlsControlBaselinesItem]]):  Example:
            ['NISTSP80053_OPERATIONAL'].
        cmmc_classes (Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]]):
            Example: ['CMMC_MANAGEMENT'].
        domains (Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]]):  Example:
            ['FFIEC_CYBERSECURITY_CONTROLS'].
        assessment_factors (Union[Unset,
            list[GRCPublicControllerGetControlsAssessmentFactorsItem]]):  Example:
            ['FFIEC_GOVERNANCE'].
        articles (Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]]):  Example:
            ['NIS2_GOVERNANCE'].
        dora_chapters (Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]]):
            Example: ['DORA_ICT_RMF_RTS'].
        drata_functions (Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]]):
            Example: ['DRATA_ESSENTIALS_DETECT'].
        iso420012023 (Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]]):
            Example: ['ISO420012023_AI_SYSTEM_LIFE_CYCLE'].
        nist_800171_r_3_control_families (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]]):  Example:
            ['NIST800171R3_ACCESS_CONTROL', 'NIST800171R3_PERSONNEL_SECURITY'].
        nist_800171_r_3_control_classes (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]]):  Example:
            ['NIST800171R3_TECHNICAL'].
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        is_ready (Union[Unset, bool]):  Example: True.
        is_annex_a (Union[Unset, bool]):  Example: True.
        is_archived (Union[Unset, bool]):
        is_monitored (Union[Unset, bool]):
        has_evidence (Union[Unset, bool]):  Example: True.
        has_policy (Union[Unset, bool]):  Example: True.
        has_passing_test (Union[Unset, bool]):  Example: True.
        exclude_ids (Union[Unset, list[float]]):
        exclude_requirement_id (Union[Unset, float]):
        requirement_id (Union[Unset, float]):
        exclude_test_id (Union[Unset, float]):
        test_id (Union[Unset, float]):
        has_ticket (Union[Unset, GRCPublicControllerGetControlsHasTicket]):
        connection_id (Union[Unset, float]):
        reviewers_ids (Union[Unset, list[float]]):  Example: [1].
        task_owners_ids (Union[Unset, list[float]]):  Example: [1].
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        q=q,
        framework_tags=framework_tags,
        framework_slug=framework_slug,
        trust_service_criterion=trust_service_criterion,
        trust_service_criteria=trust_service_criteria,
        isms_category=isms_category,
        isms_2022_category=isms_2022_category,
        is_annex_a2022=is_annex_a2022,
        rules=rules,
        sub_rules=sub_rules,
        pci_requirements=pci_requirements,
        chapters=chapters,
        statutes=statutes,
        regulations=regulations,
        functions=functions,
        functions2=functions2,
        sections=sections,
        control_families=control_families,
        control_classes=control_classes,
        iso27701=iso27701,
        cobit=cobit,
        soxitgc=soxitgc,
        control_baselines=control_baselines,
        cmmc_classes=cmmc_classes,
        domains=domains,
        assessment_factors=assessment_factors,
        articles=articles,
        dora_chapters=dora_chapters,
        drata_functions=drata_functions,
        iso420012023=iso420012023,
        nist_800171_r_3_control_families=nist_800171_r_3_control_families,
        nist_800171_r_3_control_classes=nist_800171_r_3_control_classes,
        user_ids=user_ids,
        is_owned=is_owned,
        is_ready=is_ready,
        is_annex_a=is_annex_a,
        is_archived=is_archived,
        is_monitored=is_monitored,
        has_evidence=has_evidence,
        has_policy=has_policy,
        has_passing_test=has_passing_test,
        exclude_ids=exclude_ids,
        exclude_requirement_id=exclude_requirement_id,
        requirement_id=requirement_id,
        exclude_test_id=exclude_test_id,
        test_id=test_id,
        has_ticket=has_ticket,
        connection_id=connection_id,
        reviewers_ids=reviewers_ids,
        task_owners_ids=task_owners_ids,
        workspace_id=workspace_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, float] = 1.0,
    limit: Union[Unset, float] = 20.0,
    q: Union[Unset, str] = UNSET,
    framework_tags: Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]] = UNSET,
    framework_slug: Union[Unset, str] = UNSET,
    trust_service_criterion: Union[Unset, GRCPublicControllerGetControlsTrustServiceCriterion] = UNSET,
    trust_service_criteria: Union[Unset, list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]] = UNSET,
    isms_category: Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]] = UNSET,
    isms_2022_category: Union[Unset, list[GRCPublicControllerGetControlsIsms2022CategoryItem]] = UNSET,
    is_annex_a2022: Union[Unset, bool] = UNSET,
    rules: Union[Unset, list[GRCPublicControllerGetControlsRulesItem]] = UNSET,
    sub_rules: Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]] = UNSET,
    pci_requirements: Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]] = UNSET,
    chapters: Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]] = UNSET,
    statutes: Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]] = UNSET,
    regulations: Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]] = UNSET,
    functions: Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]] = UNSET,
    functions2: Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]] = UNSET,
    sections: Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]] = UNSET,
    control_families: Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]] = UNSET,
    control_classes: Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]] = UNSET,
    iso27701: Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]] = UNSET,
    cobit: Union[Unset, list[GRCPublicControllerGetControlsCobitItem]] = UNSET,
    soxitgc: Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]] = UNSET,
    control_baselines: Union[Unset, list[GRCPublicControllerGetControlsControlBaselinesItem]] = UNSET,
    cmmc_classes: Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]] = UNSET,
    domains: Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]] = UNSET,
    assessment_factors: Union[Unset, list[GRCPublicControllerGetControlsAssessmentFactorsItem]] = UNSET,
    articles: Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]] = UNSET,
    dora_chapters: Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]] = UNSET,
    drata_functions: Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]] = UNSET,
    iso420012023: Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]] = UNSET,
    nist_800171_r_3_control_families: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]
    ] = UNSET,
    nist_800171_r_3_control_classes: Union[
        Unset, list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]
    ] = UNSET,
    user_ids: Union[Unset, list[float]] = UNSET,
    is_owned: Union[Unset, bool] = UNSET,
    is_ready: Union[Unset, bool] = UNSET,
    is_annex_a: Union[Unset, bool] = UNSET,
    is_archived: Union[Unset, bool] = UNSET,
    is_monitored: Union[Unset, bool] = UNSET,
    has_evidence: Union[Unset, bool] = UNSET,
    has_policy: Union[Unset, bool] = UNSET,
    has_passing_test: Union[Unset, bool] = UNSET,
    exclude_ids: Union[Unset, list[float]] = UNSET,
    exclude_requirement_id: Union[Unset, float] = UNSET,
    requirement_id: Union[Unset, float] = UNSET,
    exclude_test_id: Union[Unset, float] = UNSET,
    test_id: Union[Unset, float] = UNSET,
    has_ticket: Union[Unset, GRCPublicControllerGetControlsHasTicket] = UNSET,
    connection_id: Union[Unset, float] = UNSET,
    reviewers_ids: Union[Unset, list[float]] = UNSET,
    task_owners_ids: Union[Unset, list[float]] = UNSET,
    workspace_id: Union[Unset, float] = UNSET,
) -> Optional[Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]]:
    """Find controls by search terms and filters

     List Controls given the provided search terms and filters

    Args:
        page (Union[Unset, float]):  Default: 1.0.
        limit (Union[Unset, float]):  Default: 20.0.
        q (Union[Unset, str]):  Example: Least-Privileged Policy for Customer Data Access.
        framework_tags (Union[Unset, list[GRCPublicControllerGetControlsFrameworkTagsItem]]):
            Example: ['SOC_2', 'ISO27001'].
        framework_slug (Union[Unset, str]):  Example: soc2.
        trust_service_criterion (Union[Unset,
            GRCPublicControllerGetControlsTrustServiceCriterion]):  Example: ['AVAILABILITY'].
        trust_service_criteria (Union[Unset,
            list[GRCPublicControllerGetControlsTrustServiceCriteriaItem]]):  Example: ['AVAILABILITY',
            'CONFIDENTIALITY'].
        isms_category (Union[Unset, list[GRCPublicControllerGetControlsIsmsCategoryItem]]):
            Example: ['ISO27001_CONTEXT_OF_THE_ORGANIZATION', 'ISO27001_LEADERSHIP'].
        isms_2022_category (Union[Unset,
            list[GRCPublicControllerGetControlsIsms2022CategoryItem]]):  Example:
            ['ISO270012022_CONTEXT_OF_THE_ORGANIZATION', 'ISO270012022_LEADERSHIP'].
        is_annex_a2022 (Union[Unset, bool]):  Example: True.
        rules (Union[Unset, list[GRCPublicControllerGetControlsRulesItem]]):  Example:
            ['HIPAA_BREACH_NOTIFICATION', 'HIPAA_PRIVACY'].
        sub_rules (Union[Unset, list[GRCPublicControllerGetControlsSubRulesItem]]):  Example:
            ['GENERAL_RULES', 'ADMINISTRATIVE_SAFEGUARDS'].
        pci_requirements (Union[Unset, list[GRCPublicControllerGetControlsPciRequirementsItem]]):
            Example: ['PCI_FIREWALL', 'PCI_ACCESS_RESTRICTION'].
        chapters (Union[Unset, list[GRCPublicControllerGetControlsChaptersItem]]):  Example:
            ['GDPR_CONTROLLER_AND_PROCESSOR', 'GDPR_PRINCIPLES'].
        statutes (Union[Unset, list[GRCPublicControllerGetControlsStatutesItem]]):  Example:
            ['CCPA_INDIVIDUAL_RIGHTS', 'CCPA_SERVICE_PROVIDER'].
        regulations (Union[Unset, list[GRCPublicControllerGetControlsRegulationsItem]]):  Example:
            ['CCPA_BUSINESS_PRACTICES_FOR_HANDLING_CONSUMER_REQUESTS', 'CCPA_NON_DISCRIMINATION'].
        functions (Union[Unset, list[GRCPublicControllerGetControlsFunctionsItem]]):  Example:
            ['NISTCSF_RECOVER', 'NISTCSF_RESPOND'].
        functions2 (Union[Unset, list[GRCPublicControllerGetControlsFunctions2Item]]):  Example:
            ['NISTCSF2_GOVERN_GV', 'NISTCSF2_IDENTIFY_ID'].
        sections (Union[Unset, list[GRCPublicControllerGetControlsSectionsItem]]):  Example:
            ['MSSSPA_DATA_SUBJECTS', 'MSSSPA_CHOICE_AND_CONSENT'].
        control_families (Union[Unset, list[GRCPublicControllerGetControlsControlFamiliesItem]]):
            Example: ['NIST800171R2_ACCESS_CONTROL', 'NIST800171R2_PERSONNEL_SECURITY'].
        control_classes (Union[Unset, list[GRCPublicControllerGetControlsControlClassesItem]]):
            Example: ['NIST800171R2_TECHNICAL'].
        iso27701 (Union[Unset, list[GRCPublicControllerGetControlsIso27701Item]]):  Example:
            ['ISO277012019_ANNEX_B_CONDITIONS_FOR_COLLECTION_AND_PROCESSING'].
        cobit (Union[Unset, list[GRCPublicControllerGetControlsCobitItem]]):  Example:
            ['COBIT_ALIGN_PLAN_AND_ORGANIZE'].
        soxitgc (Union[Unset, list[GRCPublicControllerGetControlsSoxitgcItem]]):  Example:
            ['SOX_ITGC_PROGRAM_DEVELOPMENT'].
        control_baselines (Union[Unset,
            list[GRCPublicControllerGetControlsControlBaselinesItem]]):  Example:
            ['NISTSP80053_OPERATIONAL'].
        cmmc_classes (Union[Unset, list[GRCPublicControllerGetControlsCmmcClassesItem]]):
            Example: ['CMMC_MANAGEMENT'].
        domains (Union[Unset, list[GRCPublicControllerGetControlsDomainsItem]]):  Example:
            ['FFIEC_CYBERSECURITY_CONTROLS'].
        assessment_factors (Union[Unset,
            list[GRCPublicControllerGetControlsAssessmentFactorsItem]]):  Example:
            ['FFIEC_GOVERNANCE'].
        articles (Union[Unset, list[GRCPublicControllerGetControlsArticlesItem]]):  Example:
            ['NIS2_GOVERNANCE'].
        dora_chapters (Union[Unset, list[GRCPublicControllerGetControlsDoraChaptersItem]]):
            Example: ['DORA_ICT_RMF_RTS'].
        drata_functions (Union[Unset, list[GRCPublicControllerGetControlsDrataFunctionsItem]]):
            Example: ['DRATA_ESSENTIALS_DETECT'].
        iso420012023 (Union[Unset, list[GRCPublicControllerGetControlsIso420012023Item]]):
            Example: ['ISO420012023_AI_SYSTEM_LIFE_CYCLE'].
        nist_800171_r_3_control_families (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlFamiliesItem]]):  Example:
            ['NIST800171R3_ACCESS_CONTROL', 'NIST800171R3_PERSONNEL_SECURITY'].
        nist_800171_r_3_control_classes (Union[Unset,
            list[GRCPublicControllerGetControlsNist800171R3ControlClassesItem]]):  Example:
            ['NIST800171R3_TECHNICAL'].
        user_ids (Union[Unset, list[float]]):  Example: [1].
        is_owned (Union[Unset, bool]):  Example: True.
        is_ready (Union[Unset, bool]):  Example: True.
        is_annex_a (Union[Unset, bool]):  Example: True.
        is_archived (Union[Unset, bool]):
        is_monitored (Union[Unset, bool]):
        has_evidence (Union[Unset, bool]):  Example: True.
        has_policy (Union[Unset, bool]):  Example: True.
        has_passing_test (Union[Unset, bool]):  Example: True.
        exclude_ids (Union[Unset, list[float]]):
        exclude_requirement_id (Union[Unset, float]):
        requirement_id (Union[Unset, float]):
        exclude_test_id (Union[Unset, float]):
        test_id (Union[Unset, float]):
        has_ticket (Union[Unset, GRCPublicControllerGetControlsHasTicket]):
        connection_id (Union[Unset, float]):
        reviewers_ids (Union[Unset, list[float]]):  Example: [1].
        task_owners_ids (Union[Unset, list[float]]):  Example: [1].
        workspace_id (Union[Unset, float]):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ControlPaginatedResponsePublicDto, ExceptionResponseDto, ExceptionResponsePublicDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            q=q,
            framework_tags=framework_tags,
            framework_slug=framework_slug,
            trust_service_criterion=trust_service_criterion,
            trust_service_criteria=trust_service_criteria,
            isms_category=isms_category,
            isms_2022_category=isms_2022_category,
            is_annex_a2022=is_annex_a2022,
            rules=rules,
            sub_rules=sub_rules,
            pci_requirements=pci_requirements,
            chapters=chapters,
            statutes=statutes,
            regulations=regulations,
            functions=functions,
            functions2=functions2,
            sections=sections,
            control_families=control_families,
            control_classes=control_classes,
            iso27701=iso27701,
            cobit=cobit,
            soxitgc=soxitgc,
            control_baselines=control_baselines,
            cmmc_classes=cmmc_classes,
            domains=domains,
            assessment_factors=assessment_factors,
            articles=articles,
            dora_chapters=dora_chapters,
            drata_functions=drata_functions,
            iso420012023=iso420012023,
            nist_800171_r_3_control_families=nist_800171_r_3_control_families,
            nist_800171_r_3_control_classes=nist_800171_r_3_control_classes,
            user_ids=user_ids,
            is_owned=is_owned,
            is_ready=is_ready,
            is_annex_a=is_annex_a,
            is_archived=is_archived,
            is_monitored=is_monitored,
            has_evidence=has_evidence,
            has_policy=has_policy,
            has_passing_test=has_passing_test,
            exclude_ids=exclude_ids,
            exclude_requirement_id=exclude_requirement_id,
            requirement_id=requirement_id,
            exclude_test_id=exclude_test_id,
            test_id=test_id,
            has_ticket=has_ticket,
            connection_id=connection_id,
            reviewers_ids=reviewers_ids,
            task_owners_ids=task_owners_ids,
            workspace_id=workspace_id,
        )
    ).parsed
