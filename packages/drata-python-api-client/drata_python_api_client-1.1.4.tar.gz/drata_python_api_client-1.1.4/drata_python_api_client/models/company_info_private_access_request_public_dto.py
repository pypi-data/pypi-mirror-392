from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CompanyInfoPrivateAccessRequestPublicDto")


@_attrs_define
class CompanyInfoPrivateAccessRequestPublicDto:
    """
    Attributes:
        security_emails (Union[Unset, str]): Company's security/compliance email Example: security@drata.com.
        remove_nda (Union[Unset, bool]): Remove the current NDA? Example: True.
        preapproved_email_domains (Union[Unset, list[str]]): List of preapproved email domains Example: domain.com.
    """

    security_emails: Union[Unset, str] = UNSET
    remove_nda: Union[Unset, bool] = UNSET
    preapproved_email_domains: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        security_emails = self.security_emails

        remove_nda = self.remove_nda

        preapproved_email_domains: Union[Unset, list[str]] = UNSET
        if not isinstance(self.preapproved_email_domains, Unset):
            preapproved_email_domains = self.preapproved_email_domains

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if security_emails is not UNSET:
            field_dict["securityEmails"] = security_emails
        if remove_nda is not UNSET:
            field_dict["removeNda"] = remove_nda
        if preapproved_email_domains is not UNSET:
            field_dict["preapprovedEmailDomains"] = preapproved_email_domains

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        security_emails = d.pop("securityEmails", UNSET)

        remove_nda = d.pop("removeNda", UNSET)

        preapproved_email_domains = cast(list[str], d.pop("preapprovedEmailDomains", UNSET))

        company_info_private_access_request_public_dto = cls(
            security_emails=security_emails,
            remove_nda=remove_nda,
            preapproved_email_domains=preapproved_email_domains,
        )

        company_info_private_access_request_public_dto.additional_properties = d
        return company_info_private_access_request_public_dto

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
