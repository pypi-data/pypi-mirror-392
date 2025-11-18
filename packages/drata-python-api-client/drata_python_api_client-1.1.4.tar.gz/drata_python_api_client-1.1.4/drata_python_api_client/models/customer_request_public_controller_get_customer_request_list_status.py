from enum import Enum


class CustomerRequestPublicControllerGetCustomerRequestListStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    IN_REVIEW = "IN_REVIEW"
    OUTSTANDING = "OUTSTANDING"

    def __str__(self) -> str:
        return str(self.value)
