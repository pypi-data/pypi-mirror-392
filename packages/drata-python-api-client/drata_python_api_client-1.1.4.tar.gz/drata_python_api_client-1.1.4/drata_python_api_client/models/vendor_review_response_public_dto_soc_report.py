from enum import Enum


class VendorReviewResponsePublicDtoSocReport(str, Enum):
    SOC_1 = "SOC_1"
    SOC_2 = "SOC_2"
    SOC_3 = "SOC_3"

    def __str__(self) -> str:
        return str(self.value)
