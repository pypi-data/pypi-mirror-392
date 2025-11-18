import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="BackgroundCheckResponsePublicDto")


@_attrs_define
class BackgroundCheckResponsePublicDto:
    """
    Attributes:
        id (float): The Background Check Id Example: 1.
        user_id (float): The user ID Example: 1.
        status (str): The status of the KarmaCheck case Example: OK.
        case_id (str): The case ID of the KarmaCheck background check Example: abc123.
        case_invitation_id (str): The case invitation ID of the KarmaCheck background check Example: abc123.
        url (str): The URL of the background check Example: https://app-stage.karmacheck.com/background_check/aaaaaaaa-
            bbbb-0000-cccc-dddddddddddd.
        manual_check_date (str): The date this background check was manually uploaded Example: 2020-07-06.
        manually_check_url (str): The url of manual background check Example: url.com.
        type_ (str): The background check type Example: CERTN.
        source (str): The background check source Example: DRATA.
        report_data (str): The background check report data
        user (UserResponsePublicDto):
        out_of_scope_reason (str): the reason it was marked out of scope Example: abc123.
        out_of_scope_at (datetime.datetime): when it was marked out of scope date timestamp Example:
            2025-07-01T16:45:55.246Z.
        invitation_email (str): Invitation email Example: email@email.com.
        linked_at (datetime.datetime): Report linked to a user date timestamp Example: 2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): Report created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Report updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    user_id: float
    status: str
    case_id: str
    case_invitation_id: str
    url: str
    manual_check_date: str
    manually_check_url: str
    type_: str
    source: str
    report_data: str
    user: "UserResponsePublicDto"
    out_of_scope_reason: str
    out_of_scope_at: datetime.datetime
    invitation_email: str
    linked_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        status = self.status

        case_id = self.case_id

        case_invitation_id = self.case_invitation_id

        url = self.url

        manual_check_date = self.manual_check_date

        manually_check_url = self.manually_check_url

        type_ = self.type_

        source = self.source

        report_data = self.report_data

        user = self.user.to_dict()

        out_of_scope_reason = self.out_of_scope_reason

        out_of_scope_at = self.out_of_scope_at.isoformat()

        invitation_email = self.invitation_email

        linked_at = self.linked_at.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "userId": user_id,
                "status": status,
                "caseId": case_id,
                "caseInvitationId": case_invitation_id,
                "url": url,
                "manualCheckDate": manual_check_date,
                "manuallyCheckUrl": manually_check_url,
                "type": type_,
                "source": source,
                "reportData": report_data,
                "user": user,
                "outOfScopeReason": out_of_scope_reason,
                "outOfScopeAt": out_of_scope_at,
                "invitationEmail": invitation_email,
                "linkedAt": linked_at,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        status = d.pop("status")

        case_id = d.pop("caseId")

        case_invitation_id = d.pop("caseInvitationId")

        url = d.pop("url")

        manual_check_date = d.pop("manualCheckDate")

        manually_check_url = d.pop("manuallyCheckUrl")

        type_ = d.pop("type")

        source = d.pop("source")

        report_data = d.pop("reportData")

        user = UserResponsePublicDto.from_dict(d.pop("user"))

        out_of_scope_reason = d.pop("outOfScopeReason")

        out_of_scope_at = isoparse(d.pop("outOfScopeAt"))

        invitation_email = d.pop("invitationEmail")

        linked_at = isoparse(d.pop("linkedAt"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        background_check_response_public_dto = cls(
            id=id,
            user_id=user_id,
            status=status,
            case_id=case_id,
            case_invitation_id=case_invitation_id,
            url=url,
            manual_check_date=manual_check_date,
            manually_check_url=manually_check_url,
            type_=type_,
            source=source,
            report_data=report_data,
            user=user,
            out_of_scope_reason=out_of_scope_reason,
            out_of_scope_at=out_of_scope_at,
            invitation_email=invitation_email,
            linked_at=linked_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        background_check_response_public_dto.additional_properties = d
        return background_check_response_public_dto

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
