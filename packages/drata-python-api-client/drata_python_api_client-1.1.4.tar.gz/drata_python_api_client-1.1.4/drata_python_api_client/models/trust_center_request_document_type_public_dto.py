from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trust_center_request_document_type_public_dto_type import TrustCenterRequestDocumentTypePublicDtoType

T = TypeVar("T", bound="TrustCenterRequestDocumentTypePublicDto")


@_attrs_define
class TrustCenterRequestDocumentTypePublicDto:
    """
    Attributes:
        document_id (float): The private document id Example: 1.
        type_ (TrustCenterRequestDocumentTypePublicDtoType): The private document type Example: SECURITY_REPORT.
    """

    document_id: float
    type_: TrustCenterRequestDocumentTypePublicDtoType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document_id = self.document_id

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "documentId": document_id,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_id = d.pop("documentId")

        type_ = TrustCenterRequestDocumentTypePublicDtoType(d.pop("type"))

        trust_center_request_document_type_public_dto = cls(
            document_id=document_id,
            type_=type_,
        )

        trust_center_request_document_type_public_dto.additional_properties = d
        return trust_center_request_document_type_public_dto

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
