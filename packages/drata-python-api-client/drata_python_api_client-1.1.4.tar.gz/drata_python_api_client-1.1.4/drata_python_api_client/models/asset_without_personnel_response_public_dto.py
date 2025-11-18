import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssetWithoutPersonnelResponsePublicDto")


@_attrs_define
class AssetWithoutPersonnelResponsePublicDto:
    """
    Attributes:
        id (float): Assessment ID Example: 1.
        name (str): The name of the asset Example: MacBook Pro - Space Black 16-inch.
        description (str): The description of the asset Example: MacBook Pro Space Black - with 16-inch Liquid Retina
            XDR display.
        asset_type (str): The asset type Example: PHYSICAL.
        asset_provider (str): The asset source provider Example: AGENT.
        approved_at (datetime.datetime): When the asset was approved (if applicable) Example: 2025-07-01T16:45:55.246Z.
        company (str): The owning company of the asset Example: Acme, Inc.
        asset_reference_type (Union[None, str]): The asset reference type Example: PERSONNEL.
        unique_id (str): Unique Id associated with this asset Example: C02T6CDJGTFL.
        created_at (datetime.datetime): asset created timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): asset update timestamp Example: 2025-07-01T16:45:55.246Z.
        removed_at (Union[None, Unset, datetime.datetime]): When the asset stopped being tracked Example:
            2025-07-01T16:45:55.246Z.
        notes (Union[None, Unset, str]): The asset notes
        external_id (Union[Unset, str]): An externally sourced unique identifier for a virtual asset Example:
            i-0c844e3b433e4e3f.
        external_owner_id (Union[Unset, str]): Used to track the source of virtual assets, typically an account id.
            Example: account-353.
    """

    id: float
    name: str
    description: str
    asset_type: str
    asset_provider: str
    approved_at: datetime.datetime
    company: str
    asset_reference_type: Union[None, str]
    unique_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    removed_at: Union[None, Unset, datetime.datetime] = UNSET
    notes: Union[None, Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    external_owner_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        asset_type = self.asset_type

        asset_provider = self.asset_provider

        approved_at = self.approved_at.isoformat()

        company = self.company

        asset_reference_type: Union[None, str]
        asset_reference_type = self.asset_reference_type

        unique_id = self.unique_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        removed_at: Union[None, Unset, str]
        if isinstance(self.removed_at, Unset):
            removed_at = UNSET
        elif isinstance(self.removed_at, datetime.datetime):
            removed_at = self.removed_at.isoformat()
        else:
            removed_at = self.removed_at

        notes: Union[None, Unset, str]
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        external_id = self.external_id

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
                "company": company,
                "assetReferenceType": asset_reference_type,
                "uniqueId": unique_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if removed_at is not UNSET:
            field_dict["removedAt"] = removed_at
        if notes is not UNSET:
            field_dict["notes"] = notes
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if external_owner_id is not UNSET:
            field_dict["externalOwnerId"] = external_owner_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        asset_type = d.pop("assetType")

        asset_provider = d.pop("assetProvider")

        approved_at = isoparse(d.pop("approvedAt"))

        company = d.pop("company")

        def _parse_asset_reference_type(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        asset_reference_type = _parse_asset_reference_type(d.pop("assetReferenceType"))

        unique_id = d.pop("uniqueId")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_removed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                removed_at_type_0 = isoparse(data)

                return removed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        removed_at = _parse_removed_at(d.pop("removedAt", UNSET))

        def _parse_notes(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        notes = _parse_notes(d.pop("notes", UNSET))

        external_id = d.pop("externalId", UNSET)

        external_owner_id = d.pop("externalOwnerId", UNSET)

        asset_without_personnel_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            asset_type=asset_type,
            asset_provider=asset_provider,
            approved_at=approved_at,
            company=company,
            asset_reference_type=asset_reference_type,
            unique_id=unique_id,
            created_at=created_at,
            updated_at=updated_at,
            removed_at=removed_at,
            notes=notes,
            external_id=external_id,
            external_owner_id=external_owner_id,
        )

        asset_without_personnel_response_public_dto.additional_properties = d
        return asset_without_personnel_response_public_dto

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
