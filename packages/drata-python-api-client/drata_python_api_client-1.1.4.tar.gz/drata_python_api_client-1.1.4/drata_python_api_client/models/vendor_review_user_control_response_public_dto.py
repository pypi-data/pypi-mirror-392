from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VendorReviewUserControlResponsePublicDto")


@_attrs_define
class VendorReviewUserControlResponsePublicDto:
    """
    Attributes:
        id (float): Vendor review user control ID Example: 1.
        name (str): Vendor review user control name Example: End User Control 1.
        in_place (bool): Vendor review user control in place Example: True.
    """

    id: float
    name: str
    in_place: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        in_place = self.in_place

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "inPlace": in_place,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        in_place = d.pop("inPlace")

        vendor_review_user_control_response_public_dto = cls(
            id=id,
            name=name,
            in_place=in_place,
        )

        vendor_review_user_control_response_public_dto.additional_properties = d
        return vendor_review_user_control_response_public_dto

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
