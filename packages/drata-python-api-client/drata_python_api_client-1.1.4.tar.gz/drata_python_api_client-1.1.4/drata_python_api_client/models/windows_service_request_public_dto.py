from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WindowsServiceRequestPublicDto")


@_attrs_define
class WindowsServiceRequestPublicDto:
    """
    Attributes:
        description (str): Windows service description. Example: Security feature that monitors and controls network
            traffic entering and exiting the device.
        name (str): Windows service name Example: Windows Firewall.
        start_type (str): Windows service Example: Automatic.
        status (str): Windows service status Example: Running.
    """

    description: str
    name: str
    start_type: str
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        name = self.name

        start_type = self.start_type

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "name": name,
                "startType": start_type,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description")

        name = d.pop("name")

        start_type = d.pop("startType")

        status = d.pop("status")

        windows_service_request_public_dto = cls(
            description=description,
            name=name,
            start_type=start_type,
            status=status,
        )

        windows_service_request_public_dto.additional_properties = d
        return windows_service_request_public_dto

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
