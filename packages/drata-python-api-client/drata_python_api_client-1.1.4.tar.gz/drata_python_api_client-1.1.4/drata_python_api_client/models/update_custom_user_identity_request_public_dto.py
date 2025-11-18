import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateCustomUserIdentityRequestPublicDto")


@_attrs_define
class UpdateCustomUserIdentityRequestPublicDto:
    """
    Attributes:
        username (Union[None, Unset, str]): Username for custom user identity Example: John Doe.
        email (Union[None, Unset, str]): Email for custom user identity Example: johndoe@test.com.
        is_service_account (Union[None, Unset, bool]): Flag to indicate if custom user identity is a service account
        has_mfa (Union[None, Unset, bool]): Flag to indicate if custom user identity has multi-factor authentication
            enabled Example: True.
        user_id (Union[None, Unset, float]): ID from existing user that will be assigned to the custom user identity
            Example: 1.
        secondary_email (Union[None, Unset, str]): Secondary email for custom user identity Example: johndoe@test.com.
        first_name (Union[None, Unset, str]): First name for custom user identity Example: John.
        last_name (Union[None, Unset, str]): Last name for custom user identity Example: Doe.
        started_at (Union[None, Unset, datetime.datetime]): Start date from the user identity Example:
            2024-10-18T01:28:40.
        separated_at (Union[None, Unset, datetime.datetime]): Separation date from the user identity Example:
            2024-10-18T01:28:40.
        is_contractor (Union[None, Unset, bool]): If `true`, this user identity is identified as a contractor user
            Example: True.
        job_title (Union[None, Unset, str]): User identity job title Example: Engineer.
        manager_id (Union[None, Unset, str]): User identity manager's id Example: x00jk12-2312.
        manager_name (Union[None, Unset, str]): User identity manager's name
    """

    username: Union[None, Unset, str] = UNSET
    email: Union[None, Unset, str] = UNSET
    is_service_account: Union[None, Unset, bool] = UNSET
    has_mfa: Union[None, Unset, bool] = UNSET
    user_id: Union[None, Unset, float] = UNSET
    secondary_email: Union[None, Unset, str] = UNSET
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    started_at: Union[None, Unset, datetime.datetime] = UNSET
    separated_at: Union[None, Unset, datetime.datetime] = UNSET
    is_contractor: Union[None, Unset, bool] = UNSET
    job_title: Union[None, Unset, str] = UNSET
    manager_id: Union[None, Unset, str] = UNSET
    manager_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username: Union[None, Unset, str]
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        email: Union[None, Unset, str]
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        is_service_account: Union[None, Unset, bool]
        if isinstance(self.is_service_account, Unset):
            is_service_account = UNSET
        else:
            is_service_account = self.is_service_account

        has_mfa: Union[None, Unset, bool]
        if isinstance(self.has_mfa, Unset):
            has_mfa = UNSET
        else:
            has_mfa = self.has_mfa

        user_id: Union[None, Unset, float]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        secondary_email: Union[None, Unset, str]
        if isinstance(self.secondary_email, Unset):
            secondary_email = UNSET
        else:
            secondary_email = self.secondary_email

        first_name: Union[None, Unset, str]
        if isinstance(self.first_name, Unset):
            first_name = UNSET
        else:
            first_name = self.first_name

        last_name: Union[None, Unset, str]
        if isinstance(self.last_name, Unset):
            last_name = UNSET
        else:
            last_name = self.last_name

        started_at: Union[None, Unset, str]
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        separated_at: Union[None, Unset, str]
        if isinstance(self.separated_at, Unset):
            separated_at = UNSET
        elif isinstance(self.separated_at, datetime.datetime):
            separated_at = self.separated_at.isoformat()
        else:
            separated_at = self.separated_at

        is_contractor: Union[None, Unset, bool]
        if isinstance(self.is_contractor, Unset):
            is_contractor = UNSET
        else:
            is_contractor = self.is_contractor

        job_title: Union[None, Unset, str]
        if isinstance(self.job_title, Unset):
            job_title = UNSET
        else:
            job_title = self.job_title

        manager_id: Union[None, Unset, str]
        if isinstance(self.manager_id, Unset):
            manager_id = UNSET
        else:
            manager_id = self.manager_id

        manager_name: Union[None, Unset, str]
        if isinstance(self.manager_name, Unset):
            manager_name = UNSET
        else:
            manager_name = self.manager_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if email is not UNSET:
            field_dict["email"] = email
        if is_service_account is not UNSET:
            field_dict["isServiceAccount"] = is_service_account
        if has_mfa is not UNSET:
            field_dict["hasMfa"] = has_mfa
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if secondary_email is not UNSET:
            field_dict["secondaryEmail"] = secondary_email
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if separated_at is not UNSET:
            field_dict["separatedAt"] = separated_at
        if is_contractor is not UNSET:
            field_dict["isContractor"] = is_contractor
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if manager_id is not UNSET:
            field_dict["managerId"] = manager_id
        if manager_name is not UNSET:
            field_dict["managerName"] = manager_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email = _parse_email(d.pop("email", UNSET))

        def _parse_is_service_account(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_service_account = _parse_is_service_account(d.pop("isServiceAccount", UNSET))

        def _parse_has_mfa(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        has_mfa = _parse_has_mfa(d.pop("hasMfa", UNSET))

        def _parse_user_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        user_id = _parse_user_id(d.pop("userId", UNSET))

        def _parse_secondary_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        secondary_email = _parse_secondary_email(d.pop("secondaryEmail", UNSET))

        def _parse_first_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_name = _parse_first_name(d.pop("firstName", UNSET))

        def _parse_last_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_name = _parse_last_name(d.pop("lastName", UNSET))

        def _parse_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        started_at = _parse_started_at(d.pop("startedAt", UNSET))

        def _parse_separated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                separated_at_type_0 = isoparse(data)

                return separated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        separated_at = _parse_separated_at(d.pop("separatedAt", UNSET))

        def _parse_is_contractor(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_contractor = _parse_is_contractor(d.pop("isContractor", UNSET))

        def _parse_job_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        job_title = _parse_job_title(d.pop("jobTitle", UNSET))

        def _parse_manager_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        manager_id = _parse_manager_id(d.pop("managerId", UNSET))

        def _parse_manager_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        manager_name = _parse_manager_name(d.pop("managerName", UNSET))

        update_custom_user_identity_request_public_dto = cls(
            username=username,
            email=email,
            is_service_account=is_service_account,
            has_mfa=has_mfa,
            user_id=user_id,
            secondary_email=secondary_email,
            first_name=first_name,
            last_name=last_name,
            started_at=started_at,
            separated_at=separated_at,
            is_contractor=is_contractor,
            job_title=job_title,
            manager_id=manager_id,
            manager_name=manager_name,
        )

        update_custom_user_identity_request_public_dto.additional_properties = d
        return update_custom_user_identity_request_public_dto

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
