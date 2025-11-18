import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.asset_class_type_response_public_dto import AssetClassTypeResponsePublicDto
    from ..models.device_response_public_dto import DeviceResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="AssetResponsePublicDto")


@_attrs_define
class AssetResponsePublicDto:
    """
    Attributes:
        id (float): Assessment ID Example: 1.
        name (str): The name of the asset Example: MacbookPro 13.
        description (str): The description of the asset Example: MacbookPro 13.
        asset_type (str): The asset type Example: PHYSICAL.
        asset_provider (str): The asset source provider Example: AGENT.
        approved_at (datetime.datetime): When the asset was approved (if applicable) Example: 2025-07-01T16:45:55.246Z.
        removed_at (datetime.datetime): When the asset stopped being tracked Example: 2025-07-01T16:45:55.246Z.
        asset_class_types (list['AssetClassTypeResponsePublicDto']): Asset class types associated to this asset Example:
            AssetClassTypeResponseDto[].
        company (str): The owning company of the asset Example: Acme, Inc.
        owner (UserResponsePublicDto):
        notes (str): The asset notes
        asset_reference_type (str): The asset reference type Example: PERSONNEL.
        unique_id (str): Unique Id associated with this asset Example: C02T6CDJGTFL.
        created_at (datetime.datetime): asset created timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): asset update timestamp Example: 2025-07-01T16:45:55.246Z.
        device (DeviceResponsePublicDto):
        external_id (str): An externally sourced unique identifier for a virtual asset Example: i-0c844e3b433e4e3f.
        employment_status (Union[Unset, str]): The employment status of the personnel Example: CURRENT_EMPLOYEE.
        external_owner_id (Union[Unset, str]): Used to track the source of virtual assets, typically an account id.
            Example: account-353.
    """

    id: float
    name: str
    description: str
    asset_type: str
    asset_provider: str
    approved_at: datetime.datetime
    removed_at: datetime.datetime
    asset_class_types: list["AssetClassTypeResponsePublicDto"]
    company: str
    owner: "UserResponsePublicDto"
    notes: str
    asset_reference_type: str
    unique_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    device: "DeviceResponsePublicDto"
    external_id: str
    employment_status: Union[Unset, str] = UNSET
    external_owner_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        asset_type = self.asset_type

        asset_provider = self.asset_provider

        approved_at = self.approved_at.isoformat()

        removed_at = self.removed_at.isoformat()

        asset_class_types = []
        for asset_class_types_item_data in self.asset_class_types:
            asset_class_types_item = asset_class_types_item_data.to_dict()
            asset_class_types.append(asset_class_types_item)

        company = self.company

        owner = self.owner.to_dict()

        notes = self.notes

        asset_reference_type = self.asset_reference_type

        unique_id = self.unique_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        device = self.device.to_dict()

        external_id = self.external_id

        employment_status = self.employment_status

        external_owner_id = self.external_owner_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "assetType": asset_type,
                "assetProvider": asset_provider,
                "approvedAt": approved_at,
                "removedAt": removed_at,
                "assetClassTypes": asset_class_types,
                "company": company,
                "owner": owner,
                "notes": notes,
                "assetReferenceType": asset_reference_type,
                "uniqueId": unique_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "device": device,
                "externalId": external_id,
            }
        )
        if employment_status is not UNSET:
            field_dict["employmentStatus"] = employment_status
        if external_owner_id is not UNSET:
            field_dict["externalOwnerId"] = external_owner_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.asset_class_type_response_public_dto import AssetClassTypeResponsePublicDto
        from ..models.device_response_public_dto import DeviceResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        asset_type = d.pop("assetType")

        asset_provider = d.pop("assetProvider")

        approved_at = isoparse(d.pop("approvedAt"))

        removed_at = isoparse(d.pop("removedAt"))

        asset_class_types = []
        _asset_class_types = d.pop("assetClassTypes")
        for asset_class_types_item_data in _asset_class_types:
            asset_class_types_item = AssetClassTypeResponsePublicDto.from_dict(asset_class_types_item_data)

            asset_class_types.append(asset_class_types_item)

        company = d.pop("company")

        owner = UserResponsePublicDto.from_dict(d.pop("owner"))

        notes = d.pop("notes")

        asset_reference_type = d.pop("assetReferenceType")

        unique_id = d.pop("uniqueId")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        device = DeviceResponsePublicDto.from_dict(d.pop("device"))

        external_id = d.pop("externalId")

        employment_status = d.pop("employmentStatus", UNSET)

        external_owner_id = d.pop("externalOwnerId", UNSET)

        asset_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            asset_type=asset_type,
            asset_provider=asset_provider,
            approved_at=approved_at,
            removed_at=removed_at,
            asset_class_types=asset_class_types,
            company=company,
            owner=owner,
            notes=notes,
            asset_reference_type=asset_reference_type,
            unique_id=unique_id,
            created_at=created_at,
            updated_at=updated_at,
            device=device,
            external_id=external_id,
            employment_status=employment_status,
            external_owner_id=external_owner_id,
        )

        asset_response_public_dto.additional_properties = d
        return asset_response_public_dto

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
