from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.trust_center_all_private_documents_response_public_dto_private_documents_item import (
        TrustCenterAllPrivateDocumentsResponsePublicDtoPrivateDocumentsItem,
    )


T = TypeVar("T", bound="TrustCenterAllPrivateDocumentsResponsePublicDto")


@_attrs_define
class TrustCenterAllPrivateDocumentsResponsePublicDto:
    """
    Attributes:
        private_documents (list['TrustCenterAllPrivateDocumentsResponsePublicDtoPrivateDocumentsItem']): Policies,
            Compliance and Security Reports private documents
    """

    private_documents: list["TrustCenterAllPrivateDocumentsResponsePublicDtoPrivateDocumentsItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        private_documents = []
        for private_documents_item_data in self.private_documents:
            private_documents_item = private_documents_item_data.to_dict()
            private_documents.append(private_documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "privateDocuments": private_documents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trust_center_all_private_documents_response_public_dto_private_documents_item import (
            TrustCenterAllPrivateDocumentsResponsePublicDtoPrivateDocumentsItem,
        )

        d = dict(src_dict)
        private_documents = []
        _private_documents = d.pop("privateDocuments")
        for private_documents_item_data in _private_documents:
            private_documents_item = TrustCenterAllPrivateDocumentsResponsePublicDtoPrivateDocumentsItem.from_dict(
                private_documents_item_data
            )

            private_documents.append(private_documents_item)

        trust_center_all_private_documents_response_public_dto = cls(
            private_documents=private_documents,
        )

        trust_center_all_private_documents_response_public_dto.additional_properties = d
        return trust_center_all_private_documents_response_public_dto

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
