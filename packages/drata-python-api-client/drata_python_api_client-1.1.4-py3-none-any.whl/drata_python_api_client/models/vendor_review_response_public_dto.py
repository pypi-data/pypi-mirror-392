import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.vendor_review_response_public_dto_report_opinion import VendorReviewResponsePublicDtoReportOpinion
from ..models.vendor_review_response_public_dto_soc_report import VendorReviewResponsePublicDtoSocReport

if TYPE_CHECKING:
    from ..models.vendor_review_finding_response_public_dto import VendorReviewFindingResponsePublicDto
    from ..models.vendor_review_location_response_public_dto import VendorReviewLocationResponsePublicDto
    from ..models.vendor_review_service_response_public_dto import VendorReviewServiceResponsePublicDto
    from ..models.vendor_review_trust_service_category_map_response_public_dto import (
        VendorReviewTrustServiceCategoryMapResponsePublicDto,
    )
    from ..models.vendor_review_user_control_response_public_dto import VendorReviewUserControlResponsePublicDto


T = TypeVar("T", bound="VendorReviewResponsePublicDto")


@_attrs_define
class VendorReviewResponsePublicDto:
    """
    Attributes:
        id (float): Vendor Review ID Example: 1.
        updated_at (datetime.datetime): Review last updated date Example: 2025-07-01T16:45:55.246Z.
        reviewer (Union[None, str]): Reviewer name Example: John Doe.
        review_date (Union[None, datetime.datetime]): Review date Example: 2025-07-01T16:45:55.246Z.
        report_issue_date (Union[None, datetime.datetime]): Report issue date Example: 2025-07-01T16:45:55.246Z.
        soc_report (VendorReviewResponsePublicDtoSocReport): SOC report type Example: SOC_1.
        soc_report_type_1 (bool): Flag that indicates the SOC report type applies to type 1 Example: True.
        soc_report_type_2 (bool): Flag that indicates the SOC report type applies to type 2 Example: True.
        soc_type_1_start_date (Union[None, datetime.datetime]): Start date for SOC report type 1 Example:
            2025-07-01T16:45:55.246Z.
        soc_type_1_end_date (Union[None, datetime.datetime]): End date for SOC report type 1 Example:
            2025-07-01T16:45:55.246Z.
        soc_type_2_start_date (Union[None, datetime.datetime]): Start date for SOC report type 2 Example:
            2025-07-01T16:45:55.246Z.
        soc_type_2_end_date (Union[None, datetime.datetime]): End date for SOC report type 2 Example:
            2025-07-01T16:45:55.246Z.
        report_opinion (VendorReviewResponsePublicDtoReportOpinion): Vendor report opinion Example: UNQUALIFIED.
        encompass_business_needs (bool): Do control objectives or trust principles encompass business needs? Example:
            True.
        follow_up_activity (Union[None, str]): Follow up activity if report opinion is qualified Example: User must
            proceed to....
        has_material_impact (bool): Do the findings have any material impact on your control environment? Example: True.
        cpa_firm (Union[None, str]): CPA firm that performed the audit Example: CPA firm name.
        cpa_procedure_performed (Union[None, str]): Procedures Performed to Assess Reputation of CPA Firm Example: The
            following procedures were performed....
        subservice_organization (Union[None, str]): Subservice Organizations In Report Example: Subservice Inc..
        subservice_organization_using_inclusive_method (Union[None, bool]): Are Subservice Organizations Presented in
            the Report Using the Inclusive Method? Example: True.
        subservice_organization_procedure_performed (Union[None, str]): Procedures Performed to Assess Subservice
            Organizations Example: The following procedures were performed....
        trust_service_categories (list['VendorReviewTrustServiceCategoryMapResponsePublicDto']): Procedures Performed to
            Assess Subservice Organizations
        user_controls (list['VendorReviewUserControlResponsePublicDto']): Procedures Performed to Assess Subservice
            Organizations
        services (list['VendorReviewServiceResponsePublicDto']): Procedures Performed to Assess Subservice Organizations
        locations (list['VendorReviewLocationResponsePublicDto']): Procedures Performed to Assess Subservice
            Organizations
        findings (list['VendorReviewFindingResponsePublicDto']): Procedures Performed to Assess Subservice Organizations
    """

    id: float
    updated_at: datetime.datetime
    reviewer: Union[None, str]
    review_date: Union[None, datetime.datetime]
    report_issue_date: Union[None, datetime.datetime]
    soc_report: VendorReviewResponsePublicDtoSocReport
    soc_report_type_1: bool
    soc_report_type_2: bool
    soc_type_1_start_date: Union[None, datetime.datetime]
    soc_type_1_end_date: Union[None, datetime.datetime]
    soc_type_2_start_date: Union[None, datetime.datetime]
    soc_type_2_end_date: Union[None, datetime.datetime]
    report_opinion: VendorReviewResponsePublicDtoReportOpinion
    encompass_business_needs: bool
    follow_up_activity: Union[None, str]
    has_material_impact: bool
    cpa_firm: Union[None, str]
    cpa_procedure_performed: Union[None, str]
    subservice_organization: Union[None, str]
    subservice_organization_using_inclusive_method: Union[None, bool]
    subservice_organization_procedure_performed: Union[None, str]
    trust_service_categories: list["VendorReviewTrustServiceCategoryMapResponsePublicDto"]
    user_controls: list["VendorReviewUserControlResponsePublicDto"]
    services: list["VendorReviewServiceResponsePublicDto"]
    locations: list["VendorReviewLocationResponsePublicDto"]
    findings: list["VendorReviewFindingResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        updated_at = self.updated_at.isoformat()

        reviewer: Union[None, str]
        reviewer = self.reviewer

        review_date: Union[None, str]
        if isinstance(self.review_date, datetime.datetime):
            review_date = self.review_date.isoformat()
        else:
            review_date = self.review_date

        report_issue_date: Union[None, str]
        if isinstance(self.report_issue_date, datetime.datetime):
            report_issue_date = self.report_issue_date.isoformat()
        else:
            report_issue_date = self.report_issue_date

        soc_report = self.soc_report.value

        soc_report_type_1 = self.soc_report_type_1

        soc_report_type_2 = self.soc_report_type_2

        soc_type_1_start_date: Union[None, str]
        if isinstance(self.soc_type_1_start_date, datetime.datetime):
            soc_type_1_start_date = self.soc_type_1_start_date.isoformat()
        else:
            soc_type_1_start_date = self.soc_type_1_start_date

        soc_type_1_end_date: Union[None, str]
        if isinstance(self.soc_type_1_end_date, datetime.datetime):
            soc_type_1_end_date = self.soc_type_1_end_date.isoformat()
        else:
            soc_type_1_end_date = self.soc_type_1_end_date

        soc_type_2_start_date: Union[None, str]
        if isinstance(self.soc_type_2_start_date, datetime.datetime):
            soc_type_2_start_date = self.soc_type_2_start_date.isoformat()
        else:
            soc_type_2_start_date = self.soc_type_2_start_date

        soc_type_2_end_date: Union[None, str]
        if isinstance(self.soc_type_2_end_date, datetime.datetime):
            soc_type_2_end_date = self.soc_type_2_end_date.isoformat()
        else:
            soc_type_2_end_date = self.soc_type_2_end_date

        report_opinion = self.report_opinion.value

        encompass_business_needs = self.encompass_business_needs

        follow_up_activity: Union[None, str]
        follow_up_activity = self.follow_up_activity

        has_material_impact = self.has_material_impact

        cpa_firm: Union[None, str]
        cpa_firm = self.cpa_firm

        cpa_procedure_performed: Union[None, str]
        cpa_procedure_performed = self.cpa_procedure_performed

        subservice_organization: Union[None, str]
        subservice_organization = self.subservice_organization

        subservice_organization_using_inclusive_method: Union[None, bool]
        subservice_organization_using_inclusive_method = self.subservice_organization_using_inclusive_method

        subservice_organization_procedure_performed: Union[None, str]
        subservice_organization_procedure_performed = self.subservice_organization_procedure_performed

        trust_service_categories = []
        for trust_service_categories_item_data in self.trust_service_categories:
            trust_service_categories_item = trust_service_categories_item_data.to_dict()
            trust_service_categories.append(trust_service_categories_item)

        user_controls = []
        for user_controls_item_data in self.user_controls:
            user_controls_item = user_controls_item_data.to_dict()
            user_controls.append(user_controls_item)

        services = []
        for services_item_data in self.services:
            services_item = services_item_data.to_dict()
            services.append(services_item)

        locations = []
        for locations_item_data in self.locations:
            locations_item = locations_item_data.to_dict()
            locations.append(locations_item)

        findings = []
        for findings_item_data in self.findings:
            findings_item = findings_item_data.to_dict()
            findings.append(findings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "updatedAt": updated_at,
                "reviewer": reviewer,
                "reviewDate": review_date,
                "reportIssueDate": report_issue_date,
                "socReport": soc_report,
                "socReportType1": soc_report_type_1,
                "socReportType2": soc_report_type_2,
                "socType1StartDate": soc_type_1_start_date,
                "socType1EndDate": soc_type_1_end_date,
                "socType2StartDate": soc_type_2_start_date,
                "socType2EndDate": soc_type_2_end_date,
                "reportOpinion": report_opinion,
                "encompassBusinessNeeds": encompass_business_needs,
                "followUpActivity": follow_up_activity,
                "hasMaterialImpact": has_material_impact,
                "cpaFirm": cpa_firm,
                "cpaProcedurePerformed": cpa_procedure_performed,
                "subserviceOrganization": subservice_organization,
                "subserviceOrganizationUsingInclusiveMethod": subservice_organization_using_inclusive_method,
                "subserviceOrganizationProcedurePerformed": subservice_organization_procedure_performed,
                "trustServiceCategories": trust_service_categories,
                "userControls": user_controls,
                "services": services,
                "locations": locations,
                "findings": findings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vendor_review_finding_response_public_dto import VendorReviewFindingResponsePublicDto
        from ..models.vendor_review_location_response_public_dto import VendorReviewLocationResponsePublicDto
        from ..models.vendor_review_service_response_public_dto import VendorReviewServiceResponsePublicDto
        from ..models.vendor_review_trust_service_category_map_response_public_dto import (
            VendorReviewTrustServiceCategoryMapResponsePublicDto,
        )
        from ..models.vendor_review_user_control_response_public_dto import VendorReviewUserControlResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_reviewer(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        reviewer = _parse_reviewer(d.pop("reviewer"))

        def _parse_review_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                review_date_type_0 = isoparse(data)

                return review_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        review_date = _parse_review_date(d.pop("reviewDate"))

        def _parse_report_issue_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                report_issue_date_type_0 = isoparse(data)

                return report_issue_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        report_issue_date = _parse_report_issue_date(d.pop("reportIssueDate"))

        soc_report = VendorReviewResponsePublicDtoSocReport(d.pop("socReport"))

        soc_report_type_1 = d.pop("socReportType1")

        soc_report_type_2 = d.pop("socReportType2")

        def _parse_soc_type_1_start_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                soc_type_1_start_date_type_0 = isoparse(data)

                return soc_type_1_start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        soc_type_1_start_date = _parse_soc_type_1_start_date(d.pop("socType1StartDate"))

        def _parse_soc_type_1_end_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                soc_type_1_end_date_type_0 = isoparse(data)

                return soc_type_1_end_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        soc_type_1_end_date = _parse_soc_type_1_end_date(d.pop("socType1EndDate"))

        def _parse_soc_type_2_start_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                soc_type_2_start_date_type_0 = isoparse(data)

                return soc_type_2_start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        soc_type_2_start_date = _parse_soc_type_2_start_date(d.pop("socType2StartDate"))

        def _parse_soc_type_2_end_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                soc_type_2_end_date_type_0 = isoparse(data)

                return soc_type_2_end_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        soc_type_2_end_date = _parse_soc_type_2_end_date(d.pop("socType2EndDate"))

        report_opinion = VendorReviewResponsePublicDtoReportOpinion(d.pop("reportOpinion"))

        encompass_business_needs = d.pop("encompassBusinessNeeds")

        def _parse_follow_up_activity(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        follow_up_activity = _parse_follow_up_activity(d.pop("followUpActivity"))

        has_material_impact = d.pop("hasMaterialImpact")

        def _parse_cpa_firm(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        cpa_firm = _parse_cpa_firm(d.pop("cpaFirm"))

        def _parse_cpa_procedure_performed(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        cpa_procedure_performed = _parse_cpa_procedure_performed(d.pop("cpaProcedurePerformed"))

        def _parse_subservice_organization(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        subservice_organization = _parse_subservice_organization(d.pop("subserviceOrganization"))

        def _parse_subservice_organization_using_inclusive_method(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        subservice_organization_using_inclusive_method = _parse_subservice_organization_using_inclusive_method(
            d.pop("subserviceOrganizationUsingInclusiveMethod")
        )

        def _parse_subservice_organization_procedure_performed(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        subservice_organization_procedure_performed = _parse_subservice_organization_procedure_performed(
            d.pop("subserviceOrganizationProcedurePerformed")
        )

        trust_service_categories = []
        _trust_service_categories = d.pop("trustServiceCategories")
        for trust_service_categories_item_data in _trust_service_categories:
            trust_service_categories_item = VendorReviewTrustServiceCategoryMapResponsePublicDto.from_dict(
                trust_service_categories_item_data
            )

            trust_service_categories.append(trust_service_categories_item)

        user_controls = []
        _user_controls = d.pop("userControls")
        for user_controls_item_data in _user_controls:
            user_controls_item = VendorReviewUserControlResponsePublicDto.from_dict(user_controls_item_data)

            user_controls.append(user_controls_item)

        services = []
        _services = d.pop("services")
        for services_item_data in _services:
            services_item = VendorReviewServiceResponsePublicDto.from_dict(services_item_data)

            services.append(services_item)

        locations = []
        _locations = d.pop("locations")
        for locations_item_data in _locations:
            locations_item = VendorReviewLocationResponsePublicDto.from_dict(locations_item_data)

            locations.append(locations_item)

        findings = []
        _findings = d.pop("findings")
        for findings_item_data in _findings:
            findings_item = VendorReviewFindingResponsePublicDto.from_dict(findings_item_data)

            findings.append(findings_item)

        vendor_review_response_public_dto = cls(
            id=id,
            updated_at=updated_at,
            reviewer=reviewer,
            review_date=review_date,
            report_issue_date=report_issue_date,
            soc_report=soc_report,
            soc_report_type_1=soc_report_type_1,
            soc_report_type_2=soc_report_type_2,
            soc_type_1_start_date=soc_type_1_start_date,
            soc_type_1_end_date=soc_type_1_end_date,
            soc_type_2_start_date=soc_type_2_start_date,
            soc_type_2_end_date=soc_type_2_end_date,
            report_opinion=report_opinion,
            encompass_business_needs=encompass_business_needs,
            follow_up_activity=follow_up_activity,
            has_material_impact=has_material_impact,
            cpa_firm=cpa_firm,
            cpa_procedure_performed=cpa_procedure_performed,
            subservice_organization=subservice_organization,
            subservice_organization_using_inclusive_method=subservice_organization_using_inclusive_method,
            subservice_organization_procedure_performed=subservice_organization_procedure_performed,
            trust_service_categories=trust_service_categories,
            user_controls=user_controls,
            services=services,
            locations=locations,
            findings=findings,
        )

        vendor_review_response_public_dto.additional_properties = d
        return vendor_review_response_public_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
