from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ConnectionProviderTypeResponsePublicDto")


@_attrs_define
class ConnectionProviderTypeResponsePublicDto:
    """
    Attributes:
        value (str): The provider type Example: MDM.
        is_enabled (bool): Provider type status Example: True.
    """

    value: str
    is_enabled: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        is_enabled = self.is_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "isEnabled": is_enabled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        is_enabled = d.pop("isEnabled")

        connection_provider_type_response_public_dto = cls(
            value=value,
            is_enabled=is_enabled,
        )

        connection_provider_type_response_public_dto.additional_properties = d
        return connection_provider_type_response_public_dto

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
