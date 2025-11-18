from enum import Enum


class VendorsPublicControllerListVendorsScheduledQuestionnaireStatus(str, Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"

    def __str__(self) -> str:
        return str(self.value)
