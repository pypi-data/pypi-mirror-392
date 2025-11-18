import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonnelDataPublicDto")


@_attrs_define
class PersonnelDataPublicDto:
    """
    Attributes:
        id (str): The personnel identifier Example: 233.
        first_name (str): The personnel first name Example: Neil.
        last_name (str): The personnel last name Example: Armstrong.
        email (str): The personnel email Example: david@mail.com.
        contractor (bool): Indicates if the personnel is contractor
        is_mfa_enabled (bool): Indicates if the personnel has mfa enabled, true for enabled, false for disabled Example:
            True.
        date (datetime.datetime): The employment start date for the personnel. Format is ISO 8601 (YYYY-MM-DDTHH:mm:ss),
            American (MM/DD/YYYY), or RFC 3339 (YYYY-MM-DDTHH:mm:ssZ) Example: 2024-10-18T01:28:40.
        avatar_url (Union[Unset, str]): The personnel avatar picture Example: https://i.pravatar.cc/150?img=60.
        job_title (Union[Unset, str]): The personnel job title Example: painter.
        customer_id (Union[Unset, str]): The customer id Example: A232-23983.
    """

    id: str
    first_name: str
    last_name: str
    email: str
    contractor: bool
    is_mfa_enabled: bool
    date: datetime.datetime
    avatar_url: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    customer_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        contractor = self.contractor

        is_mfa_enabled = self.is_mfa_enabled

        date = self.date.isoformat()

        avatar_url = self.avatar_url

        job_title = self.job_title

        customer_id = self.customer_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "contractor": contractor,
                "isMfaEnabled": is_mfa_enabled,
                "date": date,
            }
        )
        if avatar_url is not UNSET:
            field_dict["avatarUrl"] = avatar_url
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if customer_id is not UNSET:
            field_dict["customerId"] = customer_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        first_name = d.pop("firstName")

        last_name = d.pop("lastName")

        email = d.pop("email")

        contractor = d.pop("contractor")

        is_mfa_enabled = d.pop("isMfaEnabled")

        date = isoparse(d.pop("date"))

        avatar_url = d.pop("avatarUrl", UNSET)

        job_title = d.pop("jobTitle", UNSET)

        customer_id = d.pop("customerId", UNSET)

        personnel_data_public_dto = cls(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            contractor=contractor,
            is_mfa_enabled=is_mfa_enabled,
            date=date,
            avatar_url=avatar_url,
            job_title=job_title,
            customer_id=customer_id,
        )

        personnel_data_public_dto.additional_properties = d
        return personnel_data_public_dto

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
