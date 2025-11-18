from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trust_center_approve_request_request_public_dto_expiration_type import (
    TrustCenterApproveRequestRequestPublicDtoExpirationType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TrustCenterApproveRequestRequestPublicDto")


@_attrs_define
class TrustCenterApproveRequestRequestPublicDto:
    """
    Attributes:
        expiration_type (TrustCenterApproveRequestRequestPublicDtoExpirationType): Default Access Length Type Example:
            DAYS.
        expiration (Union[Unset, float]): Number of days to expire Example: 365.
        is_new_expiration (Union[Unset, bool]): Is update expiration date checked
    """

    expiration_type: TrustCenterApproveRequestRequestPublicDtoExpirationType
    expiration: Union[Unset, float] = UNSET
    is_new_expiration: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expiration_type = self.expiration_type.value

        expiration = self.expiration

        is_new_expiration = self.is_new_expiration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expirationType": expiration_type,
            }
        )
        if expiration is not UNSET:
            field_dict["expiration"] = expiration
        if is_new_expiration is not UNSET:
            field_dict["isNewExpiration"] = is_new_expiration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expiration_type = TrustCenterApproveRequestRequestPublicDtoExpirationType(d.pop("expirationType"))

        expiration = d.pop("expiration", UNSET)

        is_new_expiration = d.pop("isNewExpiration", UNSET)

        trust_center_approve_request_request_public_dto = cls(
            expiration_type=expiration_type,
            expiration=expiration,
            is_new_expiration=is_new_expiration,
        )

        trust_center_approve_request_request_public_dto.additional_properties = d
        return trust_center_approve_request_request_public_dto

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
