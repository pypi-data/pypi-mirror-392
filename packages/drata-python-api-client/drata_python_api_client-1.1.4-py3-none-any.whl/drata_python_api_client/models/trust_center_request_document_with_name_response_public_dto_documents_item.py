import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.trust_center_request_document_with_name_response_public_dto_documents_item_type import (
    TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItemType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem")


@_attrs_define
class TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem:
    """
    Attributes:
        id (Union[Unset, float]):
        name (Union[Unset, str]):
        type_ (Union[Unset, TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItemType]):
        file (Union[Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
        version (Union[Unset, float]):
        is_public (Union[Unset, bool]):
    """

    id: Union[Unset, float] = UNSET
    name: Union[Unset, str] = UNSET
    type_: Union[Unset, TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItemType] = UNSET
    file: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    version: Union[Unset, float] = UNSET
    is_public: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        file = self.file

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        version = self.version

        is_public = self.is_public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if file is not UNSET:
            field_dict["file"] = file
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if version is not UNSET:
            field_dict["version"] = version
        if is_public is not UNSET:
            field_dict["isPublic"] = is_public

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItemType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItemType(_type_)

        file = d.pop("file", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        version = d.pop("version", UNSET)

        is_public = d.pop("isPublic", UNSET)

        trust_center_request_document_with_name_response_public_dto_documents_item = cls(
            id=id,
            name=name,
            type_=type_,
            file=file,
            created_at=created_at,
            version=version,
            is_public=is_public,
        )

        trust_center_request_document_with_name_response_public_dto_documents_item.additional_properties = d
        return trust_center_request_document_with_name_response_public_dto_documents_item

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
