import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ControlMonitorResponsePublicDto")


@_attrs_define
class ControlMonitorResponsePublicDto:
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
        archived_at (Union[None, datetime.datetime]): Date control was archived at or NULL Example:
            2025-07-01T16:45:55.246Z.
    """

    id: float
    name: str
    code: str
    description: str
    question: str
    activity: str
    slug: str
    archived_at: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        code = self.code

        description = self.description

        question = self.question

        activity = self.activity

        slug = self.slug

        archived_at: Union[None, str]
        if isinstance(self.archived_at, datetime.datetime):
            archived_at = self.archived_at.isoformat()
        else:
            archived_at = self.archived_at

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
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        code = d.pop("code")

        description = d.pop("description")

        question = d.pop("question")

        activity = d.pop("activity")

        slug = d.pop("slug")

        def _parse_archived_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                archived_at_type_0 = isoparse(data)

                return archived_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        archived_at = _parse_archived_at(d.pop("archivedAt"))

        control_monitor_response_public_dto = cls(
            id=id,
            name=name,
            code=code,
            description=description,
            question=question,
            activity=activity,
            slug=slug,
            archived_at=archived_at,
        )

        control_monitor_response_public_dto.additional_properties = d
        return control_monitor_response_public_dto

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
