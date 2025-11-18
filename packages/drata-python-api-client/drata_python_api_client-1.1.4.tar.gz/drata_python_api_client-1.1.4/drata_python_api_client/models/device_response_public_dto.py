import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_compliance_check_response_public_dto import DeviceComplianceCheckResponsePublicDto
    from ..models.device_document_response_public_dto import DeviceDocumentResponsePublicDto
    from ..models.device_identifier_response_public_dto import DeviceIdentifierResponsePublicDto
    from ..models.device_response_public_dto_antivirus_explanation_type_0 import (
        DeviceResponsePublicDtoAntivirusExplanationType0,
    )
    from ..models.device_response_public_dto_auto_update_explanation_type_0 import (
        DeviceResponsePublicDtoAutoUpdateExplanationType0,
    )
    from ..models.device_response_public_dto_encryption_explanation_type_0 import (
        DeviceResponsePublicDtoEncryptionExplanationType0,
    )
    from ..models.device_response_public_dto_firewall_explanation_type_0 import (
        DeviceResponsePublicDtoFirewallExplanationType0,
    )
    from ..models.device_response_public_dto_password_manager_explanation_type_0 import (
        DeviceResponsePublicDtoPasswordManagerExplanationType0,
    )
    from ..models.device_response_public_dto_screen_lock_explanation_type_0 import (
        DeviceResponsePublicDtoScreenLockExplanationType0,
    )


T = TypeVar("T", bound="DeviceResponsePublicDto")


@_attrs_define
class DeviceResponsePublicDto:
    """
    Attributes:
        id (float): Device Id Example: 1.
        os_version (Union[None, str]): The device operating system version Example: MacOS 10.15.6.
        serial_number (Union[None, str]): The device serial number Example: C02T6CDJGTFL.
        model (Union[None, str]): The device model Example: MacBook Pro.
        mac_address (Union[None, str]): The device MAC address Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        encryption_enabled (Union[None, bool]): Denotes device actual encryption status
        encryption_explanation (Union['DeviceResponsePublicDtoEncryptionExplanationType0', None]): Encryption
            explanation Example: No encryption provided.
        firewall_enabled (Union[None, bool]): Denotes device actual firewall status Example: True.
        firewall_explanation (Union['DeviceResponsePublicDtoFirewallExplanationType0', None]): Firewall explanation
            Example: {}.
        last_checked_at (Union[None, datetime.datetime]): Last time device data checked by the source Example:
            2025-07-01T16:45:55.246Z.
        source_type (str): The device source type Example: AGENT.
        created_at (datetime.datetime): The device created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): The device updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        deleted_at (Union[None, datetime.datetime]): The device deleted date timestamp Example:
            2025-07-01T16:45:55.246Z.
        apps_count (Union[None, float]): The number of applications installed Example: 20.
        is_device_compliant (bool): Is device compliant
        screen_lock_time (Union[None, float]): The number of seconds the lock screen must be enabled before this device
            is prompted to enter a password Example: 60.
        screen_lock_explanation (Union['DeviceResponsePublicDtoScreenLockExplanationType0', None]): Screen look
            explanation Example: {'minutesIdleBeforeSleep': '2', 'minutesSleepingBeforePasswordIsRequired': '2'}.
        antivirus_enabled (Union[None, bool]): Denotes device actual antivirus status Example: True.
        antivirus_explanation (Union['DeviceResponsePublicDtoAntivirusExplanationType0', None]): Antivirus explanation
            Example: No matching app was found.
        auto_update_enabled (Union[None, bool]): Denotes device actual auto-update status Example: True.
        auto_update_explanation (Union['DeviceResponsePublicDtoAutoUpdateExplanationType0', None]): Auto update
            explanation Example: No compliances found.
        password_manager_enabled (Union[None, bool]): Denotes device actual password manager status Example: True.
        password_manager_explanation (Union['DeviceResponsePublicDtoPasswordManagerExplanationType0', None]): password
            manager explanation Example: {'passwordManagerApps': ['1password 7']}.
        agent_version (Union[None, str]): The agent version this device uses Example: 1.0.
        compliance_checks (Union[Unset, list['DeviceComplianceCheckResponsePublicDto']]): The device compliance checks
            list
        identifiers (Union[Unset, list['DeviceIdentifierResponsePublicDto']]): The device identifiers list
        documents (Union[Unset, list['DeviceDocumentResponsePublicDto']]): The device documents list
    """

    id: float
    os_version: Union[None, str]
    serial_number: Union[None, str]
    model: Union[None, str]
    mac_address: Union[None, str]
    encryption_enabled: Union[None, bool]
    encryption_explanation: Union["DeviceResponsePublicDtoEncryptionExplanationType0", None]
    firewall_enabled: Union[None, bool]
    firewall_explanation: Union["DeviceResponsePublicDtoFirewallExplanationType0", None]
    last_checked_at: Union[None, datetime.datetime]
    source_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: Union[None, datetime.datetime]
    apps_count: Union[None, float]
    is_device_compliant: bool
    screen_lock_time: Union[None, float]
    screen_lock_explanation: Union["DeviceResponsePublicDtoScreenLockExplanationType0", None]
    antivirus_enabled: Union[None, bool]
    antivirus_explanation: Union["DeviceResponsePublicDtoAntivirusExplanationType0", None]
    auto_update_enabled: Union[None, bool]
    auto_update_explanation: Union["DeviceResponsePublicDtoAutoUpdateExplanationType0", None]
    password_manager_enabled: Union[None, bool]
    password_manager_explanation: Union["DeviceResponsePublicDtoPasswordManagerExplanationType0", None]
    agent_version: Union[None, str]
    compliance_checks: Union[Unset, list["DeviceComplianceCheckResponsePublicDto"]] = UNSET
    identifiers: Union[Unset, list["DeviceIdentifierResponsePublicDto"]] = UNSET
    documents: Union[Unset, list["DeviceDocumentResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.device_response_public_dto_antivirus_explanation_type_0 import (
            DeviceResponsePublicDtoAntivirusExplanationType0,
        )
        from ..models.device_response_public_dto_auto_update_explanation_type_0 import (
            DeviceResponsePublicDtoAutoUpdateExplanationType0,
        )
        from ..models.device_response_public_dto_encryption_explanation_type_0 import (
            DeviceResponsePublicDtoEncryptionExplanationType0,
        )
        from ..models.device_response_public_dto_firewall_explanation_type_0 import (
            DeviceResponsePublicDtoFirewallExplanationType0,
        )
        from ..models.device_response_public_dto_password_manager_explanation_type_0 import (
            DeviceResponsePublicDtoPasswordManagerExplanationType0,
        )
        from ..models.device_response_public_dto_screen_lock_explanation_type_0 import (
            DeviceResponsePublicDtoScreenLockExplanationType0,
        )

        id = self.id

        os_version: Union[None, str]
        os_version = self.os_version

        serial_number: Union[None, str]
        serial_number = self.serial_number

        model: Union[None, str]
        model = self.model

        mac_address: Union[None, str]
        mac_address = self.mac_address

        encryption_enabled: Union[None, bool]
        encryption_enabled = self.encryption_enabled

        encryption_explanation: Union[None, dict[str, Any]]
        if isinstance(self.encryption_explanation, DeviceResponsePublicDtoEncryptionExplanationType0):
            encryption_explanation = self.encryption_explanation.to_dict()
        else:
            encryption_explanation = self.encryption_explanation

        firewall_enabled: Union[None, bool]
        firewall_enabled = self.firewall_enabled

        firewall_explanation: Union[None, dict[str, Any]]
        if isinstance(self.firewall_explanation, DeviceResponsePublicDtoFirewallExplanationType0):
            firewall_explanation = self.firewall_explanation.to_dict()
        else:
            firewall_explanation = self.firewall_explanation

        last_checked_at: Union[None, str]
        if isinstance(self.last_checked_at, datetime.datetime):
            last_checked_at = self.last_checked_at.isoformat()
        else:
            last_checked_at = self.last_checked_at

        source_type = self.source_type

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        deleted_at: Union[None, str]
        if isinstance(self.deleted_at, datetime.datetime):
            deleted_at = self.deleted_at.isoformat()
        else:
            deleted_at = self.deleted_at

        apps_count: Union[None, float]
        apps_count = self.apps_count

        is_device_compliant = self.is_device_compliant

        screen_lock_time: Union[None, float]
        screen_lock_time = self.screen_lock_time

        screen_lock_explanation: Union[None, dict[str, Any]]
        if isinstance(self.screen_lock_explanation, DeviceResponsePublicDtoScreenLockExplanationType0):
            screen_lock_explanation = self.screen_lock_explanation.to_dict()
        else:
            screen_lock_explanation = self.screen_lock_explanation

        antivirus_enabled: Union[None, bool]
        antivirus_enabled = self.antivirus_enabled

        antivirus_explanation: Union[None, dict[str, Any]]
        if isinstance(self.antivirus_explanation, DeviceResponsePublicDtoAntivirusExplanationType0):
            antivirus_explanation = self.antivirus_explanation.to_dict()
        else:
            antivirus_explanation = self.antivirus_explanation

        auto_update_enabled: Union[None, bool]
        auto_update_enabled = self.auto_update_enabled

        auto_update_explanation: Union[None, dict[str, Any]]
        if isinstance(self.auto_update_explanation, DeviceResponsePublicDtoAutoUpdateExplanationType0):
            auto_update_explanation = self.auto_update_explanation.to_dict()
        else:
            auto_update_explanation = self.auto_update_explanation

        password_manager_enabled: Union[None, bool]
        password_manager_enabled = self.password_manager_enabled

        password_manager_explanation: Union[None, dict[str, Any]]
        if isinstance(self.password_manager_explanation, DeviceResponsePublicDtoPasswordManagerExplanationType0):
            password_manager_explanation = self.password_manager_explanation.to_dict()
        else:
            password_manager_explanation = self.password_manager_explanation

        agent_version: Union[None, str]
        agent_version = self.agent_version

        compliance_checks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.compliance_checks, Unset):
            compliance_checks = []
            for compliance_checks_item_data in self.compliance_checks:
                compliance_checks_item = compliance_checks_item_data.to_dict()
                compliance_checks.append(compliance_checks_item)

        identifiers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.identifiers, Unset):
            identifiers = []
            for identifiers_item_data in self.identifiers:
                identifiers_item = identifiers_item_data.to_dict()
                identifiers.append(identifiers_item)

        documents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.documents, Unset):
            documents = []
            for documents_item_data in self.documents:
                documents_item = documents_item_data.to_dict()
                documents.append(documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "osVersion": os_version,
                "serialNumber": serial_number,
                "model": model,
                "macAddress": mac_address,
                "encryptionEnabled": encryption_enabled,
                "encryptionExplanation": encryption_explanation,
                "firewallEnabled": firewall_enabled,
                "firewallExplanation": firewall_explanation,
                "lastCheckedAt": last_checked_at,
                "sourceType": source_type,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "deletedAt": deleted_at,
                "appsCount": apps_count,
                "isDeviceCompliant": is_device_compliant,
                "screenLockTime": screen_lock_time,
                "screenLockExplanation": screen_lock_explanation,
                "antivirusEnabled": antivirus_enabled,
                "antivirusExplanation": antivirus_explanation,
                "autoUpdateEnabled": auto_update_enabled,
                "autoUpdateExplanation": auto_update_explanation,
                "passwordManagerEnabled": password_manager_enabled,
                "passwordManagerExplanation": password_manager_explanation,
                "agentVersion": agent_version,
            }
        )
        if compliance_checks is not UNSET:
            field_dict["complianceChecks"] = compliance_checks
        if identifiers is not UNSET:
            field_dict["identifiers"] = identifiers
        if documents is not UNSET:
            field_dict["documents"] = documents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_compliance_check_response_public_dto import DeviceComplianceCheckResponsePublicDto
        from ..models.device_document_response_public_dto import DeviceDocumentResponsePublicDto
        from ..models.device_identifier_response_public_dto import DeviceIdentifierResponsePublicDto
        from ..models.device_response_public_dto_antivirus_explanation_type_0 import (
            DeviceResponsePublicDtoAntivirusExplanationType0,
        )
        from ..models.device_response_public_dto_auto_update_explanation_type_0 import (
            DeviceResponsePublicDtoAutoUpdateExplanationType0,
        )
        from ..models.device_response_public_dto_encryption_explanation_type_0 import (
            DeviceResponsePublicDtoEncryptionExplanationType0,
        )
        from ..models.device_response_public_dto_firewall_explanation_type_0 import (
            DeviceResponsePublicDtoFirewallExplanationType0,
        )
        from ..models.device_response_public_dto_password_manager_explanation_type_0 import (
            DeviceResponsePublicDtoPasswordManagerExplanationType0,
        )
        from ..models.device_response_public_dto_screen_lock_explanation_type_0 import (
            DeviceResponsePublicDtoScreenLockExplanationType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

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

        def _parse_model(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        model = _parse_model(d.pop("model"))

        def _parse_mac_address(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        mac_address = _parse_mac_address(d.pop("macAddress"))

        def _parse_encryption_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        encryption_enabled = _parse_encryption_enabled(d.pop("encryptionEnabled"))

        def _parse_encryption_explanation(
            data: object,
        ) -> Union["DeviceResponsePublicDtoEncryptionExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                encryption_explanation_type_0 = DeviceResponsePublicDtoEncryptionExplanationType0.from_dict(data)

                return encryption_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoEncryptionExplanationType0", None], data)

        encryption_explanation = _parse_encryption_explanation(d.pop("encryptionExplanation"))

        def _parse_firewall_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        firewall_enabled = _parse_firewall_enabled(d.pop("firewallEnabled"))

        def _parse_firewall_explanation(data: object) -> Union["DeviceResponsePublicDtoFirewallExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                firewall_explanation_type_0 = DeviceResponsePublicDtoFirewallExplanationType0.from_dict(data)

                return firewall_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoFirewallExplanationType0", None], data)

        firewall_explanation = _parse_firewall_explanation(d.pop("firewallExplanation"))

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

        source_type = d.pop("sourceType")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_deleted_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_at_type_0 = isoparse(data)

                return deleted_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        deleted_at = _parse_deleted_at(d.pop("deletedAt"))

        def _parse_apps_count(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        apps_count = _parse_apps_count(d.pop("appsCount"))

        is_device_compliant = d.pop("isDeviceCompliant")

        def _parse_screen_lock_time(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        screen_lock_time = _parse_screen_lock_time(d.pop("screenLockTime"))

        def _parse_screen_lock_explanation(
            data: object,
        ) -> Union["DeviceResponsePublicDtoScreenLockExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                screen_lock_explanation_type_0 = DeviceResponsePublicDtoScreenLockExplanationType0.from_dict(data)

                return screen_lock_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoScreenLockExplanationType0", None], data)

        screen_lock_explanation = _parse_screen_lock_explanation(d.pop("screenLockExplanation"))

        def _parse_antivirus_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        antivirus_enabled = _parse_antivirus_enabled(d.pop("antivirusEnabled"))

        def _parse_antivirus_explanation(
            data: object,
        ) -> Union["DeviceResponsePublicDtoAntivirusExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                antivirus_explanation_type_0 = DeviceResponsePublicDtoAntivirusExplanationType0.from_dict(data)

                return antivirus_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoAntivirusExplanationType0", None], data)

        antivirus_explanation = _parse_antivirus_explanation(d.pop("antivirusExplanation"))

        def _parse_auto_update_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        auto_update_enabled = _parse_auto_update_enabled(d.pop("autoUpdateEnabled"))

        def _parse_auto_update_explanation(
            data: object,
        ) -> Union["DeviceResponsePublicDtoAutoUpdateExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                auto_update_explanation_type_0 = DeviceResponsePublicDtoAutoUpdateExplanationType0.from_dict(data)

                return auto_update_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoAutoUpdateExplanationType0", None], data)

        auto_update_explanation = _parse_auto_update_explanation(d.pop("autoUpdateExplanation"))

        def _parse_password_manager_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        password_manager_enabled = _parse_password_manager_enabled(d.pop("passwordManagerEnabled"))

        def _parse_password_manager_explanation(
            data: object,
        ) -> Union["DeviceResponsePublicDtoPasswordManagerExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                password_manager_explanation_type_0 = DeviceResponsePublicDtoPasswordManagerExplanationType0.from_dict(
                    data
                )

                return password_manager_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponsePublicDtoPasswordManagerExplanationType0", None], data)

        password_manager_explanation = _parse_password_manager_explanation(d.pop("passwordManagerExplanation"))

        def _parse_agent_version(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        agent_version = _parse_agent_version(d.pop("agentVersion"))

        compliance_checks = []
        _compliance_checks = d.pop("complianceChecks", UNSET)
        for compliance_checks_item_data in _compliance_checks or []:
            compliance_checks_item = DeviceComplianceCheckResponsePublicDto.from_dict(compliance_checks_item_data)

            compliance_checks.append(compliance_checks_item)

        identifiers = []
        _identifiers = d.pop("identifiers", UNSET)
        for identifiers_item_data in _identifiers or []:
            identifiers_item = DeviceIdentifierResponsePublicDto.from_dict(identifiers_item_data)

            identifiers.append(identifiers_item)

        documents = []
        _documents = d.pop("documents", UNSET)
        for documents_item_data in _documents or []:
            documents_item = DeviceDocumentResponsePublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        device_response_public_dto = cls(
            id=id,
            os_version=os_version,
            serial_number=serial_number,
            model=model,
            mac_address=mac_address,
            encryption_enabled=encryption_enabled,
            encryption_explanation=encryption_explanation,
            firewall_enabled=firewall_enabled,
            firewall_explanation=firewall_explanation,
            last_checked_at=last_checked_at,
            source_type=source_type,
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at,
            apps_count=apps_count,
            is_device_compliant=is_device_compliant,
            screen_lock_time=screen_lock_time,
            screen_lock_explanation=screen_lock_explanation,
            antivirus_enabled=antivirus_enabled,
            antivirus_explanation=antivirus_explanation,
            auto_update_enabled=auto_update_enabled,
            auto_update_explanation=auto_update_explanation,
            password_manager_enabled=password_manager_enabled,
            password_manager_explanation=password_manager_explanation,
            agent_version=agent_version,
            compliance_checks=compliance_checks,
            identifiers=identifiers,
            documents=documents,
        )

        device_response_public_dto.additional_properties = d
        return device_response_public_dto

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
