from enum import Enum


class VendorRequestPublicDtoOperationalImpact(str, Enum):
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    LOW = "LOW"
    NONE = "NONE"
    NORMAL = "NORMAL"

    def __str__(self) -> str:
        return str(self.value)
