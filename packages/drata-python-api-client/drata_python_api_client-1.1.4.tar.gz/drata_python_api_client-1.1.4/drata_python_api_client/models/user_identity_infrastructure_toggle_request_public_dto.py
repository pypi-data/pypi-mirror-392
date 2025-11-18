from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_identity_infrastructure_toggle_request_public_dto_toggle_field import (
    UserIdentityInfrastructureToggleRequestPublicDtoToggleField,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserIdentityInfrastructureToggleRequestPublicDto")


@_attrs_define
class UserIdentityInfrastructureToggleRequestPublicDto:
    """
    Attributes:
        toggle (bool): Toggle value for the setting Example: True.
        toggle_field (Union[Unset, UserIdentityInfrastructureToggleRequestPublicDtoToggleField]): The toggle field type
            to update Example: INFRASTRUCTURE_ADMIN_ACCESS.
    """

    toggle: bool
    toggle_field: Union[Unset, UserIdentityInfrastructureToggleRequestPublicDtoToggleField] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        toggle = self.toggle

        toggle_field: Union[Unset, str] = UNSET
        if not isinstance(self.toggle_field, Unset):
            toggle_field = self.toggle_field.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "toggle": toggle,
            }
        )
        if toggle_field is not UNSET:
            field_dict["toggleField"] = toggle_field

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        toggle = d.pop("toggle")

        _toggle_field = d.pop("toggleField", UNSET)
        toggle_field: Union[Unset, UserIdentityInfrastructureToggleRequestPublicDtoToggleField]
        if isinstance(_toggle_field, Unset):
            toggle_field = UNSET
        else:
            toggle_field = UserIdentityInfrastructureToggleRequestPublicDtoToggleField(_toggle_field)

        user_identity_infrastructure_toggle_request_public_dto = cls(
            toggle=toggle,
            toggle_field=toggle_field,
        )

        user_identity_infrastructure_toggle_request_public_dto.additional_properties = d
        return user_identity_infrastructure_toggle_request_public_dto

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
