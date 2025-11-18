from enum import Enum


class VendorSecurityReviewRequestPublicDtoSecurityReviewType(str, Enum):
    SECURITY = "SECURITY"
    SOC_REPORT = "SOC_REPORT"
    UPLOAD_REPORT = "UPLOAD_REPORT"

    def __str__(self) -> str:
        return str(self.value)
