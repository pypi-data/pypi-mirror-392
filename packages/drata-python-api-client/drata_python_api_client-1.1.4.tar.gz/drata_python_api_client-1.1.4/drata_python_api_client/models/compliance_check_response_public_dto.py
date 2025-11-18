import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.compliance_check_response_public_dto_check_frequency import ComplianceCheckResponsePublicDtoCheckFrequency
from ..models.compliance_check_response_public_dto_status import ComplianceCheckResponsePublicDtoStatus
from ..models.compliance_check_response_public_dto_type import ComplianceCheckResponsePublicDtoType

T = TypeVar("T", bound="ComplianceCheckResponsePublicDto")


@_attrs_define
class ComplianceCheckResponsePublicDto:
    """
    Attributes:
        id (float): Compliance check ID Example: 1.
        status (ComplianceCheckResponsePublicDtoStatus): Denotes actual compliance
        type_ (ComplianceCheckResponsePublicDtoType): The compliance type
        completion_date (Union[None, datetime.datetime]): Date the user completed the compliance activity. A null value
            indicates the user is not compliant, possibly because evidence was deleted or is past its renewal date. Example:
            2025-07-01T16:45:55.246Z.
        expires_at (Union[None, datetime.datetime]): When this compliance is due for a re-verification Example:
            2025-07-01T16:45:55.246Z.
        check_frequency (ComplianceCheckResponsePublicDtoCheckFrequency): How often should this check be run for
            compliance
        last_checked_at (Union[None, datetime.datetime]): Last time Drata checked for compliance Example:
            2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): Compliance check creation timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Compliance check updated timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    status: ComplianceCheckResponsePublicDtoStatus
    type_: ComplianceCheckResponsePublicDtoType
    completion_date: Union[None, datetime.datetime]
    expires_at: Union[None, datetime.datetime]
    check_frequency: ComplianceCheckResponsePublicDtoCheckFrequency
    last_checked_at: Union[None, datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status.value

        type_ = self.type_.value

        completion_date: Union[None, str]
        if isinstance(self.completion_date, datetime.datetime):
            completion_date = self.completion_date.isoformat()
        else:
            completion_date = self.completion_date

        expires_at: Union[None, str]
        if isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        check_frequency = self.check_frequency.value

        last_checked_at: Union[None, str]
        if isinstance(self.last_checked_at, datetime.datetime):
            last_checked_at = self.last_checked_at.isoformat()
        else:
            last_checked_at = self.last_checked_at

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "type": type_,
                "completionDate": completion_date,
                "expiresAt": expires_at,
                "checkFrequency": check_frequency,
                "lastCheckedAt": last_checked_at,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        status = ComplianceCheckResponsePublicDtoStatus(d.pop("status"))

        type_ = ComplianceCheckResponsePublicDtoType(d.pop("type"))

        def _parse_completion_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completion_date_type_0 = isoparse(data)

                return completion_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        completion_date = _parse_completion_date(d.pop("completionDate"))

        def _parse_expires_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expiresAt"))

        check_frequency = ComplianceCheckResponsePublicDtoCheckFrequency(d.pop("checkFrequency"))

        def _parse_last_checked_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_checked_at_type_0 = isoparse(data)

                return last_checked_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_checked_at = _parse_last_checked_at(d.pop("lastCheckedAt"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        compliance_check_response_public_dto = cls(
            id=id,
            status=status,
            type_=type_,
            completion_date=completion_date,
            expires_at=expires_at,
            check_frequency=check_frequency,
            last_checked_at=last_checked_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        compliance_check_response_public_dto.additional_properties = d
        return compliance_check_response_public_dto

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
