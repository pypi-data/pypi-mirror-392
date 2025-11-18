from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceAppResponsePublicDto")


@_attrs_define
class DeviceAppResponsePublicDto:
    """
    Attributes:
        id (float): Installed app Id Example: 1.
        installed_app (str): The app description Example: Adobe Photoshop version 3.3 license 1a2b3c4d.
    """

    id: float
    installed_app: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        installed_app = self.installed_app

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "installedApp": installed_app,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        installed_app = d.pop("installedApp")

        device_app_response_public_dto = cls(
            id=id,
            installed_app=installed_app,
        )

        device_app_response_public_dto.additional_properties = d
        return device_app_response_public_dto

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
