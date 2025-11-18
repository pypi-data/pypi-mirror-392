from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vendor_document_request_public_dto_type import VendorDocumentRequestPublicDtoType
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="VendorDocumentRequestPublicDto")


@_attrs_define
class VendorDocumentRequestPublicDto:
    """
    Attributes:
        file (File): Accepted file extensions: .pdf, .docx, .odt, .xlsx, .ods, .pptx, .odp, .gif, .jpeg, .jpg, .png
        type_ (Union[Unset, VendorDocumentRequestPublicDtoType]): Vendor document type Example: COMPLIANCE_REPORT.
    """

    file: File
    type_: Union[Unset, VendorDocumentRequestPublicDtoType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        type_: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = (None, str(self.type_.value).encode(), "text/plain")

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "file": file,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, VendorDocumentRequestPublicDtoType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = VendorDocumentRequestPublicDtoType(_type_)

        vendor_document_request_public_dto = cls(
            file=file,
            type_=type_,
        )

        vendor_document_request_public_dto.additional_properties = d
        return vendor_document_request_public_dto

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
