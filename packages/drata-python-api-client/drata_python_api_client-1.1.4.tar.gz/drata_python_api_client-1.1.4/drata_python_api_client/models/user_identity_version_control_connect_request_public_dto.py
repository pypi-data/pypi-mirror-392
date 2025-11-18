from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserIdentityVersionControlConnectRequestPublicDto")


@_attrs_define
class UserIdentityVersionControlConnectRequestPublicDto:
    """
    Attributes:
        user_id (Union[None, float]): The desired user id to link or null to unlink Example: 1.
    """

    user_id: Union[None, float]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id: Union[None, float]
        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userId": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_user_id(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        user_id = _parse_user_id(d.pop("userId"))

        user_identity_version_control_connect_request_public_dto = cls(
            user_id=user_id,
        )

        user_identity_version_control_connect_request_public_dto.additional_properties = d
        return user_identity_version_control_connect_request_public_dto

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
