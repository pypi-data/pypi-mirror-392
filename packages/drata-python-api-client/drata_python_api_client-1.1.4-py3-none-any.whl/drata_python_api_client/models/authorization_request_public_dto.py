from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AuthorizationRequestPublicDto")


@_attrs_define
class AuthorizationRequestPublicDto:
    """
    Attributes:
        enterprise_id (Union[None, str]):
        team_id (str):
        user_id (str):
        is_bot (bool):
        is_enterprise_install (bool):
    """

    enterprise_id: Union[None, str]
    team_id: str
    user_id: str
    is_bot: bool
    is_enterprise_install: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enterprise_id: Union[None, str]
        enterprise_id = self.enterprise_id

        team_id = self.team_id

        user_id = self.user_id

        is_bot = self.is_bot

        is_enterprise_install = self.is_enterprise_install

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enterprise_id": enterprise_id,
                "team_id": team_id,
                "user_id": user_id,
                "is_bot": is_bot,
                "is_enterprise_install": is_enterprise_install,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_enterprise_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        enterprise_id = _parse_enterprise_id(d.pop("enterprise_id"))

        team_id = d.pop("team_id")

        user_id = d.pop("user_id")

        is_bot = d.pop("is_bot")

        is_enterprise_install = d.pop("is_enterprise_install")

        authorization_request_public_dto = cls(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
            is_bot=is_bot,
            is_enterprise_install=is_enterprise_install,
        )

        authorization_request_public_dto.additional_properties = d
        return authorization_request_public_dto

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
