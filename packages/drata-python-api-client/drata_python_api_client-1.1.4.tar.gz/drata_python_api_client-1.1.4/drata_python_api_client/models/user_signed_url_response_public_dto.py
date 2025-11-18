from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserSignedUrlResponsePublicDto")


@_attrs_define
class UserSignedUrlResponsePublicDto:
    """
    Attributes:
        signed_url (str): The short lived signed URL to link directly to the private file Example:
            https://somedomain.com/filename.pdf?Signature=ABC123.
    """

    signed_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signed_url = self.signed_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "signedUrl": signed_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        signed_url = d.pop("signedUrl")

        user_signed_url_response_public_dto = cls(
            signed_url=signed_url,
        )

        user_signed_url_response_public_dto.additional_properties = d
        return user_signed_url_response_public_dto

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
