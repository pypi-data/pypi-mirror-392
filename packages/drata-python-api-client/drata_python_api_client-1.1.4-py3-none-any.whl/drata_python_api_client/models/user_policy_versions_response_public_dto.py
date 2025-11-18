from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_policy_version_response_public_dto import UserPolicyVersionResponsePublicDto


T = TypeVar("T", bound="UserPolicyVersionsResponsePublicDto")


@_attrs_define
class UserPolicyVersionsResponsePublicDto:
    """
    Attributes:
        user_policy_versions (list['UserPolicyVersionResponsePublicDto']): The set of current policy versions for a
            target user
    """

    user_policy_versions: list["UserPolicyVersionResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_policy_versions = []
        for user_policy_versions_item_data in self.user_policy_versions:
            user_policy_versions_item = user_policy_versions_item_data.to_dict()
            user_policy_versions.append(user_policy_versions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userPolicyVersions": user_policy_versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_policy_version_response_public_dto import UserPolicyVersionResponsePublicDto

        d = dict(src_dict)
        user_policy_versions = []
        _user_policy_versions = d.pop("userPolicyVersions")
        for user_policy_versions_item_data in _user_policy_versions:
            user_policy_versions_item = UserPolicyVersionResponsePublicDto.from_dict(user_policy_versions_item_data)

            user_policy_versions.append(user_policy_versions_item)

        user_policy_versions_response_public_dto = cls(
            user_policy_versions=user_policy_versions,
        )

        user_policy_versions_response_public_dto.additional_properties = d
        return user_policy_versions_response_public_dto

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
