import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connection_response_public_dto import ConnectionResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="UserIdentityResponsePublicDto")


@_attrs_define
class UserIdentityResponsePublicDto:
    """
    Attributes:
        id (float): User identity ID Example: 1.
        identity_id (str): External service unique id Example: 1a2b3c.
        username (str): External service username Example: Username.
        connected_at (datetime.datetime): When this external user was linked to an application user Example:
            2025-07-01T16:45:55.246Z.
        disconnected_at (datetime.datetime): When this external user was unlinked to an application user Example:
            2025-07-01T16:45:55.246Z.
        has_mfa (bool): Indicates the external user MFA status Example: True.
        user (UserResponsePublicDto):
        connection (ConnectionResponsePublicDto):
        has_idp (bool): Indicates if user is connected with Idp Example: True.
        secondary_email (str): Secondary email for custom user identity Example: johndoe@test.com.
        first_name (str): First name for custom user identity Example: John.
        last_name (str): Last name for custom user identity Example: Doe.
        started_at (datetime.datetime): Start date from the user identity Example: 2025-07-01T16:45:55.246Z.
        separated_at (datetime.datetime): Separation date from the user identity Example: 2025-07-01T16:45:55.246Z.
        job_title (str): User identity job title Example: Engineer.
        manager_id (str): User identity manager's id Example: x00jk12-2312.
        manager_name (str): User identity manager's name
        is_contractor (Union[Unset, bool]): If `true`, this user identity is identified as a contractor user Example:
            True.
    """

    id: float
    identity_id: str
    username: str
    connected_at: datetime.datetime
    disconnected_at: datetime.datetime
    has_mfa: bool
    user: "UserResponsePublicDto"
    connection: "ConnectionResponsePublicDto"
    has_idp: bool
    secondary_email: str
    first_name: str
    last_name: str
    started_at: datetime.datetime
    separated_at: datetime.datetime
    job_title: str
    manager_id: str
    manager_name: str
    is_contractor: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        identity_id = self.identity_id

        username = self.username

        connected_at = self.connected_at.isoformat()

        disconnected_at = self.disconnected_at.isoformat()

        has_mfa = self.has_mfa

        user = self.user.to_dict()

        connection = self.connection.to_dict()

        has_idp = self.has_idp

        secondary_email = self.secondary_email

        first_name = self.first_name

        last_name = self.last_name

        started_at = self.started_at.isoformat()

        separated_at = self.separated_at.isoformat()

        job_title = self.job_title

        manager_id = self.manager_id

        manager_name = self.manager_name

        is_contractor = self.is_contractor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "identityId": identity_id,
                "username": username,
                "connectedAt": connected_at,
                "disconnectedAt": disconnected_at,
                "hasMfa": has_mfa,
                "user": user,
                "connection": connection,
                "hasIdp": has_idp,
                "secondaryEmail": secondary_email,
                "firstName": first_name,
                "lastName": last_name,
                "startedAt": started_at,
                "separatedAt": separated_at,
                "jobTitle": job_title,
                "managerId": manager_id,
                "managerName": manager_name,
            }
        )
        if is_contractor is not UNSET:
            field_dict["isContractor"] = is_contractor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_response_public_dto import ConnectionResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        identity_id = d.pop("identityId")

        username = d.pop("username")

        connected_at = isoparse(d.pop("connectedAt"))

        disconnected_at = isoparse(d.pop("disconnectedAt"))

        has_mfa = d.pop("hasMfa")

        user = UserResponsePublicDto.from_dict(d.pop("user"))

        connection = ConnectionResponsePublicDto.from_dict(d.pop("connection"))

        has_idp = d.pop("hasIdp")

        secondary_email = d.pop("secondaryEmail")

        first_name = d.pop("firstName")

        last_name = d.pop("lastName")

        started_at = isoparse(d.pop("startedAt"))

        separated_at = isoparse(d.pop("separatedAt"))

        job_title = d.pop("jobTitle")

        manager_id = d.pop("managerId")

        manager_name = d.pop("managerName")

        is_contractor = d.pop("isContractor", UNSET)

        user_identity_response_public_dto = cls(
            id=id,
            identity_id=identity_id,
            username=username,
            connected_at=connected_at,
            disconnected_at=disconnected_at,
            has_mfa=has_mfa,
            user=user,
            connection=connection,
            has_idp=has_idp,
            secondary_email=secondary_email,
            first_name=first_name,
            last_name=last_name,
            started_at=started_at,
            separated_at=separated_at,
            job_title=job_title,
            manager_id=manager_id,
            manager_name=manager_name,
            is_contractor=is_contractor,
        )

        user_identity_response_public_dto.additional_properties = d
        return user_identity_response_public_dto

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
