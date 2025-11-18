from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SecurityReportResponsePublicDto")


@_attrs_define
class SecurityReportResponsePublicDto:
    """
    Attributes:
        visibility (str): The type of tests to return in the security report based on the result status Example:
            PASSING.
        sharing (bool): Indicates if the security report can be shared publicly Example: True.
        share_token (str): The token used to share the security report Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
    """

    visibility: str
    sharing: bool
    share_token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        visibility = self.visibility

        sharing = self.sharing

        share_token = self.share_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "visibility": visibility,
                "sharing": sharing,
                "shareToken": share_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        visibility = d.pop("visibility")

        sharing = d.pop("sharing")

        share_token = d.pop("shareToken")

        security_report_response_public_dto = cls(
            visibility=visibility,
            sharing=sharing,
            share_token=share_token,
        )

        security_report_response_public_dto.additional_properties = d
        return security_report_response_public_dto

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
