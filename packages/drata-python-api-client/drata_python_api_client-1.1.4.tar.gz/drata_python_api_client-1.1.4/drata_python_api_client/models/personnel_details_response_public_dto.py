import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.personnel_details_response_public_dto_employment_status import (
    PersonnelDetailsResponsePublicDtoEmploymentStatus,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compliance_check_response_public_dto import ComplianceCheckResponsePublicDto
    from ..models.compliance_test_response_public_dto import ComplianceTestResponsePublicDto
    from ..models.device_response_public_dto import DeviceResponsePublicDto
    from ..models.personnel_data_response_public_dto import PersonnelDataResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="PersonnelDetailsResponsePublicDto")


@_attrs_define
class PersonnelDetailsResponsePublicDto:
    """
    Attributes:
        id (float): Personnel Id Example: 1.
        employment_status (PersonnelDetailsResponsePublicDtoEmploymentStatus): The employment status of the personnel
        os_version (Union[None, str]): The OS version this personnel uses Example: Windows 3.1.
        serial_number (Union[None, str]): The serial number of the machine this personnel uses Example: 1A2B3C4D.
        user (UserResponsePublicDto):
        compliance_checks (list['ComplianceCheckResponsePublicDto']): Company products Example: [].
        start_date (str): The date when this personnel was onboarded onto the company system Example: 2020-07-06.
        status_updated_at (Union[None, datetime.datetime]): The date when this personnel was manually updated
        data (PersonnelDataResponsePublicDto):
        created_at (datetime.datetime): Personnel created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Personnel updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        devices (list['DeviceResponsePublicDto']): A list of the devices registered to the personnel Example: [].
        not_human_reason (Union[None, Unset, str]): Explains why the employment status of this personnel is marked as
            OUT_OF_SCOPE Example: This is not a real personnel, but a placeholder for anyone in charge of X.
        reason_provider (Union['UserResponsePublicDto', None, Unset]): The user who provided the reason why this
            personnel was marked as OUT_OF_SCOPE
        compliance_tests (Union[Unset, list['ComplianceTestResponsePublicDto']]): Compliance Tests Example: [].
        separation_date (Union[None, Unset, str]): The date when this personnel was separated from the company system
            Example: 2020-07-06.
    """

    id: float
    employment_status: PersonnelDetailsResponsePublicDtoEmploymentStatus
    os_version: Union[None, str]
    serial_number: Union[None, str]
    user: "UserResponsePublicDto"
    compliance_checks: list["ComplianceCheckResponsePublicDto"]
    start_date: str
    status_updated_at: Union[None, datetime.datetime]
    data: "PersonnelDataResponsePublicDto"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    devices: list["DeviceResponsePublicDto"]
    not_human_reason: Union[None, Unset, str] = UNSET
    reason_provider: Union["UserResponsePublicDto", None, Unset] = UNSET
    compliance_tests: Union[Unset, list["ComplianceTestResponsePublicDto"]] = UNSET
    separation_date: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_response_public_dto import UserResponsePublicDto

        id = self.id

        employment_status = self.employment_status.value

        os_version: Union[None, str]
        os_version = self.os_version

        serial_number: Union[None, str]
        serial_number = self.serial_number

        user = self.user.to_dict()

        compliance_checks = []
        for compliance_checks_item_data in self.compliance_checks:
            compliance_checks_item = compliance_checks_item_data.to_dict()
            compliance_checks.append(compliance_checks_item)

        start_date = self.start_date

        status_updated_at: Union[None, str]
        if isinstance(self.status_updated_at, datetime.datetime):
            status_updated_at = self.status_updated_at.isoformat()
        else:
            status_updated_at = self.status_updated_at

        data = self.data.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        not_human_reason: Union[None, Unset, str]
        if isinstance(self.not_human_reason, Unset):
            not_human_reason = UNSET
        else:
            not_human_reason = self.not_human_reason

        reason_provider: Union[None, Unset, dict[str, Any]]
        if isinstance(self.reason_provider, Unset):
            reason_provider = UNSET
        elif isinstance(self.reason_provider, UserResponsePublicDto):
            reason_provider = self.reason_provider.to_dict()
        else:
            reason_provider = self.reason_provider

        compliance_tests: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.compliance_tests, Unset):
            compliance_tests = []
            for compliance_tests_item_data in self.compliance_tests:
                compliance_tests_item = compliance_tests_item_data.to_dict()
                compliance_tests.append(compliance_tests_item)

        separation_date: Union[None, Unset, str]
        if isinstance(self.separation_date, Unset):
            separation_date = UNSET
        else:
            separation_date = self.separation_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "employmentStatus": employment_status,
                "osVersion": os_version,
                "serialNumber": serial_number,
                "user": user,
                "complianceChecks": compliance_checks,
                "startDate": start_date,
                "statusUpdatedAt": status_updated_at,
                "data": data,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "devices": devices,
            }
        )
        if not_human_reason is not UNSET:
            field_dict["notHumanReason"] = not_human_reason
        if reason_provider is not UNSET:
            field_dict["reasonProvider"] = reason_provider
        if compliance_tests is not UNSET:
            field_dict["complianceTests"] = compliance_tests
        if separation_date is not UNSET:
            field_dict["separationDate"] = separation_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compliance_check_response_public_dto import ComplianceCheckResponsePublicDto
        from ..models.compliance_test_response_public_dto import ComplianceTestResponsePublicDto
        from ..models.device_response_public_dto import DeviceResponsePublicDto
        from ..models.personnel_data_response_public_dto import PersonnelDataResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        employment_status = PersonnelDetailsResponsePublicDtoEmploymentStatus(d.pop("employmentStatus"))

        def _parse_os_version(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        os_version = _parse_os_version(d.pop("osVersion"))

        def _parse_serial_number(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        serial_number = _parse_serial_number(d.pop("serialNumber"))

        user = UserResponsePublicDto.from_dict(d.pop("user"))

        compliance_checks = []
        _compliance_checks = d.pop("complianceChecks")
        for compliance_checks_item_data in _compliance_checks:
            compliance_checks_item = ComplianceCheckResponsePublicDto.from_dict(compliance_checks_item_data)

            compliance_checks.append(compliance_checks_item)

        start_date = d.pop("startDate")

        def _parse_status_updated_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_updated_at_type_0 = isoparse(data)

                return status_updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        status_updated_at = _parse_status_updated_at(d.pop("statusUpdatedAt"))

        data = PersonnelDataResponsePublicDto.from_dict(d.pop("data"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        devices = []
        _devices = d.pop("devices")
        for devices_item_data in _devices:
            devices_item = DeviceResponsePublicDto.from_dict(devices_item_data)

            devices.append(devices_item)

        def _parse_not_human_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        not_human_reason = _parse_not_human_reason(d.pop("notHumanReason", UNSET))

        def _parse_reason_provider(data: object) -> Union["UserResponsePublicDto", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reason_provider_type_1 = UserResponsePublicDto.from_dict(data)

                return reason_provider_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserResponsePublicDto", None, Unset], data)

        reason_provider = _parse_reason_provider(d.pop("reasonProvider", UNSET))

        compliance_tests = []
        _compliance_tests = d.pop("complianceTests", UNSET)
        for compliance_tests_item_data in _compliance_tests or []:
            compliance_tests_item = ComplianceTestResponsePublicDto.from_dict(compliance_tests_item_data)

            compliance_tests.append(compliance_tests_item)

        def _parse_separation_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        separation_date = _parse_separation_date(d.pop("separationDate", UNSET))

        personnel_details_response_public_dto = cls(
            id=id,
            employment_status=employment_status,
            os_version=os_version,
            serial_number=serial_number,
            user=user,
            compliance_checks=compliance_checks,
            start_date=start_date,
            status_updated_at=status_updated_at,
            data=data,
            created_at=created_at,
            updated_at=updated_at,
            devices=devices,
            not_human_reason=not_human_reason,
            reason_provider=reason_provider,
            compliance_tests=compliance_tests,
            separation_date=separation_date,
        )

        personnel_details_response_public_dto.additional_properties = d
        return personnel_details_response_public_dto

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
