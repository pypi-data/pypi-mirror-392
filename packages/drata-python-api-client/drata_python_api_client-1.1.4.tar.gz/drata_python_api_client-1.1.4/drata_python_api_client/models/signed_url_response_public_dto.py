from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.signed_url_response_public_dto_file_buffer_type_0 import SignedUrlResponsePublicDtoFileBufferType0


T = TypeVar("T", bound="SignedUrlResponsePublicDto")


@_attrs_define
class SignedUrlResponsePublicDto:
    """
    Attributes:
        signed_url (str): The short lived signed URL to link directly to the private file Example:
            https://somedomain.com/filename.pdf?Signature=ABC123.
        file_buffer (Union['SignedUrlResponsePublicDtoFileBufferType0', None]): The file on buffer format. This only
            applies for txt files. Example: {'buffer': 'RXhhbXBsZSB0ZXh0IGNvbnRlbnQ='}.
    """

    signed_url: str
    file_buffer: Union["SignedUrlResponsePublicDtoFileBufferType0", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.signed_url_response_public_dto_file_buffer_type_0 import SignedUrlResponsePublicDtoFileBufferType0

        signed_url = self.signed_url

        file_buffer: Union[None, dict[str, Any]]
        if isinstance(self.file_buffer, SignedUrlResponsePublicDtoFileBufferType0):
            file_buffer = self.file_buffer.to_dict()
        else:
            file_buffer = self.file_buffer

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "signedUrl": signed_url,
                "fileBuffer": file_buffer,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.signed_url_response_public_dto_file_buffer_type_0 import SignedUrlResponsePublicDtoFileBufferType0

        d = dict(src_dict)
        signed_url = d.pop("signedUrl")

        def _parse_file_buffer(data: object) -> Union["SignedUrlResponsePublicDtoFileBufferType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                file_buffer_type_0 = SignedUrlResponsePublicDtoFileBufferType0.from_dict(data)

                return file_buffer_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SignedUrlResponsePublicDtoFileBufferType0", None], data)

        file_buffer = _parse_file_buffer(d.pop("fileBuffer"))

        signed_url_response_public_dto = cls(
            signed_url=signed_url,
            file_buffer=file_buffer,
        )

        signed_url_response_public_dto.additional_properties = d
        return signed_url_response_public_dto

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
