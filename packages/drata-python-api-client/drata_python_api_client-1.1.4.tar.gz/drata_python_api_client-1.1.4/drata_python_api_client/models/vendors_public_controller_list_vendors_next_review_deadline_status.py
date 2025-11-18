from enum import Enum


class VendorsPublicControllerListVendorsNextReviewDeadlineStatus(str, Enum):
    DUE_SOON = "DUE_SOON"
    NO_RENEWAL = "NO_RENEWAL"
    OVERDUE = "OVERDUE"

    def __str__(self) -> str:
        return str(self.value)
