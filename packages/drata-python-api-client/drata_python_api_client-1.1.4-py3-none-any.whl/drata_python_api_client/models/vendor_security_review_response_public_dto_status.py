from enum import Enum


class VendorSecurityReviewResponsePublicDtoStatus(str, Enum):
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_REQUIRED = "NOT_REQUIRED"
    NOT_YET_STARTED = "NOT_YET_STARTED"

    def __str__(self) -> str:
        return str(self.value)
