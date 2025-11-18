import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.connection_response_public_dto import ConnectionResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="UserIdentityVersionControlResponsePublicDto")


@_attrs_define
class UserIdentityVersionControlResponsePublicDto:
    """
    Attributes:
        id (float): User identity ID Example: 1.
        identity_id (str): External service unique id Example: 1a2b3c.
        username (str): External service username Example: Username.
        email (str): External service email Example: email@email.com.
        connected_at (datetime.datetime): When this external user was linked to an application user Example:
            2025-07-01T16:45:55.246Z.
        disconnected_at (datetime.datetime): When this external user was unlinked to an application user Example:
            2025-07-01T16:45:55.246Z.
        service_account (datetime.datetime): When this external user was marked a service account Example:
            2025-07-01T16:45:55.246Z.
        service_account_reason (str): Description of why this was marked as a service account Example: This user is used
            to deploy code.
        user (UserResponsePublicDto):
        service_account_designator (UserResponsePublicDto):
        has_mfa (bool): Indicates the external user MFA status Example: True.
        connection (ConnectionResponsePublicDto):
        last_checked_at (datetime.datetime): The last time the user identity was last checked by the syncing service
            Example: 2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        write_access (datetime.datetime): Indicates external user write access ability Example:
            2025-07-01T16:45:55.246Z.
        push_production_code_access (datetime.datetime): Indicates external user production code access ability Example:
            2025-07-01T16:45:55.246Z.
    """

    id: float
    identity_id: str
    username: str
    email: str
    connected_at: datetime.datetime
    disconnected_at: datetime.datetime
    service_account: datetime.datetime
    service_account_reason: str
    user: "UserResponsePublicDto"
    service_account_designator: "UserResponsePublicDto"
    has_mfa: bool
    connection: "ConnectionResponsePublicDto"
    last_checked_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    write_access: datetime.datetime
    push_production_code_access: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        identity_id = self.identity_id

        username = self.username

        email = self.email

        connected_at = self.connected_at.isoformat()

        disconnected_at = self.disconnected_at.isoformat()

        service_account = self.service_account.isoformat()

        service_account_reason = self.service_account_reason

        user = self.user.to_dict()

        service_account_designator = self.service_account_designator.to_dict()

        has_mfa = self.has_mfa

        connection = self.connection.to_dict()

        last_checked_at = self.last_checked_at.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        write_access = self.write_access.isoformat()

        push_production_code_access = self.push_production_code_access.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "identityId": identity_id,
                "username": username,
                "email": email,
                "connectedAt": connected_at,
                "disconnectedAt": disconnected_at,
                "serviceAccount": service_account,
                "serviceAccountReason": service_account_reason,
                "user": user,
                "serviceAccountDesignator": service_account_designator,
                "hasMfa": has_mfa,
                "connection": connection,
                "lastCheckedAt": last_checked_at,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "writeAccess": write_access,
                "pushProductionCodeAccess": push_production_code_access,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_response_public_dto import ConnectionResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        identity_id = d.pop("identityId")

        username = d.pop("username")

        email = d.pop("email")

        connected_at = isoparse(d.pop("connectedAt"))

        disconnected_at = isoparse(d.pop("disconnectedAt"))

        service_account = isoparse(d.pop("serviceAccount"))

        service_account_reason = d.pop("serviceAccountReason")

        user = UserResponsePublicDto.from_dict(d.pop("user"))

        service_account_designator = UserResponsePublicDto.from_dict(d.pop("serviceAccountDesignator"))

        has_mfa = d.pop("hasMfa")

        connection = ConnectionResponsePublicDto.from_dict(d.pop("connection"))

        last_checked_at = isoparse(d.pop("lastCheckedAt"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        write_access = isoparse(d.pop("writeAccess"))

        push_production_code_access = isoparse(d.pop("pushProductionCodeAccess"))

        user_identity_version_control_response_public_dto = cls(
            id=id,
            identity_id=identity_id,
            username=username,
            email=email,
            connected_at=connected_at,
            disconnected_at=disconnected_at,
            service_account=service_account,
            service_account_reason=service_account_reason,
            user=user,
            service_account_designator=service_account_designator,
            has_mfa=has_mfa,
            connection=connection,
            last_checked_at=last_checked_at,
            created_at=created_at,
            updated_at=updated_at,
            write_access=write_access,
            push_production_code_access=push_production_code_access,
        )

        user_identity_version_control_response_public_dto.additional_properties = d
        return user_identity_version_control_response_public_dto

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
