from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonnelContractDateRequestPublicDto")


@_attrs_define
class PersonnelContractDateRequestPublicDto:
    """
    Attributes:
        start_date (str): The date when this person started working on the company Example: 2020-07-06.
        separation_date (Union[Unset, str]): The date when this person was separated from the company system. Example:
            2020-07-06.
    """

    start_date: str
    separation_date: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date

        separation_date = self.separation_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startDate": start_date,
            }
        )
        if separation_date is not UNSET:
            field_dict["separationDate"] = separation_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_date = d.pop("startDate")

        separation_date = d.pop("separationDate", UNSET)

        personnel_contract_date_request_public_dto = cls(
            start_date=start_date,
            separation_date=separation_date,
        )

        personnel_contract_date_request_public_dto.additional_properties = d
        return personnel_contract_date_request_public_dto

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
