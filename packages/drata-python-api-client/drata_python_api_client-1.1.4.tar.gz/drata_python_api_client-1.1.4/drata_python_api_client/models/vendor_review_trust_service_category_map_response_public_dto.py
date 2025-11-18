from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VendorReviewTrustServiceCategoryMapResponsePublicDto")


@_attrs_define
class VendorReviewTrustServiceCategoryMapResponsePublicDto:
    """
    Attributes:
        id (float): Vendor review trust service category ID Example: 1.
        category (Union[None, float]): Vendor review trust service category Example: AVAILABILITY.
    """

    id: float
    category: Union[None, float]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        category: Union[None, float]
        category = self.category

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "category": category,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_category(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        category = _parse_category(d.pop("category"))

        vendor_review_trust_service_category_map_response_public_dto = cls(
            id=id,
            category=category,
        )

        vendor_review_trust_service_category_map_response_public_dto.additional_properties = d
        return vendor_review_trust_service_category_map_response_public_dto

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
