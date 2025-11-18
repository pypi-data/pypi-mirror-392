import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="UserCardCompactResponsePublicDto")


@_attrs_define
class UserCardCompactResponsePublicDto:
    """
    Attributes:
        id (float): User ID Example: 1.
        email (str): User email Example: email@email.com.
        first_name (Union[None, str]): User first name Example: Sally.
        last_name (Union[None, str]): User last name Example: Smith.
        created_at (datetime.datetime): User created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): User updated date timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    email: str
    first_name: Union[None, str]
    last_name: Union[None, str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        first_name: Union[None, str]
        first_name = self.first_name

        last_name: Union[None, str]
        last_name = self.last_name

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        def _parse_first_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        first_name = _parse_first_name(d.pop("firstName"))

        def _parse_last_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        last_name = _parse_last_name(d.pop("lastName"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        user_card_compact_response_public_dto = cls(
            id=id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            created_at=created_at,
            updated_at=updated_at,
        )

        user_card_compact_response_public_dto.additional_properties = d
        return user_card_compact_response_public_dto

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
