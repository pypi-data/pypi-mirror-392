import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.vendor_security_review_request_public_dto_security_review_status import (
    VendorSecurityReviewRequestPublicDtoSecurityReviewStatus,
)
from ..models.vendor_security_review_request_public_dto_security_review_type import (
    VendorSecurityReviewRequestPublicDtoSecurityReviewType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="VendorSecurityReviewRequestPublicDto")


@_attrs_define
class VendorSecurityReviewRequestPublicDto:
    """
    Attributes:
        review_deadline_at (datetime.datetime): Vendor security review deadline date Example: 2025-07-01T16:45:55.246Z.
        security_review_status (VendorSecurityReviewRequestPublicDtoSecurityReviewStatus): The status for the security
            review Example: NOT_YET_STARTED.
        security_review_type (VendorSecurityReviewRequestPublicDtoSecurityReviewType): The type for the security review
            Example: SECURITY.
        title (Union[None, Unset, str]): Vendor security review title Example: Security review title.
        requested_at (Union[Unset, datetime.datetime]): Vendor security requested date Example:
            2025-07-01T16:45:55.246Z.
        requester_user_id (Union[Unset, float]): The user ID of the person that requested the security review Example:
            1.
    """

    review_deadline_at: datetime.datetime
    security_review_status: VendorSecurityReviewRequestPublicDtoSecurityReviewStatus
    security_review_type: VendorSecurityReviewRequestPublicDtoSecurityReviewType
    title: Union[None, Unset, str] = UNSET
    requested_at: Union[Unset, datetime.datetime] = UNSET
    requester_user_id: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        review_deadline_at = self.review_deadline_at.isoformat()

        security_review_status = self.security_review_status.value

        security_review_type = self.security_review_type.value

        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        requested_at: Union[Unset, str] = UNSET
        if not isinstance(self.requested_at, Unset):
            requested_at = self.requested_at.isoformat()

        requester_user_id = self.requester_user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reviewDeadlineAt": review_deadline_at,
                "securityReviewStatus": security_review_status,
                "securityReviewType": security_review_type,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if requested_at is not UNSET:
            field_dict["requestedAt"] = requested_at
        if requester_user_id is not UNSET:
            field_dict["requesterUserId"] = requester_user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        review_deadline_at = isoparse(d.pop("reviewDeadlineAt"))

        security_review_status = VendorSecurityReviewRequestPublicDtoSecurityReviewStatus(d.pop("securityReviewStatus"))

        security_review_type = VendorSecurityReviewRequestPublicDtoSecurityReviewType(d.pop("securityReviewType"))

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        _requested_at = d.pop("requestedAt", UNSET)
        requested_at: Union[Unset, datetime.datetime]
        if isinstance(_requested_at, Unset):
            requested_at = UNSET
        else:
            requested_at = isoparse(_requested_at)

        requester_user_id = d.pop("requesterUserId", UNSET)

        vendor_security_review_request_public_dto = cls(
            review_deadline_at=review_deadline_at,
            security_review_status=security_review_status,
            security_review_type=security_review_type,
            title=title,
            requested_at=requested_at,
            requester_user_id=requester_user_id,
        )

        vendor_security_review_request_public_dto.additional_properties = d
        return vendor_security_review_request_public_dto

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
