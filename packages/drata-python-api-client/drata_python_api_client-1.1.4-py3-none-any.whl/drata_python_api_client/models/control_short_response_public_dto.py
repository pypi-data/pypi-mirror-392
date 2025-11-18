import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.user_card_response_public_dto import UserCardResponsePublicDto


T = TypeVar("T", bound="ControlShortResponsePublicDto")


@_attrs_define
class ControlShortResponsePublicDto:
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
        activity (str): Control activity Example: 1. Ensure tools are implemented to monitor databases.
        slug (str): Control slug Example: databases-monitored-and-alarmed.
        archived_at (datetime.datetime): Date control was archived at or NULL Example: 2025-07-01T16:45:55.246Z.
        last_updated_by (UserCardResponsePublicDto):
        updated_at (datetime.datetime): Date control was last updated Example: 2025-07-01T16:45:55.246Z.
        fk_control_template_id (float): Control template id, used to determine if control is custom Example: 123.
        has_evidence (bool): Boolean if control has any linked polices, reports, externalEvidence, or controlTests
            Example: True.
        has_policy (bool): Boolean if control has any linked polices Example: True.
        is_ready (bool): Is control "ready" Example: true.
        has_ticket (bool): This Control is associated to a Task Management Ticket Example: true.
    """

    id: float
    name: str
    code: str
    description: str
    question: str
    activity: str
    slug: str
    archived_at: datetime.datetime
    last_updated_by: "UserCardResponsePublicDto"
    updated_at: datetime.datetime
    fk_control_template_id: float
    has_evidence: bool
    has_policy: bool
    is_ready: bool
    has_ticket: bool
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

        last_updated_by = self.last_updated_by.to_dict()

        updated_at = self.updated_at.isoformat()

        fk_control_template_id = self.fk_control_template_id

        has_evidence = self.has_evidence

        has_policy = self.has_policy

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
                "question": question,
                "activity": activity,
                "slug": slug,
                "archivedAt": archived_at,
                "lastUpdatedBy": last_updated_by,
                "updatedAt": updated_at,
                "fk_control_template_id": fk_control_template_id,
                "hasEvidence": has_evidence,
                "hasPolicy": has_policy,
                "isReady": is_ready,
                "hasTicket": has_ticket,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        last_updated_by = UserCardResponsePublicDto.from_dict(d.pop("lastUpdatedBy"))

        updated_at = isoparse(d.pop("updatedAt"))

        fk_control_template_id = d.pop("fk_control_template_id")

        has_evidence = d.pop("hasEvidence")

        has_policy = d.pop("hasPolicy")

        is_ready = d.pop("isReady")

        has_ticket = d.pop("hasTicket")

        control_short_response_public_dto = cls(
            id=id,
            name=name,
            code=code,
            description=description,
            question=question,
            activity=activity,
            slug=slug,
            archived_at=archived_at,
            last_updated_by=last_updated_by,
            updated_at=updated_at,
            fk_control_template_id=fk_control_template_id,
            has_evidence=has_evidence,
            has_policy=has_policy,
            is_ready=is_ready,
            has_ticket=has_ticket,
        )

        control_short_response_public_dto.additional_properties = d
        return control_short_response_public_dto

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
