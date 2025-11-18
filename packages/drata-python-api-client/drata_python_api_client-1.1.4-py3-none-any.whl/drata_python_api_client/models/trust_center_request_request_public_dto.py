from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trust_center_request_request_public_dto_flow_type import TrustCenterRequestRequestPublicDtoFlowType

if TYPE_CHECKING:
    from ..models.trust_center_request_document_type_public_dto import TrustCenterRequestDocumentTypePublicDto


T = TypeVar("T", bound="TrustCenterRequestRequestPublicDto")


@_attrs_define
class TrustCenterRequestRequestPublicDto:
    """
    Attributes:
        email (str): Email of requester Example: example@email.com.
        name (str): First name of requester Example: FirstName.
        lastname (str): Last name of requester Example: LastName.
        company (str): Company of requester Example: Company.
        accept_terms (bool): Accept the NDA terms and conditions Example: True.
        documents (list['TrustCenterRequestDocumentTypePublicDto']): Private documents to request access Example:
            [{'documentId': 1, 'type': 'POLICY'}, {'documentId': 2, 'type': 'SECURITY_REPORT'}].
        flow_type (TrustCenterRequestRequestPublicDtoFlowType): Type of private flow Example: SELF.
    """

    email: str
    name: str
    lastname: str
    company: str
    accept_terms: bool
    documents: list["TrustCenterRequestDocumentTypePublicDto"]
    flow_type: TrustCenterRequestRequestPublicDtoFlowType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        lastname = self.lastname

        company = self.company

        accept_terms = self.accept_terms

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        flow_type = self.flow_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "lastname": lastname,
                "company": company,
                "acceptTerms": accept_terms,
                "documents": documents,
                "flowType": flow_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trust_center_request_document_type_public_dto import TrustCenterRequestDocumentTypePublicDto

        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        lastname = d.pop("lastname")

        company = d.pop("company")

        accept_terms = d.pop("acceptTerms")

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = TrustCenterRequestDocumentTypePublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        flow_type = TrustCenterRequestRequestPublicDtoFlowType(d.pop("flowType"))

        trust_center_request_request_public_dto = cls(
            email=email,
            name=name,
            lastname=lastname,
            company=company,
            accept_terms=accept_terms,
            documents=documents,
            flow_type=flow_type,
        )

        trust_center_request_request_public_dto.additional_properties = d
        return trust_center_request_request_public_dto

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
