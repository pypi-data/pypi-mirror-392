from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_device_request_public_dto_platform_name import CreateDeviceRequestPublicDtoPlatformName
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.app_type_request_public_dto import AppTypeRequestPublicDto
    from ..models.create_device_request_public_dto_antivirus_explanation import (
        CreateDeviceRequestPublicDtoAntivirusExplanation,
    )
    from ..models.create_device_request_public_dto_auto_update_explanation import (
        CreateDeviceRequestPublicDtoAutoUpdateExplanation,
    )
    from ..models.create_device_request_public_dto_encryption_explanation import (
        CreateDeviceRequestPublicDtoEncryptionExplanation,
    )
    from ..models.create_device_request_public_dto_firewall_explanation import (
        CreateDeviceRequestPublicDtoFirewallExplanation,
    )
    from ..models.create_device_request_public_dto_password_manager_explanation import (
        CreateDeviceRequestPublicDtoPasswordManagerExplanation,
    )
    from ..models.create_device_request_public_dto_screen_lock_explanation import (
        CreateDeviceRequestPublicDtoScreenLockExplanation,
    )
    from ..models.windows_service_request_public_dto import WindowsServiceRequestPublicDto


T = TypeVar("T", bound="CreateDeviceRequestPublicDto")


@_attrs_define
class CreateDeviceRequestPublicDto:
    """
    Attributes:
        personnel_id (float): Personnel Id Example: 1.
        platform_name (CreateDeviceRequestPublicDtoPlatformName): The Operating System (OS) platform name of the device
            Example: MACOS.
        platform_version (str): The Operating System (OS) platform version of the device
        alias (Union[Unset, str]): Name of the device. Example: danielm-01.
        antivirus_enabled (Union[None, Unset, bool]): Flag to indicate antivirus software is installed and enabled
            Example: True.
        antivirus_explanation (Union[Unset, CreateDeviceRequestPublicDtoAntivirusExplanation]): Any additional
            information to explain the antivirusEnabled value Example: {'antivirusApps': ['Crowdstrike windows sensor']}.
        app_list (Union[Unset, list['AppTypeRequestPublicDto']]): List of installed applications
        auto_update_enabled (Union[None, Unset, bool]): Flag to indicate auto-update enabled or disabled Example: True.
        auto_update_explanation (Union[Unset, CreateDeviceRequestPublicDtoAutoUpdateExplanation]): Any additional
            information to explain the autoUpdateEnabled value Example: Disabled.
        browser_extensions (Union[Unset, list['AppTypeRequestPublicDto']]): List of installed browser extensions
        external_id (Union[Unset, str]): An externally-sourced unique identifier for a device Example:
            39ce3845-758c-42cc-a99f-298ec991e80a.
        firewall_enabled (Union[None, Unset, bool]): Flag to indicate the firewall is enabled or disabled Example: True.
        firewall_explanation (Union[Unset, CreateDeviceRequestPublicDtoFirewallExplanation]): Any additional information
            to explain the firewallEnabled value Example: On.
        password_manager_enabled (Union[None, Unset, bool]): Flag to indicate a password manager is in use Example:
            True.
        encryption_enabled (Union[None, Unset, bool]): Flag to indicate hard disk is encrypted Example: True.
        encryption_explanation (Union[Unset, CreateDeviceRequestPublicDtoEncryptionExplanation]): Any additional
            information to explain the encryptionEnabled value Example: {'bootPartitionEncryptionDetails':
            {'partitionFileVault2Percent': 100, 'partitionFileVault2State': 'ENCRYPTED', 'partitionName': 'Macintosh HD
            (Boot Partition)'}}.
        model (Union[Unset, str]): Hardware model Example: Mac16,1.
        serial_number (Union[Unset, str]): Hardware serial number Example: BKH8RXT4T9.
        mac_address (Union[None, Unset, str]): MAC address Example: 01-23-45-67-89-AB.
        password_manager_explanation (Union[Unset, CreateDeviceRequestPublicDtoPasswordManagerExplanation]): Any
            additional information to explain the hasPasswordManager value Example: {'passwordManagerApps': ['1password']}.
        screen_lock_enabled (Union[None, Unset, bool]): Flag to indicate hard disk is encrypted Example: True.
        screen_lock_explanation (Union[Unset, CreateDeviceRequestPublicDtoScreenLockExplanation]): Any additional
            information to explain the screenLockTime value Example: ScreenLock delay is immediate.
        screen_lock_time (Union[Unset, float]): Amount of time before display is turned off Example: 15.
        windows_services (Union[Unset, list['WindowsServiceRequestPublicDto']]): List of applicable Windows services
    """

    personnel_id: float
    platform_name: CreateDeviceRequestPublicDtoPlatformName
    platform_version: str
    alias: Union[Unset, str] = UNSET
    antivirus_enabled: Union[None, Unset, bool] = UNSET
    antivirus_explanation: Union[Unset, "CreateDeviceRequestPublicDtoAntivirusExplanation"] = UNSET
    app_list: Union[Unset, list["AppTypeRequestPublicDto"]] = UNSET
    auto_update_enabled: Union[None, Unset, bool] = UNSET
    auto_update_explanation: Union[Unset, "CreateDeviceRequestPublicDtoAutoUpdateExplanation"] = UNSET
    browser_extensions: Union[Unset, list["AppTypeRequestPublicDto"]] = UNSET
    external_id: Union[Unset, str] = UNSET
    firewall_enabled: Union[None, Unset, bool] = UNSET
    firewall_explanation: Union[Unset, "CreateDeviceRequestPublicDtoFirewallExplanation"] = UNSET
    password_manager_enabled: Union[None, Unset, bool] = UNSET
    encryption_enabled: Union[None, Unset, bool] = UNSET
    encryption_explanation: Union[Unset, "CreateDeviceRequestPublicDtoEncryptionExplanation"] = UNSET
    model: Union[Unset, str] = UNSET
    serial_number: Union[Unset, str] = UNSET
    mac_address: Union[None, Unset, str] = UNSET
    password_manager_explanation: Union[Unset, "CreateDeviceRequestPublicDtoPasswordManagerExplanation"] = UNSET
    screen_lock_enabled: Union[None, Unset, bool] = UNSET
    screen_lock_explanation: Union[Unset, "CreateDeviceRequestPublicDtoScreenLockExplanation"] = UNSET
    screen_lock_time: Union[Unset, float] = UNSET
    windows_services: Union[Unset, list["WindowsServiceRequestPublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        personnel_id = self.personnel_id

        platform_name = self.platform_name.value

        platform_version = self.platform_version

        alias = self.alias

        antivirus_enabled: Union[None, Unset, bool]
        if isinstance(self.antivirus_enabled, Unset):
            antivirus_enabled = UNSET
        else:
            antivirus_enabled = self.antivirus_enabled

        antivirus_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.antivirus_explanation, Unset):
            antivirus_explanation = self.antivirus_explanation.to_dict()

        app_list: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.app_list, Unset):
            app_list = []
            for app_list_item_data in self.app_list:
                app_list_item = app_list_item_data.to_dict()
                app_list.append(app_list_item)

        auto_update_enabled: Union[None, Unset, bool]
        if isinstance(self.auto_update_enabled, Unset):
            auto_update_enabled = UNSET
        else:
            auto_update_enabled = self.auto_update_enabled

        auto_update_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.auto_update_explanation, Unset):
            auto_update_explanation = self.auto_update_explanation.to_dict()

        browser_extensions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.browser_extensions, Unset):
            browser_extensions = []
            for browser_extensions_item_data in self.browser_extensions:
                browser_extensions_item = browser_extensions_item_data.to_dict()
                browser_extensions.append(browser_extensions_item)

        external_id = self.external_id

        firewall_enabled: Union[None, Unset, bool]
        if isinstance(self.firewall_enabled, Unset):
            firewall_enabled = UNSET
        else:
            firewall_enabled = self.firewall_enabled

        firewall_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.firewall_explanation, Unset):
            firewall_explanation = self.firewall_explanation.to_dict()

        password_manager_enabled: Union[None, Unset, bool]
        if isinstance(self.password_manager_enabled, Unset):
            password_manager_enabled = UNSET
        else:
            password_manager_enabled = self.password_manager_enabled

        encryption_enabled: Union[None, Unset, bool]
        if isinstance(self.encryption_enabled, Unset):
            encryption_enabled = UNSET
        else:
            encryption_enabled = self.encryption_enabled

        encryption_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.encryption_explanation, Unset):
            encryption_explanation = self.encryption_explanation.to_dict()

        model = self.model

        serial_number = self.serial_number

        mac_address: Union[None, Unset, str]
        if isinstance(self.mac_address, Unset):
            mac_address = UNSET
        else:
            mac_address = self.mac_address

        password_manager_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.password_manager_explanation, Unset):
            password_manager_explanation = self.password_manager_explanation.to_dict()

        screen_lock_enabled: Union[None, Unset, bool]
        if isinstance(self.screen_lock_enabled, Unset):
            screen_lock_enabled = UNSET
        else:
            screen_lock_enabled = self.screen_lock_enabled

        screen_lock_explanation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.screen_lock_explanation, Unset):
            screen_lock_explanation = self.screen_lock_explanation.to_dict()

        screen_lock_time = self.screen_lock_time

        windows_services: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.windows_services, Unset):
            windows_services = []
            for windows_services_item_data in self.windows_services:
                windows_services_item = windows_services_item_data.to_dict()
                windows_services.append(windows_services_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "personnelId": personnel_id,
                "platformName": platform_name,
                "platformVersion": platform_version,
            }
        )
        if alias is not UNSET:
            field_dict["alias"] = alias
        if antivirus_enabled is not UNSET:
            field_dict["antivirusEnabled"] = antivirus_enabled
        if antivirus_explanation is not UNSET:
            field_dict["antivirusExplanation"] = antivirus_explanation
        if app_list is not UNSET:
            field_dict["appList"] = app_list
        if auto_update_enabled is not UNSET:
            field_dict["autoUpdateEnabled"] = auto_update_enabled
        if auto_update_explanation is not UNSET:
            field_dict["autoUpdateExplanation"] = auto_update_explanation
        if browser_extensions is not UNSET:
            field_dict["browserExtensions"] = browser_extensions
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if firewall_enabled is not UNSET:
            field_dict["firewallEnabled"] = firewall_enabled
        if firewall_explanation is not UNSET:
            field_dict["firewallExplanation"] = firewall_explanation
        if password_manager_enabled is not UNSET:
            field_dict["passwordManagerEnabled"] = password_manager_enabled
        if encryption_enabled is not UNSET:
            field_dict["encryptionEnabled"] = encryption_enabled
        if encryption_explanation is not UNSET:
            field_dict["encryptionExplanation"] = encryption_explanation
        if model is not UNSET:
            field_dict["model"] = model
        if serial_number is not UNSET:
            field_dict["serialNumber"] = serial_number
        if mac_address is not UNSET:
            field_dict["macAddress"] = mac_address
        if password_manager_explanation is not UNSET:
            field_dict["passwordManagerExplanation"] = password_manager_explanation
        if screen_lock_enabled is not UNSET:
            field_dict["screenLockEnabled"] = screen_lock_enabled
        if screen_lock_explanation is not UNSET:
            field_dict["screenLockExplanation"] = screen_lock_explanation
        if screen_lock_time is not UNSET:
            field_dict["screenLockTime"] = screen_lock_time
        if windows_services is not UNSET:
            field_dict["windowsServices"] = windows_services

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.app_type_request_public_dto import AppTypeRequestPublicDto
        from ..models.create_device_request_public_dto_antivirus_explanation import (
            CreateDeviceRequestPublicDtoAntivirusExplanation,
        )
        from ..models.create_device_request_public_dto_auto_update_explanation import (
            CreateDeviceRequestPublicDtoAutoUpdateExplanation,
        )
        from ..models.create_device_request_public_dto_encryption_explanation import (
            CreateDeviceRequestPublicDtoEncryptionExplanation,
        )
        from ..models.create_device_request_public_dto_firewall_explanation import (
            CreateDeviceRequestPublicDtoFirewallExplanation,
        )
        from ..models.create_device_request_public_dto_password_manager_explanation import (
            CreateDeviceRequestPublicDtoPasswordManagerExplanation,
        )
        from ..models.create_device_request_public_dto_screen_lock_explanation import (
            CreateDeviceRequestPublicDtoScreenLockExplanation,
        )
        from ..models.windows_service_request_public_dto import WindowsServiceRequestPublicDto

        d = dict(src_dict)
        personnel_id = d.pop("personnelId")

        platform_name = CreateDeviceRequestPublicDtoPlatformName(d.pop("platformName"))

        platform_version = d.pop("platformVersion")

        alias = d.pop("alias", UNSET)

        def _parse_antivirus_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        antivirus_enabled = _parse_antivirus_enabled(d.pop("antivirusEnabled", UNSET))

        _antivirus_explanation = d.pop("antivirusExplanation", UNSET)
        antivirus_explanation: Union[Unset, CreateDeviceRequestPublicDtoAntivirusExplanation]
        if isinstance(_antivirus_explanation, Unset):
            antivirus_explanation = UNSET
        else:
            antivirus_explanation = CreateDeviceRequestPublicDtoAntivirusExplanation.from_dict(_antivirus_explanation)

        app_list = []
        _app_list = d.pop("appList", UNSET)
        for app_list_item_data in _app_list or []:
            app_list_item = AppTypeRequestPublicDto.from_dict(app_list_item_data)

            app_list.append(app_list_item)

        def _parse_auto_update_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        auto_update_enabled = _parse_auto_update_enabled(d.pop("autoUpdateEnabled", UNSET))

        _auto_update_explanation = d.pop("autoUpdateExplanation", UNSET)
        auto_update_explanation: Union[Unset, CreateDeviceRequestPublicDtoAutoUpdateExplanation]
        if isinstance(_auto_update_explanation, Unset):
            auto_update_explanation = UNSET
        else:
            auto_update_explanation = CreateDeviceRequestPublicDtoAutoUpdateExplanation.from_dict(
                _auto_update_explanation
            )

        browser_extensions = []
        _browser_extensions = d.pop("browserExtensions", UNSET)
        for browser_extensions_item_data in _browser_extensions or []:
            browser_extensions_item = AppTypeRequestPublicDto.from_dict(browser_extensions_item_data)

            browser_extensions.append(browser_extensions_item)

        external_id = d.pop("externalId", UNSET)

        def _parse_firewall_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        firewall_enabled = _parse_firewall_enabled(d.pop("firewallEnabled", UNSET))

        _firewall_explanation = d.pop("firewallExplanation", UNSET)
        firewall_explanation: Union[Unset, CreateDeviceRequestPublicDtoFirewallExplanation]
        if isinstance(_firewall_explanation, Unset):
            firewall_explanation = UNSET
        else:
            firewall_explanation = CreateDeviceRequestPublicDtoFirewallExplanation.from_dict(_firewall_explanation)

        def _parse_password_manager_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        password_manager_enabled = _parse_password_manager_enabled(d.pop("passwordManagerEnabled", UNSET))

        def _parse_encryption_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        encryption_enabled = _parse_encryption_enabled(d.pop("encryptionEnabled", UNSET))

        _encryption_explanation = d.pop("encryptionExplanation", UNSET)
        encryption_explanation: Union[Unset, CreateDeviceRequestPublicDtoEncryptionExplanation]
        if isinstance(_encryption_explanation, Unset):
            encryption_explanation = UNSET
        else:
            encryption_explanation = CreateDeviceRequestPublicDtoEncryptionExplanation.from_dict(
                _encryption_explanation
            )

        model = d.pop("model", UNSET)

        serial_number = d.pop("serialNumber", UNSET)

        def _parse_mac_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mac_address = _parse_mac_address(d.pop("macAddress", UNSET))

        _password_manager_explanation = d.pop("passwordManagerExplanation", UNSET)
        password_manager_explanation: Union[Unset, CreateDeviceRequestPublicDtoPasswordManagerExplanation]
        if isinstance(_password_manager_explanation, Unset):
            password_manager_explanation = UNSET
        else:
            password_manager_explanation = CreateDeviceRequestPublicDtoPasswordManagerExplanation.from_dict(
                _password_manager_explanation
            )

        def _parse_screen_lock_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        screen_lock_enabled = _parse_screen_lock_enabled(d.pop("screenLockEnabled", UNSET))

        _screen_lock_explanation = d.pop("screenLockExplanation", UNSET)
        screen_lock_explanation: Union[Unset, CreateDeviceRequestPublicDtoScreenLockExplanation]
        if isinstance(_screen_lock_explanation, Unset):
            screen_lock_explanation = UNSET
        else:
            screen_lock_explanation = CreateDeviceRequestPublicDtoScreenLockExplanation.from_dict(
                _screen_lock_explanation
            )

        screen_lock_time = d.pop("screenLockTime", UNSET)

        windows_services = []
        _windows_services = d.pop("windowsServices", UNSET)
        for windows_services_item_data in _windows_services or []:
            windows_services_item = WindowsServiceRequestPublicDto.from_dict(windows_services_item_data)

            windows_services.append(windows_services_item)

        create_device_request_public_dto = cls(
            personnel_id=personnel_id,
            platform_name=platform_name,
            platform_version=platform_version,
            alias=alias,
            antivirus_enabled=antivirus_enabled,
            antivirus_explanation=antivirus_explanation,
            app_list=app_list,
            auto_update_enabled=auto_update_enabled,
            auto_update_explanation=auto_update_explanation,
            browser_extensions=browser_extensions,
            external_id=external_id,
            firewall_enabled=firewall_enabled,
            firewall_explanation=firewall_explanation,
            password_manager_enabled=password_manager_enabled,
            encryption_enabled=encryption_enabled,
            encryption_explanation=encryption_explanation,
            model=model,
            serial_number=serial_number,
            mac_address=mac_address,
            password_manager_explanation=password_manager_explanation,
            screen_lock_enabled=screen_lock_enabled,
            screen_lock_explanation=screen_lock_explanation,
            screen_lock_time=screen_lock_time,
            windows_services=windows_services,
        )

        create_device_request_public_dto.additional_properties = d
        return create_device_request_public_dto

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
