from enum import Enum


class VendorReviewResponsePublicDtoReportOpinion(str, Enum):
    ADVERSE = "ADVERSE"
    DISCLAIMER = "DISCLAIMER"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"

    def __str__(self) -> str:
        return str(self.value)
