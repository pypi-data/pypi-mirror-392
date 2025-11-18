from enum import Enum


class VendorsPublicControllerListVendorsSecurityReviewStatus(str, Enum):
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NO_PAST_REVIEW = "NO_PAST_REVIEW"
    NO_SECURITY = "NO_SECURITY"
    UP_TO_DATE = "UP_TO_DATE"

    def __str__(self) -> str:
        return str(self.value)
