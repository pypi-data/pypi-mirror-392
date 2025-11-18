from enum import Enum


class DevicePublicControllerGetDevicesSourceType(str, Enum):
    AGENT = "AGENT"
    CUSTOM = "CUSTOM"
    HEXNODE_UEM = "HEXNODE_UEM"
    INTUNE = "INTUNE"
    INTUNE_GCC_HIGH = "INTUNE_GCC_HIGH"
    JAMF = "JAMF"
    JUMPCLOUD = "JUMPCLOUD"
    KANDJI = "KANDJI"
    KOLIDE = "KOLIDE"
    RIPPLING = "RIPPLING"
    UNKNOWN = "UNKNOWN"
    WORKSPACE_ONE = "WORKSPACE_ONE"

    def __str__(self) -> str:
        return str(self.value)
