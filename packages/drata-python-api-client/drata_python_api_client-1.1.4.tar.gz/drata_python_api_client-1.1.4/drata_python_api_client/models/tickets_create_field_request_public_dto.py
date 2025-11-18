from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TicketsCreateFieldRequestPublicDto")


@_attrs_define
class TicketsCreateFieldRequestPublicDto:
    """
    Attributes:
        field (str): Field name Example: summary.
        type_ (str): Type of the incoming data, used for validation Example: string.
        value (str): Value for the incoming issue field Example: My Ticket.
    """

    field: str
    type_: str
    value: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        type_ = self.type_

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "type": type_,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        type_ = d.pop("type")

        value = d.pop("value")

        tickets_create_field_request_public_dto = cls(
            field=field,
            type_=type_,
            value=value,
        )

        tickets_create_field_request_public_dto.additional_properties = d
        return tickets_create_field_request_public_dto

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
