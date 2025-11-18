from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ControlOwnerRequestPublicDto")


@_attrs_define
class ControlOwnerRequestPublicDto:
    """
    Attributes:
        owner_ids (list[float]): Array of owner ids Example: [1, 2, 3].
    """

    owner_ids: list[float]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        owner_ids = self.owner_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ownerIds": owner_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        owner_ids = cast(list[float], d.pop("ownerIds"))

        control_owner_request_public_dto = cls(
            owner_ids=owner_ids,
        )

        control_owner_request_public_dto.additional_properties = d
        return control_owner_request_public_dto

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
