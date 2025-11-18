from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_document_response_public_dto import UserDocumentResponsePublicDto


T = TypeVar("T", bound="UserAllDocumentsResponsePublicDto")


@_attrs_define
class UserAllDocumentsResponsePublicDto:
    """
    Attributes:
        documents (list['UserDocumentResponsePublicDto']): Full list of user documents
    """

    documents: list["UserDocumentResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "documents": documents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_document_response_public_dto import UserDocumentResponsePublicDto

        d = dict(src_dict)
        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = UserDocumentResponsePublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        user_all_documents_response_public_dto = cls(
            documents=documents,
        )

        user_all_documents_response_public_dto.additional_properties = d
        return user_all_documents_response_public_dto

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
