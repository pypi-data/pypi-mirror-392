import json
from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.evidence_request_public_dto_renewal_schedule_type import EvidenceRequestPublicDtoRenewalScheduleType
from ..models.evidence_request_public_dto_source import EvidenceRequestPublicDtoSource
from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="EvidenceRequestPublicDto")


@_attrs_define
class EvidenceRequestPublicDto:
    """
    Attributes:
        name (str): Document name Example: Security Training.
        renewal_date (str): Library document renewal date Example: 2020-07-06.
        renewal_schedule_type (EvidenceRequestPublicDtoRenewalScheduleType): Library Document renewal schedule type
            Example: ONE_YEAR.
        source (EvidenceRequestPublicDtoSource): The type of evidence Example: URL.
        filed_at (str): The date in which the evidence was originally filed/created Example: 2020-07-06.
        owner_id (float): Owner id Example: 1.
        description (Union[None, Unset, str]): Library document description Example: Security Training completed
            evidence.
        file (Union[Unset, File]): Accepted file extensions: .pdf, .docx, .odt, .xlsx, .ods, .pptx, .odp, .gif, .jpeg,
            .jpg, .png
        base_64_file (Union[Unset, str]): JSON string with external evidence in Base64 format. Example: {'base64String':
            'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABg', 'filename': 'excellent-filename'}.
        url (Union[None, Unset, str]): The url to the evidence Example: https://url.com.
        control_ids (Union[None, Unset, list[float]]): List of control IDs Example: [1, 2].
        ticket_url (Union[None, Unset, str]): Ticket provider url Example: https://acme.jira.com/browse/ISSUE-1234.
    """

    name: str
    renewal_date: str
    renewal_schedule_type: EvidenceRequestPublicDtoRenewalScheduleType
    source: EvidenceRequestPublicDtoSource
    filed_at: str
    owner_id: float
    description: Union[None, Unset, str] = UNSET
    file: Union[Unset, File] = UNSET
    base_64_file: Union[Unset, str] = UNSET
    url: Union[None, Unset, str] = UNSET
    control_ids: Union[None, Unset, list[float]] = UNSET
    ticket_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        renewal_date = self.renewal_date

        renewal_schedule_type = self.renewal_schedule_type.value

        source = self.source.value

        filed_at = self.filed_at

        owner_id = self.owner_id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        base_64_file = self.base_64_file

        url: Union[None, Unset, str]
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        control_ids: Union[None, Unset, list[float]]
        if isinstance(self.control_ids, Unset):
            control_ids = UNSET
        elif isinstance(self.control_ids, list):
            control_ids = self.control_ids

        else:
            control_ids = self.control_ids

        ticket_url: Union[None, Unset, str]
        if isinstance(self.ticket_url, Unset):
            ticket_url = UNSET
        else:
            ticket_url = self.ticket_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
                "source": source,
                "filedAt": filed_at,
                "ownerId": owner_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if file is not UNSET:
            field_dict["file"] = file
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file
        if url is not UNSET:
            field_dict["url"] = url
        if control_ids is not UNSET:
            field_dict["controlIds"] = control_ids
        if ticket_url is not UNSET:
            field_dict["ticketUrl"] = ticket_url

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        name = (None, str(self.name).encode(), "text/plain")

        renewal_date = (None, str(self.renewal_date).encode(), "text/plain")

        renewal_schedule_type = (None, str(self.renewal_schedule_type.value).encode(), "text/plain")

        source = (None, str(self.source.value).encode(), "text/plain")

        filed_at = (None, str(self.filed_at).encode(), "text/plain")

        owner_id = (None, str(self.owner_id).encode(), "text/plain")

        description: Union[Unset, tuple[None, bytes, str]]

        if isinstance(self.description, Unset):
            description = UNSET
        elif isinstance(self.description, str):
            description = (None, str(self.description).encode(), "text/plain")
        else:
            description = (None, str(self.description).encode(), "text/plain")

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        base_64_file = (
            self.base_64_file
            if isinstance(self.base_64_file, Unset)
            else (None, str(self.base_64_file).encode(), "text/plain")
        )

        url: Union[Unset, tuple[None, bytes, str]]

        if isinstance(self.url, Unset):
            url = UNSET
        elif isinstance(self.url, str):
            url = (None, str(self.url).encode(), "text/plain")
        else:
            url = (None, str(self.url).encode(), "text/plain")

        control_ids: Union[Unset, tuple[None, bytes, str]]

        if isinstance(self.control_ids, Unset):
            control_ids = UNSET
        elif isinstance(self.control_ids, list):
            _temp_control_ids = self.control_ids
            control_ids = (None, json.dumps(_temp_control_ids).encode(), "application/json")
        else:
            control_ids = (None, str(self.control_ids).encode(), "text/plain")

        ticket_url: Union[Unset, tuple[None, bytes, str]]

        if isinstance(self.ticket_url, Unset):
            ticket_url = UNSET
        elif isinstance(self.ticket_url, str):
            ticket_url = (None, str(self.ticket_url).encode(), "text/plain")
        else:
            ticket_url = (None, str(self.ticket_url).encode(), "text/plain")

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "name": name,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
                "source": source,
                "filedAt": filed_at,
                "ownerId": owner_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if file is not UNSET:
            field_dict["file"] = file
        if base_64_file is not UNSET:
            field_dict["base64File"] = base_64_file
        if url is not UNSET:
            field_dict["url"] = url
        if control_ids is not UNSET:
            field_dict["controlIds"] = control_ids
        if ticket_url is not UNSET:
            field_dict["ticketUrl"] = ticket_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        renewal_date = d.pop("renewalDate")

        renewal_schedule_type = EvidenceRequestPublicDtoRenewalScheduleType(d.pop("renewalScheduleType"))

        source = EvidenceRequestPublicDtoSource(d.pop("source"))

        filed_at = d.pop("filedAt")

        owner_id = d.pop("ownerId")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _file = d.pop("file", UNSET)
        file: Union[Unset, File]
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        base_64_file = d.pop("base64File", UNSET)

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_control_ids(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                control_ids_type_0 = cast(list[float], data)

                return control_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        control_ids = _parse_control_ids(d.pop("controlIds", UNSET))

        def _parse_ticket_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ticket_url = _parse_ticket_url(d.pop("ticketUrl", UNSET))

        evidence_request_public_dto = cls(
            name=name,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            source=source,
            filed_at=filed_at,
            owner_id=owner_id,
            description=description,
            file=file,
            base_64_file=base_64_file,
            url=url,
            control_ids=control_ids,
            ticket_url=ticket_url,
        )

        evidence_request_public_dto.additional_properties = d
        return evidence_request_public_dto

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
