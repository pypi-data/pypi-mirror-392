import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonnelDataResponsePublicDto")


@_attrs_define
class PersonnelDataResponsePublicDto:
    """
    Attributes:
        created_at (datetime.datetime): Personnel created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Personnel updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        os_version (Union[None, Unset, str]): The Operating System version this personnel uses Example: MacOS 10.15.6.
        serial_number (Union[None, Unset, str]): Workstation Serial Number this personnel uses Example: C02T6CDJGTFL.
        screen_lock_time (Union[None, Unset, float]): The number of seconds the lock screen must be enabled before this
            personnel is prompted to enter a password Example: 60.
        agent_version (Union[None, Unset, str]): The Agent version this personnel uses Example: 1.0.
        mac_address (Union[None, Unset, str]): The MAC addresses of the machine this personnel uses Example:
            65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        lastchecked_at (Union[None, Unset, datetime.datetime]): Personnel data last checked by agent timestamp Example:
            2025-07-01T16:45:55.246Z.
    """

    created_at: datetime.datetime
    updated_at: datetime.datetime
    os_version: Union[None, Unset, str] = UNSET
    serial_number: Union[None, Unset, str] = UNSET
    screen_lock_time: Union[None, Unset, float] = UNSET
    agent_version: Union[None, Unset, str] = UNSET
    mac_address: Union[None, Unset, str] = UNSET
    lastchecked_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        os_version: Union[None, Unset, str]
        if isinstance(self.os_version, Unset):
            os_version = UNSET
        else:
            os_version = self.os_version

        serial_number: Union[None, Unset, str]
        if isinstance(self.serial_number, Unset):
            serial_number = UNSET
        else:
            serial_number = self.serial_number

        screen_lock_time: Union[None, Unset, float]
        if isinstance(self.screen_lock_time, Unset):
            screen_lock_time = UNSET
        else:
            screen_lock_time = self.screen_lock_time

        agent_version: Union[None, Unset, str]
        if isinstance(self.agent_version, Unset):
            agent_version = UNSET
        else:
            agent_version = self.agent_version

        mac_address: Union[None, Unset, str]
        if isinstance(self.mac_address, Unset):
            mac_address = UNSET
        else:
            mac_address = self.mac_address

        lastchecked_at: Union[None, Unset, str]
        if isinstance(self.lastchecked_at, Unset):
            lastchecked_at = UNSET
        elif isinstance(self.lastchecked_at, datetime.datetime):
            lastchecked_at = self.lastchecked_at.isoformat()
        else:
            lastchecked_at = self.lastchecked_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if os_version is not UNSET:
            field_dict["osVersion"] = os_version
        if serial_number is not UNSET:
            field_dict["serialNumber"] = serial_number
        if screen_lock_time is not UNSET:
            field_dict["screenLockTime"] = screen_lock_time
        if agent_version is not UNSET:
            field_dict["agentVersion"] = agent_version
        if mac_address is not UNSET:
            field_dict["macAddress"] = mac_address
        if lastchecked_at is not UNSET:
            field_dict["lastcheckedAt"] = lastchecked_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_os_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        os_version = _parse_os_version(d.pop("osVersion", UNSET))

        def _parse_serial_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        serial_number = _parse_serial_number(d.pop("serialNumber", UNSET))

        def _parse_screen_lock_time(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        screen_lock_time = _parse_screen_lock_time(d.pop("screenLockTime", UNSET))

        def _parse_agent_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        agent_version = _parse_agent_version(d.pop("agentVersion", UNSET))

        def _parse_mac_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mac_address = _parse_mac_address(d.pop("macAddress", UNSET))

        def _parse_lastchecked_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                lastchecked_at_type_0 = isoparse(data)

                return lastchecked_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        lastchecked_at = _parse_lastchecked_at(d.pop("lastcheckedAt", UNSET))

        personnel_data_response_public_dto = cls(
            created_at=created_at,
            updated_at=updated_at,
            os_version=os_version,
            serial_number=serial_number,
            screen_lock_time=screen_lock_time,
            agent_version=agent_version,
            mac_address=mac_address,
            lastchecked_at=lastchecked_at,
        )

        personnel_data_response_public_dto.additional_properties = d
        return personnel_data_response_public_dto

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
