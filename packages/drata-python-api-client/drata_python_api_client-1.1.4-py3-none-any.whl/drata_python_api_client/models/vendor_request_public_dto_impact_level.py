from enum import Enum


class VendorRequestPublicDtoImpactLevel(str, Enum):
    CRITICAL = "CRITICAL"
    INSIGNIFICANT = "INSIGNIFICANT"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    UNSCORED = "UNSCORED"

    def __str__(self) -> str:
        return str(self.value)
