from enum import Enum


class GRCPublicControllerGetControlsControlBaselinesItem(str, Enum):
    NISTSP80053_MANAGEMENT = "NISTSP80053_MANAGEMENT"
    NISTSP80053_OPERATIONAL = "NISTSP80053_OPERATIONAL"
    NISTSP80053_TECHNICAL = "NISTSP80053_TECHNICAL"

    def __str__(self) -> str:
        return str(self.value)
