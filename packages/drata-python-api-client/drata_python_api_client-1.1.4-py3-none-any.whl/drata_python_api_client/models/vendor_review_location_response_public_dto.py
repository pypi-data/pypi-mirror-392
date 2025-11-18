from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VendorReviewLocationResponsePublicDto")


@_attrs_define
class VendorReviewLocationResponsePublicDto:
    """
    Attributes:
        id (float): Vendor review location ID Example: 1.
        city (str): Vendor review location city Example: San Diego.
        state_country (str): Vendor review location state Example: CA.
    """

    id: float
    city: str
    state_country: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        city = self.city

        state_country = self.state_country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "city": city,
                "stateCountry": state_country,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        city = d.pop("city")

        state_country = d.pop("stateCountry")

        vendor_review_location_response_public_dto = cls(
            id=id,
            city=city,
            state_country=state_country,
        )

        vendor_review_location_response_public_dto.additional_properties = d
        return vendor_review_location_response_public_dto

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
