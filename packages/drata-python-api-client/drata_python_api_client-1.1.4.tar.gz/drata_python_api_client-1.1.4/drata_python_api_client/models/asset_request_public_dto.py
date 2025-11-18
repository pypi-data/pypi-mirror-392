import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.asset_request_public_dto_asset_class_types_item import AssetRequestPublicDtoAssetClassTypesItem
from ..models.asset_request_public_dto_asset_type import AssetRequestPublicDtoAssetType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssetRequestPublicDto")


@_attrs_define
class AssetRequestPublicDto:
    """
    Attributes:
        name (str): The asset name Example: Asset name.
        description (str): The asset description Example: This is a description.
        asset_class_types (list[AssetRequestPublicDtoAssetClassTypesItem]): The asset class types Example: ['HARDWARE',
            'PERSONNEL'].
        asset_type (AssetRequestPublicDtoAssetType): The asset type Example: PHYSICAL.
        owner_id (float): The owner id Example: 1.
        notes (Union[Unset, str]): The asset notes Example: This is a note.
        unique_id (Union[Unset, str]): Unique Id associated with this asset Example: C02T6CDJGTFL.
        removed_at (Union[Unset, datetime.datetime]): Date the asset was removed Example: 2025-07-01T16:45:55.246Z.
        external_id (Union[Unset, str]): An externally sourced unique identifier for a virtual asset Example:
            i-0c844e3b433e4e3f.
        external_owner_id (Union[Unset, str]): Used to track the source of virtual assets, typically an account id
            Example: account-353.
    """

    name: str
    description: str
    asset_class_types: list[AssetRequestPublicDtoAssetClassTypesItem]
    asset_type: AssetRequestPublicDtoAssetType
    owner_id: float
    notes: Union[Unset, str] = UNSET
    unique_id: Union[Unset, str] = UNSET
    removed_at: Union[Unset, datetime.datetime] = UNSET
    external_id: Union[Unset, str] = UNSET
    external_owner_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        asset_class_types = []
        for asset_class_types_item_data in self.asset_class_types:
            asset_class_types_item = asset_class_types_item_data.value
            asset_class_types.append(asset_class_types_item)

        asset_type = self.asset_type.value

        owner_id = self.owner_id

        notes = self.notes

        unique_id = self.unique_id

        removed_at: Union[Unset, str] = UNSET
        if not isinstance(self.removed_at, Unset):
            removed_at = self.removed_at.isoformat()

        external_id = self.external_id

        external_owner_id = self.external_owner_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "assetClassTypes": asset_class_types,
                "assetType": asset_type,
                "ownerId": owner_id,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes
        if unique_id is not UNSET:
            field_dict["uniqueId"] = unique_id
        if removed_at is not UNSET:
            field_dict["removedAt"] = removed_at
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if external_owner_id is not UNSET:
            field_dict["externalOwnerId"] = external_owner_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        asset_class_types = []
        _asset_class_types = d.pop("assetClassTypes")
        for asset_class_types_item_data in _asset_class_types:
            asset_class_types_item = AssetRequestPublicDtoAssetClassTypesItem(asset_class_types_item_data)

            asset_class_types.append(asset_class_types_item)

        asset_type = AssetRequestPublicDtoAssetType(d.pop("assetType"))

        owner_id = d.pop("ownerId")

        notes = d.pop("notes", UNSET)

        unique_id = d.pop("uniqueId", UNSET)

        _removed_at = d.pop("removedAt", UNSET)
        removed_at: Union[Unset, datetime.datetime]
        if isinstance(_removed_at, Unset):
            removed_at = UNSET
        else:
            removed_at = isoparse(_removed_at)

        external_id = d.pop("externalId", UNSET)

        external_owner_id = d.pop("externalOwnerId", UNSET)

        asset_request_public_dto = cls(
            name=name,
            description=description,
            asset_class_types=asset_class_types,
            asset_type=asset_type,
            owner_id=owner_id,
            notes=notes,
            unique_id=unique_id,
            removed_at=removed_at,
            external_id=external_id,
            external_owner_id=external_owner_id,
        )

        asset_request_public_dto.additional_properties = d
        return asset_request_public_dto

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
