from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SlackUserRequestPublicDto")


@_attrs_define
class SlackUserRequestPublicDto:
    """
    Attributes:
        id (str):
        username (str):
        name (str):
        team_id (str):
    """

    id: str
    username: str
    name: str
    team_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        username = self.username

        name = self.name

        team_id = self.team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "username": username,
                "name": name,
                "team_id": team_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        username = d.pop("username")

        name = d.pop("name")

        team_id = d.pop("team_id")

        slack_user_request_public_dto = cls(
            id=id,
            username=username,
            name=name,
            team_id=team_id,
        )

        slack_user_request_public_dto.additional_properties = d
        return slack_user_request_public_dto

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
