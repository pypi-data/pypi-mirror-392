from enum import Enum


class DevicePublicControllerGetDeviceExpandItem(str, Enum):
    ASSET = "ASSET"
    COMPLIANCE_CHECKS = "COMPLIANCE_CHECKS"
    DEVICE_APPS = "DEVICE_APPS"
    DOCUMENTS = "DOCUMENTS"
    IDENTIFIERS = "IDENTIFIERS"

    def __str__(self) -> str:
        return str(self.value)
