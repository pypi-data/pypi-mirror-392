from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.personnel_status_request_public_dto_employment_status import (
    PersonnelStatusRequestPublicDtoEmploymentStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonnelStatusRequestPublicDto")


@_attrs_define
class PersonnelStatusRequestPublicDto:
    """
    Attributes:
        employment_status (PersonnelStatusRequestPublicDtoEmploymentStatus): The new employment status for this
            personnel Example: CURRENT_EMPLOYEE.
        not_human_reason (Union[Unset, str]): Explains why the employment status of this personnel is marked as
            OUT_OF_SCOPE. This field is required if the employmentStatus is set to OUT_OF_SCOPE. Example: This is not a real
            personnel, but a placeholder for anyone in charge of X.
        separation_date (Union[Unset, str]): The date when this personnel was separated from the company system. This
            field is required if the employmentStatus is either FORMER_EMPLOYEE or FORMER_CONTRACTOR Example: 2020-07-06.
    """

    employment_status: PersonnelStatusRequestPublicDtoEmploymentStatus
    not_human_reason: Union[Unset, str] = UNSET
    separation_date: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        employment_status = self.employment_status.value

        not_human_reason = self.not_human_reason

        separation_date = self.separation_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "employmentStatus": employment_status,
            }
        )
        if not_human_reason is not UNSET:
            field_dict["notHumanReason"] = not_human_reason
        if separation_date is not UNSET:
            field_dict["separationDate"] = separation_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        employment_status = PersonnelStatusRequestPublicDtoEmploymentStatus(d.pop("employmentStatus"))

        not_human_reason = d.pop("notHumanReason", UNSET)

        separation_date = d.pop("separationDate", UNSET)

        personnel_status_request_public_dto = cls(
            employment_status=employment_status,
            not_human_reason=not_human_reason,
            separation_date=separation_date,
        )

        personnel_status_request_public_dto.additional_properties = d
        return personnel_status_request_public_dto

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
