from enum import Enum


class CreateDeviceRequestPublicDtoPlatformName(str, Enum):
    ANDROID = "ANDROID"
    LINUX = "LINUX"
    MACOS = "MACOS"
    UNIX = "UNIX"
    WINDOWS = "WINDOWS"

    def __str__(self) -> str:
        return str(self.value)
