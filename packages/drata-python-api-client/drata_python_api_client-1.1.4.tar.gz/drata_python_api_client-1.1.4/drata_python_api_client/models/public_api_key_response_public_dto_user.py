from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PublicApiKeyResponsePublicDtoUser")


@_attrs_define
class PublicApiKeyResponsePublicDtoUser:
    """A user Info

    Example:
        {'firstName': 'FirstnameTest', 'lastName': 'LastnameTest', 'email': 'Email@test.com', 'avatarUrl': 'https://cdn-
            prod.imgpilot.com/avatar.png'}

    Attributes:
        id (Union[Unset, float]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        email (Union[Unset, str]):
        avatar_url (Union[Unset, str]):
    """

    id: Union[Unset, float] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    avatar_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        avatar_url = self.avatar_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if email is not UNSET:
            field_dict["email"] = email
        if avatar_url is not UNSET:
            field_dict["avatarUrl"] = avatar_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        email = d.pop("email", UNSET)

        avatar_url = d.pop("avatarUrl", UNSET)

        public_api_key_response_public_dto_user = cls(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            avatar_url=avatar_url,
        )

        public_api_key_response_public_dto_user.additional_properties = d
        return public_api_key_response_public_dto_user

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
