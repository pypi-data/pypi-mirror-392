import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.control_list_response_public_dto_topics_item import ControlListResponsePublicDtoTopicsItem

if TYPE_CHECKING:
    from ..models.framework_requirements_response_public_dto import FrameworkRequirementsResponsePublicDto


T = TypeVar("T", bound="ControlListResponsePublicDto")


@_attrs_define
class ControlListResponsePublicDto:
    """
    Attributes:
        id (float): Control id Example: 123.
        name (str): Control name Example: Databases Monitored and Alarmed.
        code (str): Control code Example: DCF-1002.
        description (str): Control description Example: Drata has implemented tools to monitor Drata's databases and
            notify appropriate personnel of any events or incidents based on predetermined criteria. Incidents are escalated
            per policy..
        slug (str): Control slug Example: databases-monitored-and-alarmed.
        workspace_id (float): Workspace(product) id associated to control Example: 2.
        archived_at (datetime.datetime): Date control was archived at or NULL Example: 2025-07-01T16:45:55.246Z.
        framework_tags (list[str]): Framework tags associated with the control Example: ['SOC_2', 'CCPA'].
        has_evidence (bool): Indicates if the control has any evidence
        has_owner (bool): Indicates if the control has any owners
        is_monitored (bool): Indicates if the control has a test
        framework_requirements (list['FrameworkRequirementsResponsePublicDto']): A list of associated requirements
            grouped by frameworks Example: FrameworkRequirementsResponseDto[].
        topics (list[ControlListResponsePublicDtoTopicsItem]): Trust Service Criteria associated with the control
            Example: [1, 2].
        is_ready (bool): Is control "ready" Example: true.
        has_ticket (bool): This Control is associated to a Task Managment Ticket Example: true.
    """

    id: float
    name: str
    code: str
    description: str
    slug: str
    workspace_id: float
    archived_at: datetime.datetime
    framework_tags: list[str]
    has_evidence: bool
    has_owner: bool
    is_monitored: bool
    framework_requirements: list["FrameworkRequirementsResponsePublicDto"]
    topics: list[ControlListResponsePublicDtoTopicsItem]
    is_ready: bool
    has_ticket: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        code = self.code

        description = self.description

        slug = self.slug

        workspace_id = self.workspace_id

        archived_at = self.archived_at.isoformat()

        framework_tags = self.framework_tags

        has_evidence = self.has_evidence

        has_owner = self.has_owner

        is_monitored = self.is_monitored

        framework_requirements = []
        for framework_requirements_item_data in self.framework_requirements:
            framework_requirements_item = framework_requirements_item_data.to_dict()
            framework_requirements.append(framework_requirements_item)

        topics = []
        for topics_item_data in self.topics:
            topics_item = topics_item_data.value
            topics.append(topics_item)

        is_ready = self.is_ready

        has_ticket = self.has_ticket

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "code": code,
                "description": description,
                "slug": slug,
                "workspaceId": workspace_id,
                "archivedAt": archived_at,
                "frameworkTags": framework_tags,
                "hasEvidence": has_evidence,
                "hasOwner": has_owner,
                "isMonitored": is_monitored,
                "frameworkRequirements": framework_requirements,
                "topics": topics,
                "isReady": is_ready,
                "hasTicket": has_ticket,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.framework_requirements_response_public_dto import FrameworkRequirementsResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        code = d.pop("code")

        description = d.pop("description")

        slug = d.pop("slug")

        workspace_id = d.pop("workspaceId")

        archived_at = isoparse(d.pop("archivedAt"))

        framework_tags = cast(list[str], d.pop("frameworkTags"))

        has_evidence = d.pop("hasEvidence")

        has_owner = d.pop("hasOwner")

        is_monitored = d.pop("isMonitored")

        framework_requirements = []
        _framework_requirements = d.pop("frameworkRequirements")
        for framework_requirements_item_data in _framework_requirements:
            framework_requirements_item = FrameworkRequirementsResponsePublicDto.from_dict(
                framework_requirements_item_data
            )

            framework_requirements.append(framework_requirements_item)

        topics = []
        _topics = d.pop("topics")
        for topics_item_data in _topics:
            topics_item = ControlListResponsePublicDtoTopicsItem(topics_item_data)

            topics.append(topics_item)

        is_ready = d.pop("isReady")

        has_ticket = d.pop("hasTicket")

        control_list_response_public_dto = cls(
            id=id,
            name=name,
            code=code,
            description=description,
            slug=slug,
            workspace_id=workspace_id,
            archived_at=archived_at,
            framework_tags=framework_tags,
            has_evidence=has_evidence,
            has_owner=has_owner,
            is_monitored=is_monitored,
            framework_requirements=framework_requirements,
            topics=topics,
            is_ready=is_ready,
            has_ticket=has_ticket,
        )

        control_list_response_public_dto.additional_properties = d
        return control_list_response_public_dto

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
