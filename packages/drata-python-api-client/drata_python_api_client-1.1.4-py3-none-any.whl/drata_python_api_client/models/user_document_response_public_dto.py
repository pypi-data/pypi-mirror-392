import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.user_document_response_public_dto_type import UserDocumentResponsePublicDtoType

T = TypeVar("T", bound="UserDocumentResponsePublicDto")


@_attrs_define
class UserDocumentResponsePublicDto:
    """
    Attributes:
        id (float): User document ID Example: 1.
        name (str): The name the file Example: Security Training.
        type_ (UserDocumentResponsePublicDtoType): The document type
        file_url (Union[None, str]): The secure URL to download the user document Example:
            http://localhost:5000/download/documents/1.
        renewal_date (datetime.date): Document's renewal date, after which the document is no longer consider valid
            evidence Example: 2026-10-27.
        created_at (datetime.datetime): User Document created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): User Document updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    name: str
    type_: UserDocumentResponsePublicDtoType
    file_url: Union[None, str]
    renewal_date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_.value

        file_url: Union[None, str]
        file_url = self.file_url

        renewal_date = self.renewal_date.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "fileUrl": file_url,
                "renewalDate": renewal_date,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = UserDocumentResponsePublicDtoType(d.pop("type"))

        def _parse_file_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        file_url = _parse_file_url(d.pop("fileUrl"))

        renewal_date = isoparse(d.pop("renewalDate")).date()

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        user_document_response_public_dto = cls(
            id=id,
            name=name,
            type_=type_,
            file_url=file_url,
            renewal_date=renewal_date,
            created_at=created_at,
            updated_at=updated_at,
        )

        user_document_response_public_dto.additional_properties = d
        return user_document_response_public_dto

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
