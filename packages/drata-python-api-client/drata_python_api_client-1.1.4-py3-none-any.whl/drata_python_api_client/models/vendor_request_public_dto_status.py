from enum import Enum


class VendorRequestPublicDtoStatus(str, Enum):
    ACTIVE = "ACTIVE"
    APPROVED = "APPROVED"
    ARCHIVED = "ARCHIVED"
    FLAGGED = "FLAGGED"
    NONE = "NONE"
    OFFBOARDED = "OFFBOARDED"
    ON_HOLD = "ON_HOLD"
    PROSPECTIVE = "PROSPECTIVE"
    REJECTED = "REJECTED"
    UNDER_REVIEW = "UNDER_REVIEW"

    def __str__(self) -> str:
        return str(self.value)
