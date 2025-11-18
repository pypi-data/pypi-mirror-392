from enum import Enum


class GRCPublicControllerGetControlsSoxitgcItem(str, Enum):
    SOX_ITGC_ACCESS_MANAGEMENT = "SOX_ITGC_ACCESS_MANAGEMENT"
    SOX_ITGC_CHANGE_MANAGEMENT = "SOX_ITGC_CHANGE_MANAGEMENT"
    SOX_ITGC_PROGRAM_DEVELOPMENT = "SOX_ITGC_PROGRAM_DEVELOPMENT"
    SOX_ITGC_SYSTEM_OPERATIONS = "SOX_ITGC_SYSTEM_OPERATIONS"

    def __str__(self) -> str:
        return str(self.value)
