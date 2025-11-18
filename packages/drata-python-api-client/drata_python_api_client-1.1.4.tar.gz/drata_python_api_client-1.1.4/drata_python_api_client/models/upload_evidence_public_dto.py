import datetime
from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.upload_evidence_public_dto_renewal_schedule_type import UploadEvidencePublicDtoRenewalScheduleType
from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="UploadEvidencePublicDto")


@_attrs_define
class UploadEvidencePublicDto:
    """
    Attributes:
        creation_date (datetime.datetime): Creation date Example: 2025-07-01T16:45:55.246Z.
        renewal_date (str): Report renewal date Example: 2020-07-06.
        renewal_schedule_type (UploadEvidencePublicDtoRenewalScheduleType): The renewal date schedule type of report
            Example: ONE_YEAR.
        file (Union[Unset, File]): Accepted file extensions: .pdf, .docx, .odt, .xlsx, .ods, .pptx, .odp, .gif, .jpeg,
            .jpg, .png Example: -F 'file=<<Your-Relative-File-Path>>'.
        url (Union[Unset, str]): The url to the evidence Example: https://url.com.
        filename (Union[Unset, str]): The name of the evidence Example: Screenshot ExternalEvidence.
        base_64_file (Union[Unset, str]): JSON string with external evidence in Base64 format. Example: {'base64String':
            'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABg', 'filename': 'excellent-filename'}.
        description (Union[Unset, str]): The description of the evidence Example: A screenshot of a computer screen.
    """

    creation_date: datetime.datetime
    renewal_date: str
    renewal_schedule_type: UploadEvidencePublicDtoRenewalScheduleType
    file: Union[Unset, File] = UNSET
    url: Union[Unset, str] = UNSET
    filename: Union[Unset, str] = UNSET
    base_64_file: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        creation_date = self.creation_date.isoformat()

        renewal_date = self.renewal_date

        renewal_schedule_type = self.renewal_schedule_type.value

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        url = self.url

        filename = self.filename

        base_64_file = self.base_64_file

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "creationDate": creation_date,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file
        if url is not UNSET:
            field_dict["url"] = url
        if filename is not UNSET:
            field_dict["filename"] = filename
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        creation_date = self.creation_date.isoformat().encode()

        renewal_date = (None, str(self.renewal_date).encode(), "text/plain")

        renewal_schedule_type = (None, str(self.renewal_schedule_type.value).encode(), "text/plain")

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        url = self.url if isinstance(self.url, Unset) else (None, str(self.url).encode(), "text/plain")

        filename = (
            self.filename if isinstance(self.filename, Unset) else (None, str(self.filename).encode(), "text/plain")
        )

        base_64_file = (
            self.base_64_file
            if isinstance(self.base_64_file, Unset)
            else (None, str(self.base_64_file).encode(), "text/plain")
        )

        description = (
            self.description
            if isinstance(self.description, Unset)
            else (None, str(self.description).encode(), "text/plain")
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "creationDate": creation_date,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file
        if url is not UNSET:
            field_dict["url"] = url
        if filename is not UNSET:
            field_dict["filename"] = filename
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        creation_date = isoparse(d.pop("creationDate"))

        renewal_date = d.pop("renewalDate")

        renewal_schedule_type = UploadEvidencePublicDtoRenewalScheduleType(d.pop("renewalScheduleType"))

        _file = d.pop("file", UNSET)
        file: Union[Unset, File]
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        url = d.pop("url", UNSET)

        filename = d.pop("filename", UNSET)

        base_64_file = d.pop("base64File", UNSET)

        description = d.pop("description", UNSET)

        upload_evidence_public_dto = cls(
            creation_date=creation_date,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            file=file,
            url=url,
            filename=filename,
            base_64_file=base_64_file,
            description=description,
        )

        upload_evidence_public_dto.additional_properties = d
        return upload_evidence_public_dto

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
