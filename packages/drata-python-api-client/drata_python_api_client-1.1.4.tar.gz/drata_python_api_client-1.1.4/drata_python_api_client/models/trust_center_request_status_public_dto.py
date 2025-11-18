import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.trust_center_request_status_public_dto_source import TrustCenterRequestStatusPublicDtoSource
from ..models.trust_center_request_status_public_dto_status import TrustCenterRequestStatusPublicDtoStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="TrustCenterRequestStatusPublicDto")


@_attrs_define
class TrustCenterRequestStatusPublicDto:
    """
    Attributes:
        status (TrustCenterRequestStatusPublicDtoStatus): Status Example: APPROVED.
        source (TrustCenterRequestStatusPublicDtoSource): Status creation source Example: SELF.
        created_at (datetime.datetime): Date of status creation Example: 2025-07-01T16:45:55.246Z.
        user (Union[Unset, str]): Status creation user name Example: John Doe.
    """

    status: TrustCenterRequestStatusPublicDtoStatus
    source: TrustCenterRequestStatusPublicDtoSource
    created_at: datetime.datetime
    user: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        source = self.source.value

        created_at = self.created_at.isoformat()

        user = self.user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "source": source,
                "createdAt": created_at,
            }
        )
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = TrustCenterRequestStatusPublicDtoStatus(d.pop("status"))

        source = TrustCenterRequestStatusPublicDtoSource(d.pop("source"))

        created_at = isoparse(d.pop("createdAt"))

        user = d.pop("user", UNSET)

        trust_center_request_status_public_dto = cls(
            status=status,
            source=source,
            created_at=created_at,
            user=user,
        )

        trust_center_request_status_public_dto.additional_properties = d
        return trust_center_request_status_public_dto

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
