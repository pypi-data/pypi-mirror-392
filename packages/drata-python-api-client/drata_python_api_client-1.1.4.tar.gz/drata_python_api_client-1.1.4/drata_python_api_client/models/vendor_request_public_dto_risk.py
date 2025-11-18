from enum import Enum


class VendorRequestPublicDtoRisk(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    MODERATE = "MODERATE"
    NONE = "NONE"

    def __str__(self) -> str:
        return str(self.value)
