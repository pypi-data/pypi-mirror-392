import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.control_monitor_response_public_dto import ControlMonitorResponsePublicDto
    from ..models.evidence_library_renewal_schema_response_public_dto import (
        EvidenceLibraryRenewalSchemaResponsePublicDto,
    )
    from ..models.evidence_library_version_response_public_dto import EvidenceLibraryVersionResponsePublicDto
    from ..models.user_card_response_public_dto import UserCardResponsePublicDto


T = TypeVar("T", bound="EvidenceResponsePublicDto")


@_attrs_define
class EvidenceResponsePublicDto:
    """
    Attributes:
        id (float): Evidence id Example: 1.
        name (str): The name of the evidence Example: Security training.
        description (str): The description of the evidence Example: Security Training completed evidence test.
        implementation_guidance (str): Guidance for implementing evidence Example: Example of architectural diagram
            www.drata/arch-diagram-example.com.
        created_at (datetime.datetime): Evidence created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Evidence updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        user (UserCardResponsePublicDto):
        controls (list['ControlMonitorResponsePublicDto']): Array of controls mapped to this evidence
        renewal_schema (EvidenceLibraryRenewalSchemaResponsePublicDto):
        is_expired (bool): The evidence is expired; passed its renewal date
        versions (list['EvidenceLibraryVersionResponsePublicDto']): Library document linked versions data Example:
            [{'id': 1, 'source': 'https://drata.com/evidence', 'type': 'URL', 'version': 1, 'current': True, 'filedAt':
            '2020-07-06'}].
    """

    id: float
    name: str
    description: str
    implementation_guidance: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user: "UserCardResponsePublicDto"
    controls: list["ControlMonitorResponsePublicDto"]
    renewal_schema: "EvidenceLibraryRenewalSchemaResponsePublicDto"
    is_expired: bool
    versions: list["EvidenceLibraryVersionResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        implementation_guidance = self.implementation_guidance

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        user = self.user.to_dict()

        controls = []
        for controls_item_data in self.controls:
            controls_item = controls_item_data.to_dict()
            controls.append(controls_item)

        renewal_schema = self.renewal_schema.to_dict()

        is_expired = self.is_expired

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "implementationGuidance": implementation_guidance,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "user": user,
                "controls": controls,
                "renewalSchema": renewal_schema,
                "isExpired": is_expired,
                "versions": versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.control_monitor_response_public_dto import ControlMonitorResponsePublicDto
        from ..models.evidence_library_renewal_schema_response_public_dto import (
            EvidenceLibraryRenewalSchemaResponsePublicDto,
        )
        from ..models.evidence_library_version_response_public_dto import EvidenceLibraryVersionResponsePublicDto
        from ..models.user_card_response_public_dto import UserCardResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        implementation_guidance = d.pop("implementationGuidance")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        user = UserCardResponsePublicDto.from_dict(d.pop("user"))

        controls = []
        _controls = d.pop("controls")
        for controls_item_data in _controls:
            controls_item = ControlMonitorResponsePublicDto.from_dict(controls_item_data)

            controls.append(controls_item)

        renewal_schema = EvidenceLibraryRenewalSchemaResponsePublicDto.from_dict(d.pop("renewalSchema"))

        is_expired = d.pop("isExpired")

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = EvidenceLibraryVersionResponsePublicDto.from_dict(versions_item_data)

            versions.append(versions_item)

        evidence_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            implementation_guidance=implementation_guidance,
            created_at=created_at,
            updated_at=updated_at,
            user=user,
            controls=controls,
            renewal_schema=renewal_schema,
            is_expired=is_expired,
            versions=versions,
        )

        evidence_response_public_dto.additional_properties = d
        return evidence_response_public_dto

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
