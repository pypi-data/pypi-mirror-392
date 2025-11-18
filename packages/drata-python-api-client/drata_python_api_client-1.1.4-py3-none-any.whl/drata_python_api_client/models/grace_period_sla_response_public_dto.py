import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="GracePeriodSLAResponsePublicDto")


@_attrs_define
class GracePeriodSLAResponsePublicDto:
    """
    Attributes:
        id (float): Grace period SLA ID Example: 1.
        policy_grace_period_sla_id (float): The corresponding policy grace period SLA ID this value is for Example: 1.
        grace_period (str): The grace period value Example: SEVEN_DAYS.
        created_at (datetime.datetime): Created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    policy_grace_period_sla_id: float
    grace_period: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        policy_grace_period_sla_id = self.policy_grace_period_sla_id

        grace_period = self.grace_period

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "policyGracePeriodSLAId": policy_grace_period_sla_id,
                "gracePeriod": grace_period,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        policy_grace_period_sla_id = d.pop("policyGracePeriodSLAId")

        grace_period = d.pop("gracePeriod")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        grace_period_sla_response_public_dto = cls(
            id=id,
            policy_grace_period_sla_id=policy_grace_period_sla_id,
            grace_period=grace_period,
            created_at=created_at,
            updated_at=updated_at,
        )

        grace_period_sla_response_public_dto.additional_properties = d
        return grace_period_sla_response_public_dto

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
