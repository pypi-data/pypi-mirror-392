from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VendorTypeStatsResponsePublicDto")


@_attrs_define
class VendorTypeStatsResponsePublicDto:
    """
    Attributes:
        key (str): Name of the vendor type Example: CONTRACTOR.
        amount (float): Count of records Example: 10.
    """

    key: str
    amount: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        amount = self.amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "amount": amount,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key")

        amount = d.pop("amount")

        vendor_type_stats_response_public_dto = cls(
            key=key,
            amount=amount,
        )

        vendor_type_stats_response_public_dto.additional_properties = d
        return vendor_type_stats_response_public_dto

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
