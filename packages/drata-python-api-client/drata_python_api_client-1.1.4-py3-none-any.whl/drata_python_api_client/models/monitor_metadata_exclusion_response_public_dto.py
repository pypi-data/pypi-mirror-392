import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.connection_response_public_dto import ConnectionResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="MonitorMetadataExclusionResponsePublicDto")


@_attrs_define
class MonitorMetadataExclusionResponsePublicDto:
    """
    Attributes:
        id (float): The id of the exclusion Example: 1.
        target_id (str): The id of the target exclusion Example: sg-12345.
        target_name (str): The name of the target exclusion Example: Drata Default Security Group.
        exclusion_reason (str): The reason for the excluded resource Example: An excluded resource.
        exclusion_designator (UserResponsePublicDto):
        connection (ConnectionResponsePublicDto):
        created_at (datetime.datetime): Exclusion created timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Exclusion update timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    target_id: str
    target_name: str
    exclusion_reason: str
    exclusion_designator: "UserResponsePublicDto"
    connection: "ConnectionResponsePublicDto"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        target_id = self.target_id

        target_name = self.target_name

        exclusion_reason = self.exclusion_reason

        exclusion_designator = self.exclusion_designator.to_dict()

        connection = self.connection.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "targetId": target_id,
                "targetName": target_name,
                "exclusionReason": exclusion_reason,
                "exclusionDesignator": exclusion_designator,
                "connection": connection,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_response_public_dto import ConnectionResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        target_id = d.pop("targetId")

        target_name = d.pop("targetName")

        exclusion_reason = d.pop("exclusionReason")

        exclusion_designator = UserResponsePublicDto.from_dict(d.pop("exclusionDesignator"))

        connection = ConnectionResponsePublicDto.from_dict(d.pop("connection"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        monitor_metadata_exclusion_response_public_dto = cls(
            id=id,
            target_id=target_id,
            target_name=target_name,
            exclusion_reason=exclusion_reason,
            exclusion_designator=exclusion_designator,
            connection=connection,
            created_at=created_at,
            updated_at=updated_at,
        )

        monitor_metadata_exclusion_response_public_dto.additional_properties = d
        return monitor_metadata_exclusion_response_public_dto

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
