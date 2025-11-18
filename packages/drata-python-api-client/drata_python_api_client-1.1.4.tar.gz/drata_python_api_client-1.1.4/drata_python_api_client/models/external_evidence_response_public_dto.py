from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExternalEvidenceResponsePublicDto")


@_attrs_define
class ExternalEvidenceResponsePublicDto:
    """
    Attributes:
        id (float): ExternalEvidence id Example: 123.
        name (str): ExternalEvidence name Example: Compelling ExternalEvidence.
        description (str): ExternalEvidence description Example: This is very good evidence.
        file (str): Path to file Example: /path/to/file.pdf.
        url (str): Url path Example: https://url.com.
        created_at (str): ExternalEvidence createdAt date Example: 2021-06-02.
        renewal_date (str): Report renewal date Example: 2020-07-06.
        renewal_schedule_type (str): The renewal date schedule type of report Example: ONE_YEAR.
        is_expired (bool): The report is expired; passed its renewal date
    """

    id: float
    name: str
    description: str
    file: str
    url: str
    created_at: str
    renewal_date: str
    renewal_schedule_type: str
    is_expired: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        file = self.file

        url = self.url

        created_at = self.created_at

        renewal_date = self.renewal_date

        renewal_schedule_type = self.renewal_schedule_type

        is_expired = self.is_expired

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "file": file,
                "url": url,
                "createdAt": created_at,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
                "isExpired": is_expired,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        file = d.pop("file")

        url = d.pop("url")

        created_at = d.pop("createdAt")

        renewal_date = d.pop("renewalDate")

        renewal_schedule_type = d.pop("renewalScheduleType")

        is_expired = d.pop("isExpired")

        external_evidence_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            file=file,
            url=url,
            created_at=created_at,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            is_expired=is_expired,
        )

        external_evidence_response_public_dto.additional_properties = d
        return external_evidence_response_public_dto

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
