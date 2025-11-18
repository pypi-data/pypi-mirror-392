from enum import Enum


class TrustCenterApproveRequestRequestPublicDtoExpirationType(str, Enum):
    DAYS = "DAYS"
    MONTHS = "MONTHS"
    WEEKS = "WEEKS"
    YEARS = "YEARS"

    def __str__(self) -> str:
        return str(self.value)
