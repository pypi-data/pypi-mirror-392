import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="DeviceDocumentResponsePublicDto")


@_attrs_define
class DeviceDocumentResponsePublicDto:
    """
    Attributes:
        id (float): Device document ID Example: 1.
        type_ (str): The device document type Example: PASSWORD_MANAGER_EVIDENCE.
        name (str): The document name Example: Password Manager Evidence.
        file_url (Union[None, str]): The secure URL to the device document Example:
            http://localhost:5000/download/device-documents/1.
        created_at (datetime.datetime): Device document created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Device document updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    type_: str
    name: str
    file_url: Union[None, str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        name = self.name

        file_url: Union[None, str]
        file_url = self.file_url

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "name": name,
                "fileUrl": file_url,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        name = d.pop("name")

        def _parse_file_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        file_url = _parse_file_url(d.pop("fileUrl"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        device_document_response_public_dto = cls(
            id=id,
            type_=type_,
            name=name,
            file_url=file_url,
            created_at=created_at,
            updated_at=updated_at,
        )

        device_document_response_public_dto.additional_properties = d
        return device_document_response_public_dto

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
