from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MonitorMetadataDataResponsePublicDto")


@_attrs_define
class MonitorMetadataDataResponsePublicDto:
    """
    Attributes:
        id (str): The metadata data id Example: 123.
        name (str): The name of the data Example: Risk Assessment Report.
        display_name (str): The display name of the data Example: The Risk Assessment Report.
        email (str): The email of the data Example: joe@google.com.
        avatar_url (str): The avatar of the data Example: https://avatar.url.
        url (str):  Example: https://tracking.com/issues/420.
        groups (Union[Unset, list[str]]):  Example: ["group1", "group2"].
    """

    id: str
    name: str
    display_name: str
    email: str
    avatar_url: str
    url: str
    groups: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        email = self.email

        avatar_url = self.avatar_url

        url = self.url

        groups: Union[Unset, list[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "displayName": display_name,
                "email": email,
                "avatarUrl": avatar_url,
                "url": url,
            }
        )
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        display_name = d.pop("displayName")

        email = d.pop("email")

        avatar_url = d.pop("avatarUrl")

        url = d.pop("url")

        groups = cast(list[str], d.pop("groups", UNSET))

        monitor_metadata_data_response_public_dto = cls(
            id=id,
            name=name,
            display_name=display_name,
            email=email,
            avatar_url=avatar_url,
            url=url,
            groups=groups,
        )

        monitor_metadata_data_response_public_dto.additional_properties = d
        return monitor_metadata_data_response_public_dto

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
