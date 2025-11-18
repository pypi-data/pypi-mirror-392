from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ManualBackgroundCheckRequestPublicDto")


@_attrs_define
class ManualBackgroundCheckRequestPublicDto:
    """
    Attributes:
        url (str): The URL of the background check Example: https://app-stage.karmacheck.com/background_check/aaaaaaaa-
            bbbb-0000-cccc-dddddddddddd.
        filed_at (str): The date when this background check data was uploaded to Drata Example: 2020-07-06.
    """

    url: str
    filed_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        filed_at = self.filed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "filedAt": filed_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        filed_at = d.pop("filedAt")

        manual_background_check_request_public_dto = cls(
            url=url,
            filed_at=filed_at,
        )

        manual_background_check_request_public_dto.additional_properties = d
        return manual_background_check_request_public_dto

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
