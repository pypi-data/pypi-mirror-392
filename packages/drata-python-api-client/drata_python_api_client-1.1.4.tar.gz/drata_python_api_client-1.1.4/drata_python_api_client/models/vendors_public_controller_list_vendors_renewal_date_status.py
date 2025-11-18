from enum import Enum


class VendorsPublicControllerListVendorsRenewalDateStatus(str, Enum):
    COMPLETED = "COMPLETED"
    NO_RENEWAL = "NO_RENEWAL"
    RENEWAL_DUE = "RENEWAL_DUE"
    RENEWAL_DUE_SOON = "RENEWAL_DUE_SOON"

    def __str__(self) -> str:
        return str(self.value)
