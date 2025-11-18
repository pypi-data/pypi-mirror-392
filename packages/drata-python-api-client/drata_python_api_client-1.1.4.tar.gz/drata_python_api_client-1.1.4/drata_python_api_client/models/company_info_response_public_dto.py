import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.company_info_response_public_dto_favicon import CompanyInfoResponsePublicDtoFavicon
    from ..models.company_info_response_public_dto_nda import CompanyInfoResponsePublicDtoNda


T = TypeVar("T", bound="CompanyInfoResponsePublicDto")


@_attrs_define
class CompanyInfoResponsePublicDto:
    """
    Attributes:
        name (str): Company's common name Example: Drata.
        security_emails (str): Company's security/compliance email Example: security@drata.com.
        about (str): About the company Example: We are a startup ....
        privacy_description (str): Company's privacy description Example: Drata Inc is a company ....
        header_template (str): Header template in HTML format Example: <header>Drata</header>.
        favicon (CompanyInfoResponsePublicDtoFavicon): Favicon URL for Trust Page Example: {'name': 'Favicon', 'file':
            'https://drata.com/favicon.ico'}.
        nda (CompanyInfoResponsePublicDtoNda): NDA for Trust Page Example: {'name': 'NDA', 'file':
            'https://drata.com/nda.pdf'}.
        about_updated_at (datetime.datetime): About updated at timestamp Example: 2025-07-01T16:45:55.246Z.
        privacy_updated_at (datetime.datetime): Privacy updated at timestamp Example: 2025-07-01T16:45:55.246Z.
        privacy_url (Union[Unset, str]): Company's privacy url Example: https://drata.com/privacy.
        footer_template (Union[Unset, str]): Footer template in HTML format Example: <footer>Drata</footer>.
        contact_url (Union[Unset, str]): Company's contact url Example: https://acme.drata.net/contactus.
    """

    name: str
    security_emails: str
    about: str
    privacy_description: str
    header_template: str
    favicon: "CompanyInfoResponsePublicDtoFavicon"
    nda: "CompanyInfoResponsePublicDtoNda"
    about_updated_at: datetime.datetime
    privacy_updated_at: datetime.datetime
    privacy_url: Union[Unset, str] = UNSET
    footer_template: Union[Unset, str] = UNSET
    contact_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        security_emails = self.security_emails

        about = self.about

        privacy_description = self.privacy_description

        header_template = self.header_template

        favicon = self.favicon.to_dict()

        nda = self.nda.to_dict()

        about_updated_at = self.about_updated_at.isoformat()

        privacy_updated_at = self.privacy_updated_at.isoformat()

        privacy_url = self.privacy_url

        footer_template = self.footer_template

        contact_url = self.contact_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "securityEmails": security_emails,
                "about": about,
                "privacyDescription": privacy_description,
                "headerTemplate": header_template,
                "favicon": favicon,
                "nda": nda,
                "aboutUpdatedAt": about_updated_at,
                "privacyUpdatedAt": privacy_updated_at,
            }
        )
        if privacy_url is not UNSET:
            field_dict["privacyUrl"] = privacy_url
        if footer_template is not UNSET:
            field_dict["footerTemplate"] = footer_template
        if contact_url is not UNSET:
            field_dict["contactUrl"] = contact_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.company_info_response_public_dto_favicon import CompanyInfoResponsePublicDtoFavicon
        from ..models.company_info_response_public_dto_nda import CompanyInfoResponsePublicDtoNda

        d = dict(src_dict)
        name = d.pop("name")

        security_emails = d.pop("securityEmails")

        about = d.pop("about")

        privacy_description = d.pop("privacyDescription")

        header_template = d.pop("headerTemplate")

        favicon = CompanyInfoResponsePublicDtoFavicon.from_dict(d.pop("favicon"))

        nda = CompanyInfoResponsePublicDtoNda.from_dict(d.pop("nda"))

        about_updated_at = isoparse(d.pop("aboutUpdatedAt"))

        privacy_updated_at = isoparse(d.pop("privacyUpdatedAt"))

        privacy_url = d.pop("privacyUrl", UNSET)

        footer_template = d.pop("footerTemplate", UNSET)

        contact_url = d.pop("contactUrl", UNSET)

        company_info_response_public_dto = cls(
            name=name,
            security_emails=security_emails,
            about=about,
            privacy_description=privacy_description,
            header_template=header_template,
            favicon=favicon,
            nda=nda,
            about_updated_at=about_updated_at,
            privacy_updated_at=privacy_updated_at,
            privacy_url=privacy_url,
            footer_template=footer_template,
            contact_url=contact_url,
        )

        company_info_response_public_dto.additional_properties = d
        return company_info_response_public_dto

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
