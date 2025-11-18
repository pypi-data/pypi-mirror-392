from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RiskUserResponsePublicDto")


@_attrs_define
class RiskUserResponsePublicDto:
    """
    Attributes:
        id (float): User ID Example: 1.
        email (str): User email Example: email@email.com.
        first_name (str): User first name Example: Sally.
        last_name (str): User last name Example: Smith.
        job_title (Union[None, str]): User job title Example: CEO.
        avatar_url (str): User avatar URL Example: https://cdn-prod.imgpilot.com/avatar.png.
    """

    id: float
    email: str
    first_name: str
    last_name: str
    job_title: Union[None, str]
    avatar_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        first_name = self.first_name

        last_name = self.last_name

        job_title: Union[None, str]
        job_title = self.job_title

        avatar_url = self.avatar_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "jobTitle": job_title,
                "avatarUrl": avatar_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        first_name = d.pop("firstName")

        last_name = d.pop("lastName")

        def _parse_job_title(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        job_title = _parse_job_title(d.pop("jobTitle"))

        avatar_url = d.pop("avatarUrl")

        risk_user_response_public_dto = cls(
            id=id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            avatar_url=avatar_url,
        )

        risk_user_response_public_dto.additional_properties = d
        return risk_user_response_public_dto

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
