from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserIdentityInfrastructureServiceStatusRequestPublicDto")


@_attrs_define
class UserIdentityInfrastructureServiceStatusRequestPublicDto:
    """
    Attributes:
        service_account (bool): Determines service account state Example: True.
        service_account_reason (str): Reason why this account is being marked as a service account Example: This account
            is used to deploy.
    """

    service_account: bool
    service_account_reason: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_account = self.service_account

        service_account_reason = self.service_account_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "serviceAccount": service_account,
                "serviceAccountReason": service_account_reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        service_account = d.pop("serviceAccount")

        service_account_reason = d.pop("serviceAccountReason")

        user_identity_infrastructure_service_status_request_public_dto = cls(
            service_account=service_account,
            service_account_reason=service_account_reason,
        )

        user_identity_infrastructure_service_status_request_public_dto.additional_properties = d
        return user_identity_infrastructure_service_status_request_public_dto

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
