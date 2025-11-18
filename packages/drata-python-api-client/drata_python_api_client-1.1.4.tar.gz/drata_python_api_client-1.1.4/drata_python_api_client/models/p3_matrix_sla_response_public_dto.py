import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="P3MatrixSLAResponsePublicDto")


@_attrs_define
class P3MatrixSLAResponsePublicDto:
    """
    Attributes:
        id (float): Week time frame SLA ID Example: 1.
        policy_p3_matrix_sla_id (float): The corresponding P3 matrix SLA ID this value is for Example: 1.
        definition (str): The description for this matrix item Example: Vulnerabilities that cause a privilege
            escalation on the platform from unprivileged....
        severity (str): The severity level Example: LOW.
        time_frame (str): The time frame value Example: ONE_DAY.
        examples (str): Examples of when this SLA is relevant Example: Vulnerabilities that result in compromising the
            system such as Sql injection....
        created_at (datetime.datetime): Created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    policy_p3_matrix_sla_id: float
    definition: str
    severity: str
    time_frame: str
    examples: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        policy_p3_matrix_sla_id = self.policy_p3_matrix_sla_id

        definition = self.definition

        severity = self.severity

        time_frame = self.time_frame

        examples = self.examples

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "policyP3MatrixSLAId": policy_p3_matrix_sla_id,
                "definition": definition,
                "severity": severity,
                "timeFrame": time_frame,
                "examples": examples,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        policy_p3_matrix_sla_id = d.pop("policyP3MatrixSLAId")

        definition = d.pop("definition")

        severity = d.pop("severity")

        time_frame = d.pop("timeFrame")

        examples = d.pop("examples")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        p3_matrix_sla_response_public_dto = cls(
            id=id,
            policy_p3_matrix_sla_id=policy_p3_matrix_sla_id,
            definition=definition,
            severity=severity,
            time_frame=time_frame,
            examples=examples,
            created_at=created_at,
            updated_at=updated_at,
        )

        p3_matrix_sla_response_public_dto.additional_properties = d
        return p3_matrix_sla_response_public_dto

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
