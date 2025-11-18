import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TrustCenterRequestResponsePublicDto")


@_attrs_define
class TrustCenterRequestResponsePublicDto:
    """
    Attributes:
        request_id (str): Request ID Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        created_at (datetime.datetime): Created at Example: 2025-07-01T16:45:55.246Z.
        expiration_date (Union[None, datetime.datetime]): End date Example: 2025-07-01T16:45:55.246Z.
        name (str): The requester name Example: Adam.
        lastname (str): The requester last name Example: Markowitz.
        email (str): The requester email Example: adam@drata.com.
        company (str): The requester company Example: Socpilot.
        flow_type (str): Private Flow Type Example: SELF.
        is_auto_approved (bool): Whether the request is auto approved or not
        status (Union[Unset, str]): Status of the request Example: APPROVED.
        reviewed_at (Union[Unset, datetime.datetime]): Reviewed at Example: 2025-07-01T16:45:55.246Z.
    """

    request_id: str
    created_at: datetime.datetime
    expiration_date: Union[None, datetime.datetime]
    name: str
    lastname: str
    email: str
    company: str
    flow_type: str
    is_auto_approved: bool
    status: Union[Unset, str] = UNSET
    reviewed_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        created_at = self.created_at.isoformat()

        expiration_date: Union[None, str]
        if isinstance(self.expiration_date, datetime.datetime):
            expiration_date = self.expiration_date.isoformat()
        else:
            expiration_date = self.expiration_date

        name = self.name

        lastname = self.lastname

        email = self.email

        company = self.company

        flow_type = self.flow_type

        is_auto_approved = self.is_auto_approved

        status = self.status

        reviewed_at: Union[Unset, str] = UNSET
        if not isinstance(self.reviewed_at, Unset):
            reviewed_at = self.reviewed_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "requestId": request_id,
                "createdAt": created_at,
                "expirationDate": expiration_date,
                "name": name,
                "lastname": lastname,
                "email": email,
                "company": company,
                "flowType": flow_type,
                "isAutoApproved": is_auto_approved,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if reviewed_at is not UNSET:
            field_dict["reviewedAt"] = reviewed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = d.pop("requestId")

        created_at = isoparse(d.pop("createdAt"))

        def _parse_expiration_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expiration_date_type_0 = isoparse(data)

                return expiration_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        expiration_date = _parse_expiration_date(d.pop("expirationDate"))

        name = d.pop("name")

        lastname = d.pop("lastname")

        email = d.pop("email")

        company = d.pop("company")

        flow_type = d.pop("flowType")

        is_auto_approved = d.pop("isAutoApproved")

        status = d.pop("status", UNSET)

        _reviewed_at = d.pop("reviewedAt", UNSET)
        reviewed_at: Union[Unset, datetime.datetime]
        if isinstance(_reviewed_at, Unset):
            reviewed_at = UNSET
        else:
            reviewed_at = isoparse(_reviewed_at)

        trust_center_request_response_public_dto = cls(
            request_id=request_id,
            created_at=created_at,
            expiration_date=expiration_date,
            name=name,
            lastname=lastname,
            email=email,
            company=company,
            flow_type=flow_type,
            is_auto_approved=is_auto_approved,
            status=status,
            reviewed_at=reviewed_at,
        )

        trust_center_request_response_public_dto.additional_properties = d
        return trust_center_request_response_public_dto

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
