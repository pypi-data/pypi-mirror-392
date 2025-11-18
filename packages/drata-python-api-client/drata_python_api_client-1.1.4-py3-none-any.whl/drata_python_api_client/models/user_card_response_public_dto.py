import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserCardResponsePublicDto")


@_attrs_define
class UserCardResponsePublicDto:
    """
    Attributes:
        id (float): User ID Example: 1.
        email (str): User email Example: email@email.com.
        created_at (datetime.datetime): User created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): User updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        first_name (Union[None, Unset, str]): User first name Example: Sally.
        last_name (Union[None, Unset, str]): User last name Example: Smith.
        job_title (Union[None, Unset, str]): User job title Example: CEO.
        avatar_url (Union[None, Unset, str]): User avatar URL Example: https://cdn-prod.imgpilot.com/avatar.png.
        drata_terms_agreed_at (Union[None, Unset, datetime.datetime]): User agreed to the Drata terms date timestamp
            Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    email: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    job_title: Union[None, Unset, str] = UNSET
    avatar_url: Union[None, Unset, str] = UNSET
    drata_terms_agreed_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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

        job_title: Union[None, Unset, str]
        if isinstance(self.job_title, Unset):
            job_title = UNSET
        else:
            job_title = self.job_title

        avatar_url: Union[None, Unset, str]
        if isinstance(self.avatar_url, Unset):
            avatar_url = UNSET
        else:
            avatar_url = self.avatar_url

        drata_terms_agreed_at: Union[None, Unset, str]
        if isinstance(self.drata_terms_agreed_at, Unset):
            drata_terms_agreed_at = UNSET
        elif isinstance(self.drata_terms_agreed_at, datetime.datetime):
            drata_terms_agreed_at = self.drata_terms_agreed_at.isoformat()
        else:
            drata_terms_agreed_at = self.drata_terms_agreed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if avatar_url is not UNSET:
            field_dict["avatarUrl"] = avatar_url
        if drata_terms_agreed_at is not UNSET:
            field_dict["drataTermsAgreedAt"] = drata_terms_agreed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

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

        def _parse_job_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        job_title = _parse_job_title(d.pop("jobTitle", UNSET))

        def _parse_avatar_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        avatar_url = _parse_avatar_url(d.pop("avatarUrl", UNSET))

        def _parse_drata_terms_agreed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                drata_terms_agreed_at_type_0 = isoparse(data)

                return drata_terms_agreed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        drata_terms_agreed_at = _parse_drata_terms_agreed_at(d.pop("drataTermsAgreedAt", UNSET))

        user_card_response_public_dto = cls(
            id=id,
            email=email,
            created_at=created_at,
            updated_at=updated_at,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            avatar_url=avatar_url,
            drata_terms_agreed_at=drata_terms_agreed_at,
        )

        user_card_response_public_dto.additional_properties = d
        return user_card_response_public_dto

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
