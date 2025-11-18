from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.trust_center_request_document_with_name_response_public_dto_documents_item import (
        TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem,
    )
    from ..models.trust_center_request_status_public_dto import TrustCenterRequestStatusPublicDto


T = TypeVar("T", bound="TrustCenterRequestDocumentWithNameResponsePublicDto")


@_attrs_define
class TrustCenterRequestDocumentWithNameResponsePublicDto:
    """
    Attributes:
        email (str): Requester Email Example: example@drata.com.
        first_name (str): Requester first name Example: Alondra.
        last_name (str): Requester last name Example: Ramos.
        company (str): Requester company Example: Acme.
        request_id (str): Request ID Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        managed_by (str): Admin account Example: Brayan Perez.
        documents (list['TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem']): Request documents Example:
            [{
                        id: 5,
                        name: Report 5,
                        approvedAt: 2025-07-01T16:45:55.246Z,
                        deniedAt: 2025-07-01T16:45:55.246Z
                    }].
        statuses (list['TrustCenterRequestStatusPublicDto']): Request statuses Example: [{
                        status: 'APPROVED',
                        source: 'SELF',
                        createdAt: 2025-07-01T16:45:55.246Z,
                        user: 'John Doe',
                    }].
        flow_type (str): Private flow type Example: SELF.
        auto_approve_type (Union[None, str]): Auto approved type Example: SELF.
        nda_url (Union[Unset, str]): DocuSign NDA URL Example: https://acme.com.
    """

    email: str
    first_name: str
    last_name: str
    company: str
    request_id: str
    managed_by: str
    documents: list["TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem"]
    statuses: list["TrustCenterRequestStatusPublicDto"]
    flow_type: str
    auto_approve_type: Union[None, str]
    nda_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        first_name = self.first_name

        last_name = self.last_name

        company = self.company

        request_id = self.request_id

        managed_by = self.managed_by

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        statuses = []
        for statuses_item_data in self.statuses:
            statuses_item = statuses_item_data.to_dict()
            statuses.append(statuses_item)

        flow_type = self.flow_type

        auto_approve_type: Union[None, str]
        auto_approve_type = self.auto_approve_type

        nda_url = self.nda_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "company": company,
                "requestId": request_id,
                "managedBy": managed_by,
                "documents": documents,
                "statuses": statuses,
                "flowType": flow_type,
                "autoApproveType": auto_approve_type,
            }
        )
        if nda_url is not UNSET:
            field_dict["ndaUrl"] = nda_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trust_center_request_document_with_name_response_public_dto_documents_item import (
            TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem,
        )
        from ..models.trust_center_request_status_public_dto import TrustCenterRequestStatusPublicDto

        d = dict(src_dict)
        email = d.pop("email")

        first_name = d.pop("firstName")

        last_name = d.pop("lastName")

        company = d.pop("company")

        request_id = d.pop("requestId")

        managed_by = d.pop("managedBy")

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = TrustCenterRequestDocumentWithNameResponsePublicDtoDocumentsItem.from_dict(
                documents_item_data
            )

            documents.append(documents_item)

        statuses = []
        _statuses = d.pop("statuses")
        for statuses_item_data in _statuses:
            statuses_item = TrustCenterRequestStatusPublicDto.from_dict(statuses_item_data)

            statuses.append(statuses_item)

        flow_type = d.pop("flowType")

        def _parse_auto_approve_type(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        auto_approve_type = _parse_auto_approve_type(d.pop("autoApproveType"))

        nda_url = d.pop("ndaUrl", UNSET)

        trust_center_request_document_with_name_response_public_dto = cls(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company,
            request_id=request_id,
            managed_by=managed_by,
            documents=documents,
            statuses=statuses,
            flow_type=flow_type,
            auto_approve_type=auto_approve_type,
            nda_url=nda_url,
        )

        trust_center_request_document_with_name_response_public_dto.additional_properties = d
        return trust_center_request_document_with_name_response_public_dto

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
