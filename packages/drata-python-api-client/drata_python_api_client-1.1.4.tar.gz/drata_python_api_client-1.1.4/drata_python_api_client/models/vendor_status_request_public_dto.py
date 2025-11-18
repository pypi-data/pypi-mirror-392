from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vendor_status_request_public_dto_vendor_status import VendorStatusRequestPublicDtoVendorStatus

T = TypeVar("T", bound="VendorStatusRequestPublicDto")


@_attrs_define
class VendorStatusRequestPublicDto:
    """
    Attributes:
        vendor_status (VendorStatusRequestPublicDtoVendorStatus): Status to update the targeted vendor Example:
            ARCHIVED.
    """

    vendor_status: VendorStatusRequestPublicDtoVendorStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vendor_status = self.vendor_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vendorStatus": vendor_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vendor_status = VendorStatusRequestPublicDtoVendorStatus(d.pop("vendorStatus"))

        vendor_status_request_public_dto = cls(
            vendor_status=vendor_status,
        )

        vendor_status_request_public_dto.additional_properties = d
        return vendor_status_request_public_dto

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
