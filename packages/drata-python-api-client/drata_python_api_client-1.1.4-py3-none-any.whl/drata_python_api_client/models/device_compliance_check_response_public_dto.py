import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="DeviceComplianceCheckResponsePublicDto")


@_attrs_define
class DeviceComplianceCheckResponsePublicDto:
    """
    Attributes:
        id (float): Device compliance check ID Example: 1.
        status (str): Denotes actual compliance Example: PASS.
        type_ (str): The compliance type Example: PASSWORD_MANAGER.
        expires_at (datetime.datetime): When this compliance is due for a re-verification Example:
            2025-07-01T16:45:55.246Z.
        check_frequency (str): How often should this check be run for compliance Example: DAILY.
        last_checked_at (datetime.datetime): Compliance check last checked timestamp Example: 2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): Compliance check creation timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Compliance check updated timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    status: str
    type_: str
    expires_at: datetime.datetime
    check_frequency: str
    last_checked_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        type_ = self.type_

        expires_at = self.expires_at.isoformat()

        check_frequency = self.check_frequency

        last_checked_at = self.last_checked_at.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "type": type_,
                "expiresAt": expires_at,
                "checkFrequency": check_frequency,
                "lastCheckedAt": last_checked_at,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        status = d.pop("status")

        type_ = d.pop("type")

        expires_at = isoparse(d.pop("expiresAt"))

        check_frequency = d.pop("checkFrequency")

        last_checked_at = isoparse(d.pop("lastCheckedAt"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        device_compliance_check_response_public_dto = cls(
            id=id,
            status=status,
            type_=type_,
            expires_at=expires_at,
            check_frequency=check_frequency,
            last_checked_at=last_checked_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        device_compliance_check_response_public_dto.additional_properties = d
        return device_compliance_check_response_public_dto

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
