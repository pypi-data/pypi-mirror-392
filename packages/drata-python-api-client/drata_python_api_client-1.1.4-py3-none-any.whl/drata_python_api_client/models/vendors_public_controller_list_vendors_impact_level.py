from enum import Enum


class VendorsPublicControllerListVendorsImpactLevel(str, Enum):
    CRITICAL = "CRITICAL"
    INSIGNIFICANT = "INSIGNIFICANT"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    UNSCORED = "UNSCORED"

    def __str__(self) -> str:
        return str(self.value)
