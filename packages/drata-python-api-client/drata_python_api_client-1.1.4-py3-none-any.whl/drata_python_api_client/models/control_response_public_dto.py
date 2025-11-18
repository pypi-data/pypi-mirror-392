import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.control_test_response_public_dto import ControlTestResponsePublicDto
    from ..models.evidence_library_control_response_public_dto import EvidenceLibraryControlResponsePublicDto
    from ..models.external_evidence_response_public_dto import ExternalEvidenceResponsePublicDto
    from ..models.framework_requirements_response_public_dto import FrameworkRequirementsResponsePublicDto
    from ..models.policy_response_public_dto import PolicyResponsePublicDto
    from ..models.user_card_response_public_dto import UserCardResponsePublicDto


T = TypeVar("T", bound="ControlResponsePublicDto")


@_attrs_define
class ControlResponsePublicDto:
    """
    Attributes:
        id (float): Control id Example: 123.
        name (str): Control name Example: Databases Monitored and Alarmed.
        code (str): Control code Example: DCF-1002.
        description (str): Control description Example: Drata has implemented tools to monitor Drata's databases and
            notify appropriate personnel of any events or incidents based on predetermined criteria. Incidents are escalated
            per policy..
        question (str): Control question Example: Does the organization implement tools to monitor its databases and
            notify appropriate personnel of incidents based on predetermined criteria?.
        activity (str): Control activity Example: 1. Ensure tools are implemented to monitor databases             2.
            Ensure notifications based on specific criteria are sent to the appropriate personnel             3. Escalate
            incidents appropriately.
        slug (str): Control slug Example: databases-monitored-and-alarmed.
        archived_at (datetime.datetime): Date control was archived at or NULL Example: 2025-07-01T16:45:55.246Z.
        framework_tags (list[str]): Framework tags associated with the control Example: ['SOC_2'].
        has_evidence (bool): Indicates if the control has evidence
        is_monitored (bool): Indicates if the control has a test
        has_owner (bool): Indicates if the control has at least one owner
        policies (list['PolicyResponsePublicDto']): Policies array, limited to id, name, createdAt, file Example:
            PolicyResponsePublicDto[].
        reports (list['EvidenceLibraryControlResponsePublicDto']): Control reports Example:
            ReportControlResponsePublicDto[].
        external_evidence (list['ExternalEvidenceResponsePublicDto']): ExternalEvidences array Example:
            ExternalEvidenceResponsePublicDto[].
        control_tests (list['ControlTestResponsePublicDto']): Control tests array Example:
            ControlTestResponsePublicDto[].
        framework_requirements (list['FrameworkRequirementsResponsePublicDto']): A list of associated requirements
            grouped by frameworks Example: FrameworkRequirementsResponsePublicDto[].
        last_updated_by (UserCardResponsePublicDto):
        updated_at (datetime.datetime): Date control was last updated Example: 2025-07-01T16:45:55.246Z.
        fk_control_template_id (float): Control template id, used to determine if control is custom Example: 123.
        owners (list['UserCardResponsePublicDto']): owners of the control Example: UserCardResponsePublicDto[].
    """

    id: float
    name: str
    code: str
    description: str
    question: str
    activity: str
    slug: str
    archived_at: datetime.datetime
    framework_tags: list[str]
    has_evidence: bool
    is_monitored: bool
    has_owner: bool
    policies: list["PolicyResponsePublicDto"]
    reports: list["EvidenceLibraryControlResponsePublicDto"]
    external_evidence: list["ExternalEvidenceResponsePublicDto"]
    control_tests: list["ControlTestResponsePublicDto"]
    framework_requirements: list["FrameworkRequirementsResponsePublicDto"]
    last_updated_by: "UserCardResponsePublicDto"
    updated_at: datetime.datetime
    fk_control_template_id: float
    owners: list["UserCardResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        code = self.code

        description = self.description

        question = self.question

        activity = self.activity

        slug = self.slug

        archived_at = self.archived_at.isoformat()

        framework_tags = self.framework_tags

        has_evidence = self.has_evidence

        is_monitored = self.is_monitored

        has_owner = self.has_owner

        policies = []
        for policies_item_data in self.policies:
            policies_item = policies_item_data.to_dict()
            policies.append(policies_item)

        reports = []
        for reports_item_data in self.reports:
            reports_item = reports_item_data.to_dict()
            reports.append(reports_item)

        external_evidence = []
        for external_evidence_item_data in self.external_evidence:
            external_evidence_item = external_evidence_item_data.to_dict()
            external_evidence.append(external_evidence_item)

        control_tests = []
        for control_tests_item_data in self.control_tests:
            control_tests_item = control_tests_item_data.to_dict()
            control_tests.append(control_tests_item)

        framework_requirements = []
        for framework_requirements_item_data in self.framework_requirements:
            framework_requirements_item = framework_requirements_item_data.to_dict()
            framework_requirements.append(framework_requirements_item)

        last_updated_by = self.last_updated_by.to_dict()

        updated_at = self.updated_at.isoformat()

        fk_control_template_id = self.fk_control_template_id

        owners = []
        for owners_item_data in self.owners:
            owners_item = owners_item_data.to_dict()
            owners.append(owners_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "code": code,
                "description": description,
                "question": question,
                "activity": activity,
                "slug": slug,
                "archivedAt": archived_at,
                "frameworkTags": framework_tags,
                "hasEvidence": has_evidence,
                "isMonitored": is_monitored,
                "hasOwner": has_owner,
                "policies": policies,
                "reports": reports,
                "externalEvidence": external_evidence,
                "controlTests": control_tests,
                "frameworkRequirements": framework_requirements,
                "lastUpdatedBy": last_updated_by,
                "updatedAt": updated_at,
                "fk_control_template_id": fk_control_template_id,
                "owners": owners,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.control_test_response_public_dto import ControlTestResponsePublicDto
        from ..models.evidence_library_control_response_public_dto import EvidenceLibraryControlResponsePublicDto
        from ..models.external_evidence_response_public_dto import ExternalEvidenceResponsePublicDto
        from ..models.framework_requirements_response_public_dto import FrameworkRequirementsResponsePublicDto
        from ..models.policy_response_public_dto import PolicyResponsePublicDto
        from ..models.user_card_response_public_dto import UserCardResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        code = d.pop("code")

        description = d.pop("description")

        question = d.pop("question")

        activity = d.pop("activity")

        slug = d.pop("slug")

        archived_at = isoparse(d.pop("archivedAt"))

        framework_tags = cast(list[str], d.pop("frameworkTags"))

        has_evidence = d.pop("hasEvidence")

        is_monitored = d.pop("isMonitored")

        has_owner = d.pop("hasOwner")

        policies = []
        _policies = d.pop("policies")
        for policies_item_data in _policies:
            policies_item = PolicyResponsePublicDto.from_dict(policies_item_data)

            policies.append(policies_item)

        reports = []
        _reports = d.pop("reports")
        for reports_item_data in _reports:
            reports_item = EvidenceLibraryControlResponsePublicDto.from_dict(reports_item_data)

            reports.append(reports_item)

        external_evidence = []
        _external_evidence = d.pop("externalEvidence")
        for external_evidence_item_data in _external_evidence:
            external_evidence_item = ExternalEvidenceResponsePublicDto.from_dict(external_evidence_item_data)

            external_evidence.append(external_evidence_item)

        control_tests = []
        _control_tests = d.pop("controlTests")
        for control_tests_item_data in _control_tests:
            control_tests_item = ControlTestResponsePublicDto.from_dict(control_tests_item_data)

            control_tests.append(control_tests_item)

        framework_requirements = []
        _framework_requirements = d.pop("frameworkRequirements")
        for framework_requirements_item_data in _framework_requirements:
            framework_requirements_item = FrameworkRequirementsResponsePublicDto.from_dict(
                framework_requirements_item_data
            )

            framework_requirements.append(framework_requirements_item)

        last_updated_by = UserCardResponsePublicDto.from_dict(d.pop("lastUpdatedBy"))

        updated_at = isoparse(d.pop("updatedAt"))

        fk_control_template_id = d.pop("fk_control_template_id")

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = UserCardResponsePublicDto.from_dict(owners_item_data)

            owners.append(owners_item)

        control_response_public_dto = cls(
            id=id,
            name=name,
            code=code,
            description=description,
            question=question,
            activity=activity,
            slug=slug,
            archived_at=archived_at,
            framework_tags=framework_tags,
            has_evidence=has_evidence,
            is_monitored=is_monitored,
            has_owner=has_owner,
            policies=policies,
            reports=reports,
            external_evidence=external_evidence,
            control_tests=control_tests,
            framework_requirements=framework_requirements,
            last_updated_by=last_updated_by,
            updated_at=updated_at,
            fk_control_template_id=fk_control_template_id,
            owners=owners,
        )

        control_response_public_dto.additional_properties = d
        return control_response_public_dto

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
