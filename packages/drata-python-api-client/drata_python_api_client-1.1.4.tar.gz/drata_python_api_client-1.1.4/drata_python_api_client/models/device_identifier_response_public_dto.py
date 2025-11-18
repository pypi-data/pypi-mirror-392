import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="DeviceIdentifierResponsePublicDto")


@_attrs_define
class DeviceIdentifierResponsePublicDto:
    """
    Attributes:
        id (float): Device identifier Id Example: 1.
        type_ (str): The identifier type Example: SERIAL_NUMBER.
        identifier (str): The identifier value Example: C02CG123DC79.
        created_at (datetime.datetime): Identifier createdAt timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Identifier updatedAt timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    type_: str
    identifier: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        identifier = self.identifier

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "identifier": identifier,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        identifier = d.pop("identifier")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        device_identifier_response_public_dto = cls(
            id=id,
            type_=type_,
            identifier=identifier,
            created_at=created_at,
            updated_at=updated_at,
        )

        device_identifier_response_public_dto.additional_properties = d
        return device_identifier_response_public_dto

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
