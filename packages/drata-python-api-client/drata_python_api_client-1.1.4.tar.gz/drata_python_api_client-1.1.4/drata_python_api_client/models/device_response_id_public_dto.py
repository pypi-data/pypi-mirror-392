import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.asset_without_personnel_response_public_dto import AssetWithoutPersonnelResponsePublicDto
    from ..models.device_app_response_public_dto import DeviceAppResponsePublicDto
    from ..models.device_compliance_check_response_public_dto import DeviceComplianceCheckResponsePublicDto
    from ..models.device_document_response_public_dto import DeviceDocumentResponsePublicDto
    from ..models.device_identifier_response_public_dto import DeviceIdentifierResponsePublicDto
    from ..models.device_response_id_public_dto_antivirus_explanation_type_0 import (
        DeviceResponseIdPublicDtoAntivirusExplanationType0,
    )
    from ..models.device_response_id_public_dto_auto_update_explanation_type_0 import (
        DeviceResponseIdPublicDtoAutoUpdateExplanationType0,
    )
    from ..models.device_response_id_public_dto_encryption_explanation_type_0 import (
        DeviceResponseIdPublicDtoEncryptionExplanationType0,
    )
    from ..models.device_response_id_public_dto_firewall_explanation_type_0 import (
        DeviceResponseIdPublicDtoFirewallExplanationType0,
    )
    from ..models.device_response_id_public_dto_password_manager_explanation_type_0 import (
        DeviceResponseIdPublicDtoPasswordManagerExplanationType0,
    )
    from ..models.device_response_id_public_dto_screen_lock_explanation_type_0 import (
        DeviceResponseIdPublicDtoScreenLockExplanationType0,
    )


T = TypeVar("T", bound="DeviceResponseIdPublicDto")


@_attrs_define
class DeviceResponseIdPublicDto:
    """
    Attributes:
        id (float): Device Id Example: 1.
        os_version (Union[None, str]): The device operating system version Example: MacOS 10.15.6.
        serial_number (Union[None, str]): The device serial number Example: C02T6CDJGTFL.
        model (Union[None, str]): The device model Example: MacBook Pro.
        mac_address (Union[None, str]): The device MAC address Example: 65-F9-3D-85-7B-6B,99-A9-3E-14-7A-3E.
        encryption_enabled (Union[None, bool]): Denotes device actual encryption status
        encryption_explanation (Union['DeviceResponseIdPublicDtoEncryptionExplanationType0', None]): Encryption
            explanation Example: No encryption provided.
        firewall_enabled (Union[None, bool]): Denotes device actual firewall status Example: True.
        firewall_explanation (Union['DeviceResponseIdPublicDtoFirewallExplanationType0', None]): Firewall explanation
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
        screen_lock_time (Union[None, float]): Denotes device actual screenLock time Example: 30.
        screen_lock_explanation (Union['DeviceResponseIdPublicDtoScreenLockExplanationType0', None]): Screen look
            explanation Example: {'minutesIdleBeforeSleep': '2', 'minutesSleepingBeforePasswordIsRequired': '2'}.
        antivirus_enabled (Union[None, bool]): Denotes device actual antivirus status Example: True.
        antivirus_explanation (Union['DeviceResponseIdPublicDtoAntivirusExplanationType0', None]): Antivirus explanation
            Example: No matching app was found.
        auto_update_enabled (Union[None, bool]): Denotes device actual auto-update status Example: True.
        auto_update_explanation (Union['DeviceResponseIdPublicDtoAutoUpdateExplanationType0', None]): Auto update
            explanation Example: No compliances found.
        password_manager_enabled (Union[None, bool]): Denotes device actual password manager status Example: True.
        password_manager_explanation (Union['DeviceResponseIdPublicDtoPasswordManagerExplanationType0', None]): password
            manager explanation Example: {'passwordManagerApps': ['1password 7']}.
        user_id (float): User Id Example: 1.
        personnel_id (float): Personnel Id Example: 1.
        external_id (Union[None, str]): An externally sourced unique identifier for a device Example: aaaaaaaa-
            bbbb-0000-cccc-dddddddddddd.
        compliance_checks (Union[Unset, list['DeviceComplianceCheckResponsePublicDto']]): The device compliance checks
            list
        identifiers (Union[Unset, list['DeviceIdentifierResponsePublicDto']]): The device identifiers list
        documents (Union[Unset, list['DeviceDocumentResponsePublicDto']]): The device documents list
        asset (Union[Unset, AssetWithoutPersonnelResponsePublicDto]):
        apps (Union[Unset, list['DeviceAppResponsePublicDto']]): Apps associated with the given device
    """

    id: float
    os_version: Union[None, str]
    serial_number: Union[None, str]
    model: Union[None, str]
    mac_address: Union[None, str]
    encryption_enabled: Union[None, bool]
    encryption_explanation: Union["DeviceResponseIdPublicDtoEncryptionExplanationType0", None]
    firewall_enabled: Union[None, bool]
    firewall_explanation: Union["DeviceResponseIdPublicDtoFirewallExplanationType0", None]
    last_checked_at: Union[None, datetime.datetime]
    source_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: Union[None, datetime.datetime]
    apps_count: Union[None, float]
    is_device_compliant: bool
    screen_lock_time: Union[None, float]
    screen_lock_explanation: Union["DeviceResponseIdPublicDtoScreenLockExplanationType0", None]
    antivirus_enabled: Union[None, bool]
    antivirus_explanation: Union["DeviceResponseIdPublicDtoAntivirusExplanationType0", None]
    auto_update_enabled: Union[None, bool]
    auto_update_explanation: Union["DeviceResponseIdPublicDtoAutoUpdateExplanationType0", None]
    password_manager_enabled: Union[None, bool]
    password_manager_explanation: Union["DeviceResponseIdPublicDtoPasswordManagerExplanationType0", None]
    user_id: float
    personnel_id: float
    external_id: Union[None, str]
    compliance_checks: Union[Unset, list["DeviceComplianceCheckResponsePublicDto"]] = UNSET
    identifiers: Union[Unset, list["DeviceIdentifierResponsePublicDto"]] = UNSET
    documents: Union[Unset, list["DeviceDocumentResponsePublicDto"]] = UNSET
    asset: Union[Unset, "AssetWithoutPersonnelResponsePublicDto"] = UNSET
    apps: Union[Unset, list["DeviceAppResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.device_response_id_public_dto_antivirus_explanation_type_0 import (
            DeviceResponseIdPublicDtoAntivirusExplanationType0,
        )
        from ..models.device_response_id_public_dto_auto_update_explanation_type_0 import (
            DeviceResponseIdPublicDtoAutoUpdateExplanationType0,
        )
        from ..models.device_response_id_public_dto_encryption_explanation_type_0 import (
            DeviceResponseIdPublicDtoEncryptionExplanationType0,
        )
        from ..models.device_response_id_public_dto_firewall_explanation_type_0 import (
            DeviceResponseIdPublicDtoFirewallExplanationType0,
        )
        from ..models.device_response_id_public_dto_password_manager_explanation_type_0 import (
            DeviceResponseIdPublicDtoPasswordManagerExplanationType0,
        )
        from ..models.device_response_id_public_dto_screen_lock_explanation_type_0 import (
            DeviceResponseIdPublicDtoScreenLockExplanationType0,
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
        if isinstance(self.encryption_explanation, DeviceResponseIdPublicDtoEncryptionExplanationType0):
            encryption_explanation = self.encryption_explanation.to_dict()
        else:
            encryption_explanation = self.encryption_explanation

        firewall_enabled: Union[None, bool]
        firewall_enabled = self.firewall_enabled

        firewall_explanation: Union[None, dict[str, Any]]
        if isinstance(self.firewall_explanation, DeviceResponseIdPublicDtoFirewallExplanationType0):
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
        if isinstance(self.screen_lock_explanation, DeviceResponseIdPublicDtoScreenLockExplanationType0):
            screen_lock_explanation = self.screen_lock_explanation.to_dict()
        else:
            screen_lock_explanation = self.screen_lock_explanation

        antivirus_enabled: Union[None, bool]
        antivirus_enabled = self.antivirus_enabled

        antivirus_explanation: Union[None, dict[str, Any]]
        if isinstance(self.antivirus_explanation, DeviceResponseIdPublicDtoAntivirusExplanationType0):
            antivirus_explanation = self.antivirus_explanation.to_dict()
        else:
            antivirus_explanation = self.antivirus_explanation

        auto_update_enabled: Union[None, bool]
        auto_update_enabled = self.auto_update_enabled

        auto_update_explanation: Union[None, dict[str, Any]]
        if isinstance(self.auto_update_explanation, DeviceResponseIdPublicDtoAutoUpdateExplanationType0):
            auto_update_explanation = self.auto_update_explanation.to_dict()
        else:
            auto_update_explanation = self.auto_update_explanation

        password_manager_enabled: Union[None, bool]
        password_manager_enabled = self.password_manager_enabled

        password_manager_explanation: Union[None, dict[str, Any]]
        if isinstance(self.password_manager_explanation, DeviceResponseIdPublicDtoPasswordManagerExplanationType0):
            password_manager_explanation = self.password_manager_explanation.to_dict()
        else:
            password_manager_explanation = self.password_manager_explanation

        user_id = self.user_id

        personnel_id = self.personnel_id

        external_id: Union[None, str]
        external_id = self.external_id

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

        asset: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.asset, Unset):
            asset = self.asset.to_dict()

        apps: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.apps, Unset):
            apps = []
            for apps_item_data in self.apps:
                apps_item = apps_item_data.to_dict()
                apps.append(apps_item)

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
                "userId": user_id,
                "personnelId": personnel_id,
                "externalId": external_id,
            }
        )
        if compliance_checks is not UNSET:
            field_dict["complianceChecks"] = compliance_checks
        if identifiers is not UNSET:
            field_dict["identifiers"] = identifiers
        if documents is not UNSET:
            field_dict["documents"] = documents
        if asset is not UNSET:
            field_dict["asset"] = asset
        if apps is not UNSET:
            field_dict["apps"] = apps

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.asset_without_personnel_response_public_dto import AssetWithoutPersonnelResponsePublicDto
        from ..models.device_app_response_public_dto import DeviceAppResponsePublicDto
        from ..models.device_compliance_check_response_public_dto import DeviceComplianceCheckResponsePublicDto
        from ..models.device_document_response_public_dto import DeviceDocumentResponsePublicDto
        from ..models.device_identifier_response_public_dto import DeviceIdentifierResponsePublicDto
        from ..models.device_response_id_public_dto_antivirus_explanation_type_0 import (
            DeviceResponseIdPublicDtoAntivirusExplanationType0,
        )
        from ..models.device_response_id_public_dto_auto_update_explanation_type_0 import (
            DeviceResponseIdPublicDtoAutoUpdateExplanationType0,
        )
        from ..models.device_response_id_public_dto_encryption_explanation_type_0 import (
            DeviceResponseIdPublicDtoEncryptionExplanationType0,
        )
        from ..models.device_response_id_public_dto_firewall_explanation_type_0 import (
            DeviceResponseIdPublicDtoFirewallExplanationType0,
        )
        from ..models.device_response_id_public_dto_password_manager_explanation_type_0 import (
            DeviceResponseIdPublicDtoPasswordManagerExplanationType0,
        )
        from ..models.device_response_id_public_dto_screen_lock_explanation_type_0 import (
            DeviceResponseIdPublicDtoScreenLockExplanationType0,
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
        ) -> Union["DeviceResponseIdPublicDtoEncryptionExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                encryption_explanation_type_0 = DeviceResponseIdPublicDtoEncryptionExplanationType0.from_dict(data)

                return encryption_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoEncryptionExplanationType0", None], data)

        encryption_explanation = _parse_encryption_explanation(d.pop("encryptionExplanation"))

        def _parse_firewall_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        firewall_enabled = _parse_firewall_enabled(d.pop("firewallEnabled"))

        def _parse_firewall_explanation(
            data: object,
        ) -> Union["DeviceResponseIdPublicDtoFirewallExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                firewall_explanation_type_0 = DeviceResponseIdPublicDtoFirewallExplanationType0.from_dict(data)

                return firewall_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoFirewallExplanationType0", None], data)

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
        ) -> Union["DeviceResponseIdPublicDtoScreenLockExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                screen_lock_explanation_type_0 = DeviceResponseIdPublicDtoScreenLockExplanationType0.from_dict(data)

                return screen_lock_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoScreenLockExplanationType0", None], data)

        screen_lock_explanation = _parse_screen_lock_explanation(d.pop("screenLockExplanation"))

        def _parse_antivirus_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        antivirus_enabled = _parse_antivirus_enabled(d.pop("antivirusEnabled"))

        def _parse_antivirus_explanation(
            data: object,
        ) -> Union["DeviceResponseIdPublicDtoAntivirusExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                antivirus_explanation_type_0 = DeviceResponseIdPublicDtoAntivirusExplanationType0.from_dict(data)

                return antivirus_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoAntivirusExplanationType0", None], data)

        antivirus_explanation = _parse_antivirus_explanation(d.pop("antivirusExplanation"))

        def _parse_auto_update_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        auto_update_enabled = _parse_auto_update_enabled(d.pop("autoUpdateEnabled"))

        def _parse_auto_update_explanation(
            data: object,
        ) -> Union["DeviceResponseIdPublicDtoAutoUpdateExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                auto_update_explanation_type_0 = DeviceResponseIdPublicDtoAutoUpdateExplanationType0.from_dict(data)

                return auto_update_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoAutoUpdateExplanationType0", None], data)

        auto_update_explanation = _parse_auto_update_explanation(d.pop("autoUpdateExplanation"))

        def _parse_password_manager_enabled(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        password_manager_enabled = _parse_password_manager_enabled(d.pop("passwordManagerEnabled"))

        def _parse_password_manager_explanation(
            data: object,
        ) -> Union["DeviceResponseIdPublicDtoPasswordManagerExplanationType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                password_manager_explanation_type_0 = (
                    DeviceResponseIdPublicDtoPasswordManagerExplanationType0.from_dict(data)
                )

                return password_manager_explanation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeviceResponseIdPublicDtoPasswordManagerExplanationType0", None], data)

        password_manager_explanation = _parse_password_manager_explanation(d.pop("passwordManagerExplanation"))

        user_id = d.pop("userId")

        personnel_id = d.pop("personnelId")

        def _parse_external_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        external_id = _parse_external_id(d.pop("externalId"))

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

        _asset = d.pop("asset", UNSET)
        asset: Union[Unset, AssetWithoutPersonnelResponsePublicDto]
        if isinstance(_asset, Unset):
            asset = UNSET
        else:
            asset = AssetWithoutPersonnelResponsePublicDto.from_dict(_asset)

        apps = []
        _apps = d.pop("apps", UNSET)
        for apps_item_data in _apps or []:
            apps_item = DeviceAppResponsePublicDto.from_dict(apps_item_data)

            apps.append(apps_item)

        device_response_id_public_dto = cls(
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
            user_id=user_id,
            personnel_id=personnel_id,
            external_id=external_id,
            compliance_checks=compliance_checks,
            identifiers=identifiers,
            documents=documents,
            asset=asset,
            apps=apps,
        )

        device_response_id_public_dto.additional_properties = d
        return device_response_id_public_dto

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
