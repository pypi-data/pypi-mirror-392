import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.vendor_security_review_compact_response_public_dto_status import (
    VendorSecurityReviewCompactResponsePublicDtoStatus,
)
from ..models.vendor_security_review_compact_response_public_dto_type import (
    VendorSecurityReviewCompactResponsePublicDtoType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto
    from ..models.vendor_response_public_dto import VendorResponsePublicDto


T = TypeVar("T", bound="VendorSecurityReviewCompactResponsePublicDto")


@_attrs_define
class VendorSecurityReviewCompactResponsePublicDto:
    """
    Attributes:
        id (float): Vendor security review id Example: 1.
        requested_at (datetime.datetime): Requested date
        review_deadline_at (datetime.datetime): Review deadline date
        decision (Union[None, str]): The decision about the security review Example: APPROVED.
        note (Union[None, str]): Vendor security review note
        status (VendorSecurityReviewCompactResponsePublicDtoStatus): The status for the security review Example:
            NOT_YET_STARTED.
        type_ (VendorSecurityReviewCompactResponsePublicDtoType): The type for the security review Example: SECURITY.
        requester_user (Union['UserCardCompactResponsePublicDto', None]): The related vendor security review requester
            user
        user (Union[Unset, UserResponsePublicDto]):
        vendor (Union[Unset, VendorResponsePublicDto]):
    """

    id: float
    requested_at: datetime.datetime
    review_deadline_at: datetime.datetime
    decision: Union[None, str]
    note: Union[None, str]
    status: VendorSecurityReviewCompactResponsePublicDtoStatus
    type_: VendorSecurityReviewCompactResponsePublicDtoType
    requester_user: Union["UserCardCompactResponsePublicDto", None]
    user: Union[Unset, "UserResponsePublicDto"] = UNSET
    vendor: Union[Unset, "VendorResponsePublicDto"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto

        id = self.id

        requested_at = self.requested_at.isoformat()

        review_deadline_at = self.review_deadline_at.isoformat()

        decision: Union[None, str]
        decision = self.decision

        note: Union[None, str]
        note = self.note

        status = self.status.value

        type_ = self.type_.value

        requester_user: Union[None, dict[str, Any]]
        if isinstance(self.requester_user, UserCardCompactResponsePublicDto):
            requester_user = self.requester_user.to_dict()
        else:
            requester_user = self.requester_user

        user: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        vendor: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vendor, Unset):
            vendor = self.vendor.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "requestedAt": requested_at,
                "reviewDeadlineAt": review_deadline_at,
                "decision": decision,
                "note": note,
                "status": status,
                "type": type_,
                "requesterUser": requester_user,
            }
        )
        if user is not UNSET:
            field_dict["user"] = user
        if vendor is not UNSET:
            field_dict["vendor"] = vendor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto
        from ..models.vendor_response_public_dto import VendorResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        requested_at = isoparse(d.pop("requestedAt"))

        review_deadline_at = isoparse(d.pop("reviewDeadlineAt"))

        def _parse_decision(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        decision = _parse_decision(d.pop("decision"))

        def _parse_note(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        note = _parse_note(d.pop("note"))

        status = VendorSecurityReviewCompactResponsePublicDtoStatus(d.pop("status"))

        type_ = VendorSecurityReviewCompactResponsePublicDtoType(d.pop("type"))

        def _parse_requester_user(data: object) -> Union["UserCardCompactResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                requester_user_type_1 = UserCardCompactResponsePublicDto.from_dict(data)

                return requester_user_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserCardCompactResponsePublicDto", None], data)

        requester_user = _parse_requester_user(d.pop("requesterUser"))

        _user = d.pop("user", UNSET)
        user: Union[Unset, UserResponsePublicDto]
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = UserResponsePublicDto.from_dict(_user)

        _vendor = d.pop("vendor", UNSET)
        vendor: Union[Unset, VendorResponsePublicDto]
        if isinstance(_vendor, Unset):
            vendor = UNSET
        else:
            vendor = VendorResponsePublicDto.from_dict(_vendor)

        vendor_security_review_compact_response_public_dto = cls(
            id=id,
            requested_at=requested_at,
            review_deadline_at=review_deadline_at,
            decision=decision,
            note=note,
            status=status,
            type_=type_,
            requester_user=requester_user,
            user=user,
            vendor=vendor,
        )

        vendor_security_review_compact_response_public_dto.additional_properties = d
        return vendor_security_review_compact_response_public_dto

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
