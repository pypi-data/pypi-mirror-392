from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.trust_center_preapproved_email_domain_response_public_dto import (
        TrustCenterPreapprovedEmailDomainResponsePublicDto,
    )


T = TypeVar("T", bound="TrustCenterPrivateAccessResponsePublicDto")


@_attrs_define
class TrustCenterPrivateAccessResponsePublicDto:
    """
    Attributes:
        flow_type (str): Private flow type Example: SELF.
        preapproved_email_domains (list['TrustCenterPreapprovedEmailDomainResponsePublicDto']): List of preapproved
            email domains Example: [{'id': 1, 'name': 'drata.com', 'createdAt': '2020-07-06', 'deletedAt': None}].
    """

    flow_type: str
    preapproved_email_domains: list["TrustCenterPreapprovedEmailDomainResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        flow_type = self.flow_type

        preapproved_email_domains = []
        for preapproved_email_domains_item_data in self.preapproved_email_domains:
            preapproved_email_domains_item = preapproved_email_domains_item_data.to_dict()
            preapproved_email_domains.append(preapproved_email_domains_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "flowType": flow_type,
                "preapprovedEmailDomains": preapproved_email_domains,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trust_center_preapproved_email_domain_response_public_dto import (
            TrustCenterPreapprovedEmailDomainResponsePublicDto,
        )

        d = dict(src_dict)
        flow_type = d.pop("flowType")

        preapproved_email_domains = []
        _preapproved_email_domains = d.pop("preapprovedEmailDomains")
        for preapproved_email_domains_item_data in _preapproved_email_domains:
            preapproved_email_domains_item = TrustCenterPreapprovedEmailDomainResponsePublicDto.from_dict(
                preapproved_email_domains_item_data
            )

            preapproved_email_domains.append(preapproved_email_domains_item)

        trust_center_private_access_response_public_dto = cls(
            flow_type=flow_type,
            preapproved_email_domains=preapproved_email_domains,
        )

        trust_center_private_access_response_public_dto.additional_properties = d
        return trust_center_private_access_response_public_dto

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
