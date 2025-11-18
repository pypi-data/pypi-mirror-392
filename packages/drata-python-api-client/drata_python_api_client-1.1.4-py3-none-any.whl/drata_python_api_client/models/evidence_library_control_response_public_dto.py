import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.evidence_library_renewal_schema_response_public_dto import (
        EvidenceLibraryRenewalSchemaResponsePublicDto,
    )
    from ..models.evidence_library_version_response_public_dto import EvidenceLibraryVersionResponsePublicDto


T = TypeVar("T", bound="EvidenceLibraryControlResponsePublicDto")


@_attrs_define
class EvidenceLibraryControlResponsePublicDto:
    """
    Attributes:
        id (float): Evidence id Example: 1.
        name (str): The name of the evidence Example: Security training.
        description (str): The description of the evidence Example: Security Training completed evidence test.
        versions (list['EvidenceLibraryVersionResponsePublicDto']): Library document linked versions data Example:
            [{'id': 1, 'source': 'https://drata.com/evidence', 'type': 'URL', 'version': 1, 'current': True, 'filedAt':
            '2020-07-06'}].
        created_at (datetime.datetime): Evidence created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Evidence updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        renewal_schema (EvidenceLibraryRenewalSchemaResponsePublicDto):
        is_expired (bool): The evidence is expired; passed its renewal date
    """

    id: float
    name: str
    description: str
    versions: list["EvidenceLibraryVersionResponsePublicDto"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    renewal_schema: "EvidenceLibraryRenewalSchemaResponsePublicDto"
    is_expired: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        renewal_schema = self.renewal_schema.to_dict()

        is_expired = self.is_expired

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "versions": versions,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "renewalSchema": renewal_schema,
                "isExpired": is_expired,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evidence_library_renewal_schema_response_public_dto import (
            EvidenceLibraryRenewalSchemaResponsePublicDto,
        )
        from ..models.evidence_library_version_response_public_dto import EvidenceLibraryVersionResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = EvidenceLibraryVersionResponsePublicDto.from_dict(versions_item_data)

            versions.append(versions_item)

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        renewal_schema = EvidenceLibraryRenewalSchemaResponsePublicDto.from_dict(d.pop("renewalSchema"))

        is_expired = d.pop("isExpired")

        evidence_library_control_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            versions=versions,
            created_at=created_at,
            updated_at=updated_at,
            renewal_schema=renewal_schema,
            is_expired=is_expired,
        )

        evidence_library_control_response_public_dto.additional_properties = d
        return evidence_library_control_response_public_dto

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
