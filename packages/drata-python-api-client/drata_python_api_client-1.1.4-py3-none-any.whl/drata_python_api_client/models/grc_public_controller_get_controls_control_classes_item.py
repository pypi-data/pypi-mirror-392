from enum import Enum


class GRCPublicControllerGetControlsControlClassesItem(str, Enum):
    NIST800171R2_MANAGEMENT = "NIST800171R2_MANAGEMENT"
    NIST800171R2_OPERATIONAL = "NIST800171R2_OPERATIONAL"
    NIST800171R2_TECHNICAL = "NIST800171R2_TECHNICAL"

    def __str__(self) -> str:
        return str(self.value)
