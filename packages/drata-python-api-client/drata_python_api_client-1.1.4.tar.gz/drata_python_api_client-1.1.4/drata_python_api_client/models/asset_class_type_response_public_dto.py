import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AssetClassTypeResponsePublicDto")


@_attrs_define
class AssetClassTypeResponsePublicDto:
    """
    Attributes:
        id (float): Asset class type ID Example: 1.
        asset_class_type (str): The string enum asset class type Example: DOCUMENT.
        created_at (datetime.datetime): asset class type created timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): asset class type update timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    asset_class_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        asset_class_type = self.asset_class_type

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "assetClassType": asset_class_type,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        asset_class_type = d.pop("assetClassType")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        asset_class_type_response_public_dto = cls(
            id=id,
            asset_class_type=asset_class_type,
            created_at=created_at,
            updated_at=updated_at,
        )

        asset_class_type_response_public_dto.additional_properties = d
        return asset_class_type_response_public_dto

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
