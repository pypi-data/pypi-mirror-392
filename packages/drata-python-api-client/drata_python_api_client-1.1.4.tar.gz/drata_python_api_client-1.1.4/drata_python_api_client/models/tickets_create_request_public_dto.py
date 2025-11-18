from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tickets_create_field_request_public_dto import TicketsCreateFieldRequestPublicDto
    from ..models.tickets_create_request_public_dto_get_parsed_request_dto import (
        TicketsCreateRequestPublicDtoGetParsedRequestDto,
    )


T = TypeVar("T", bound="TicketsCreateRequestPublicDto")


@_attrs_define
class TicketsCreateRequestPublicDto:
    """
    Attributes:
        connection_id (float): Connection ID Example: 1.
        project_id (str): Project ID Example: 10000.
        issue_type_id (str): IssueType ID Example: 10001.
        fields (list['TicketsCreateFieldRequestPublicDto']): The value keys used to fill out the expected ticket
            management provider schema
        monitor_instance_id (float): Monitor Instance id this task is associated to Example: 1.
        control_id (float): Control Id this task is associated to Example: 1.
        get_parsed_request_dto (TicketsCreateRequestPublicDtoGetParsedRequestDto):
    """

    connection_id: float
    project_id: str
    issue_type_id: str
    fields: list["TicketsCreateFieldRequestPublicDto"]
    monitor_instance_id: float
    control_id: float
    get_parsed_request_dto: "TicketsCreateRequestPublicDtoGetParsedRequestDto"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connection_id = self.connection_id

        project_id = self.project_id

        issue_type_id = self.issue_type_id

        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        monitor_instance_id = self.monitor_instance_id

        control_id = self.control_id

        get_parsed_request_dto = self.get_parsed_request_dto.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectionId": connection_id,
                "projectId": project_id,
                "issueTypeId": issue_type_id,
                "fields": fields,
                "monitorInstanceId": monitor_instance_id,
                "controlId": control_id,
                "getParsedRequestDto": get_parsed_request_dto,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tickets_create_field_request_public_dto import TicketsCreateFieldRequestPublicDto
        from ..models.tickets_create_request_public_dto_get_parsed_request_dto import (
            TicketsCreateRequestPublicDtoGetParsedRequestDto,
        )

        d = dict(src_dict)
        connection_id = d.pop("connectionId")

        project_id = d.pop("projectId")

        issue_type_id = d.pop("issueTypeId")

        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = TicketsCreateFieldRequestPublicDto.from_dict(fields_item_data)

            fields.append(fields_item)

        monitor_instance_id = d.pop("monitorInstanceId")

        control_id = d.pop("controlId")

        get_parsed_request_dto = TicketsCreateRequestPublicDtoGetParsedRequestDto.from_dict(
            d.pop("getParsedRequestDto")
        )

        tickets_create_request_public_dto = cls(
            connection_id=connection_id,
            project_id=project_id,
            issue_type_id=issue_type_id,
            fields=fields,
            monitor_instance_id=monitor_instance_id,
            control_id=control_id,
            get_parsed_request_dto=get_parsed_request_dto,
        )

        tickets_create_request_public_dto.additional_properties = d
        return tickets_create_request_public_dto

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
