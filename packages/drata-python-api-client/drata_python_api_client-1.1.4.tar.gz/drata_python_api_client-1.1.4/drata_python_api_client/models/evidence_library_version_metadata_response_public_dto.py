import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EvidenceLibraryVersionMetadataResponsePublicDto")


@_attrs_define
class EvidenceLibraryVersionMetadataResponsePublicDto:
    """
    Attributes:
        original_file_name (Union[Unset, str]): Evidence file name Example: evidence.pdf.
        extension (Union[Unset, str]): Evidence file type Example: pdf.
        file_created_at (Union[Unset, datetime.datetime]): Evidence file creation date Example: 2020-07-06.
    """

    original_file_name: Union[Unset, str] = UNSET
    extension: Union[Unset, str] = UNSET
    file_created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        original_file_name = self.original_file_name

        extension = self.extension

        file_created_at: Union[Unset, str] = UNSET
        if not isinstance(self.file_created_at, Unset):
            file_created_at = self.file_created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if original_file_name is not UNSET:
            field_dict["originalFileName"] = original_file_name
        if extension is not UNSET:
            field_dict["extension"] = extension
        if file_created_at is not UNSET:
            field_dict["fileCreatedAt"] = file_created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        original_file_name = d.pop("originalFileName", UNSET)

        extension = d.pop("extension", UNSET)

        _file_created_at = d.pop("fileCreatedAt", UNSET)
        file_created_at: Union[Unset, datetime.datetime]
        if isinstance(_file_created_at, Unset):
            file_created_at = UNSET
        else:
            file_created_at = isoparse(_file_created_at)

        evidence_library_version_metadata_response_public_dto = cls(
            original_file_name=original_file_name,
            extension=extension,
            file_created_at=file_created_at,
        )

        evidence_library_version_metadata_response_public_dto.additional_properties = d
        return evidence_library_version_metadata_response_public_dto

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
