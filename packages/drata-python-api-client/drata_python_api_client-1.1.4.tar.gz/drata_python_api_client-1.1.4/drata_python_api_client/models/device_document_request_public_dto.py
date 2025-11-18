from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_document_request_public_dto_type import DeviceDocumentRequestPublicDtoType
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="DeviceDocumentRequestPublicDto")


@_attrs_define
class DeviceDocumentRequestPublicDto:
    """
    Attributes:
        type_ (DeviceDocumentRequestPublicDtoType): The device document type Example: PASSWORD_MANAGER_EVIDENCE.
        file (File): Accepted file extensions: .pdf, .docx, .odt, .xlsx, .ods, .pptx, .odp, .gif, .jpeg, .jpg, .png
        base_64_file (Union[Unset, str]): JSON string with external evidence in Base64 format. Example: {'base64String':
            'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABg', 'filename': 'excellent-filename'}.
    """

    type_: DeviceDocumentRequestPublicDtoType
    file: File
    base_64_file: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        file = self.file.to_tuple()

        base_64_file = self.base_64_file

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "file": file,
            }
        )
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        type_ = (None, str(self.type_.value).encode(), "text/plain")

        file = self.file.to_tuple()

        base_64_file = (
            self.base_64_file
            if isinstance(self.base_64_file, Unset)
            else (None, str(self.base_64_file).encode(), "text/plain")
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "type": type_,
                "file": file,
            }
        )
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = DeviceDocumentRequestPublicDtoType(d.pop("type"))

        file = File(payload=BytesIO(d.pop("file")))

        base_64_file = d.pop("base64File", UNSET)

        device_document_request_public_dto = cls(
            type_=type_,
            file=file,
            base_64_file=base_64_file,
        )

        device_document_request_public_dto.additional_properties = d
        return device_document_request_public_dto

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
