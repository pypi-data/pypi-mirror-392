from enum import Enum


class GRCPublicControllerGetControlsNist800171R3ControlClassesItem(str, Enum):
    NIST800171R3_MANAGEMENT = "NIST800171R3_MANAGEMENT"
    NIST800171R3_OPERATIONAL = "NIST800171R3_OPERATIONAL"
    NIST800171R3_TECHNICAL = "NIST800171R3_TECHNICAL"

    def __str__(self) -> str:
        return str(self.value)
