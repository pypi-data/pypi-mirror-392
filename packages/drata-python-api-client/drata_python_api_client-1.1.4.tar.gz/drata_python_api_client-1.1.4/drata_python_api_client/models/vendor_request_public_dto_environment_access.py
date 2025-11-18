from enum import Enum


class VendorRequestPublicDtoEnvironmentAccess(str, Enum):
    NO = "NO"
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"

    def __str__(self) -> str:
        return str(self.value)
