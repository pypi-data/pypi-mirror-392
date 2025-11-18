from enum import Enum


class GRCPublicControllerGetControlsCmmcClassesItem(str, Enum):
    CMMC_MANAGEMENT = "CMMC_MANAGEMENT"
    CMMC_OPERATIONAL = "CMMC_OPERATIONAL"
    CMMC_TECHNICAL = "CMMC_TECHNICAL"

    def __str__(self) -> str:
        return str(self.value)
