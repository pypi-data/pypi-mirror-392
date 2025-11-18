from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.evidence_library_renewal_schema_response_public_dto_renewal_schedule_type import (
    EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="EvidenceLibraryRenewalSchemaResponsePublicDto")


@_attrs_define
class EvidenceLibraryRenewalSchemaResponsePublicDto:
    """
    Attributes:
        renewal_date (Union[None, Unset, str]): Evidence renewal date Example: 2020-07-06.
        renewal_schedule_type (Union[Unset, EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType]): The
            renewal date schedule type of evidence Example: ONE_YEAR.
    """

    renewal_date: Union[None, Unset, str] = UNSET
    renewal_schedule_type: Union[Unset, EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        renewal_date: Union[None, Unset, str]
        if isinstance(self.renewal_date, Unset):
            renewal_date = UNSET
        else:
            renewal_date = self.renewal_date

        renewal_schedule_type: Union[Unset, str] = UNSET
        if not isinstance(self.renewal_schedule_type, Unset):
            renewal_schedule_type = self.renewal_schedule_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if renewal_date is not UNSET:
            field_dict["renewalDate"] = renewal_date
        if renewal_schedule_type is not UNSET:
            field_dict["renewalScheduleType"] = renewal_schedule_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_renewal_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        renewal_date = _parse_renewal_date(d.pop("renewalDate", UNSET))

        _renewal_schedule_type = d.pop("renewalScheduleType", UNSET)
        renewal_schedule_type: Union[Unset, EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType]
        if isinstance(_renewal_schedule_type, Unset):
            renewal_schedule_type = UNSET
        else:
            renewal_schedule_type = EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType(
                _renewal_schedule_type
            )

        evidence_library_renewal_schema_response_public_dto = cls(
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
        )

        evidence_library_renewal_schema_response_public_dto.additional_properties = d
        return evidence_library_renewal_schema_response_public_dto

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
