from enum import Enum


class FrameworksPublicControllerGetAllRequirementsLevel(str, Enum):
    ADVANCED = "ADVANCED"
    BASELINE = "BASELINE"
    EVOLVING = "EVOLVING"
    INNOVATIVE = "INNOVATIVE"
    INTERMEDIATE = "INTERMEDIATE"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    SECURITY_HIGH = "SECURITY_HIGH"
    SECURITY_LOW = "SECURITY_LOW"
    SECURITY_MODERATE = "SECURITY_MODERATE"
    SIMPLIFIED = "SIMPLIFIED"
    STANDARD = "STANDARD"

    def __str__(self) -> str:
        return str(self.value)
