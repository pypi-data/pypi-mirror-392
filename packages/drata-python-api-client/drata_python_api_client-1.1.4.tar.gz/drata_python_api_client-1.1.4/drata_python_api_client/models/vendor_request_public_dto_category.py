from enum import Enum


class VendorRequestPublicDtoCategory(str, Enum):
    ADMINISTRATIVE = "ADMINISTRATIVE"
    CS = "CS"
    ENGINEERING = "ENGINEERING"
    FINANCE = "FINANCE"
    HR = "HR"
    INFORMATION_TECHNOLOGY = "INFORMATION_TECHNOLOGY"
    LEGAL = "LEGAL"
    MARKETING = "MARKETING"
    NONE = "NONE"
    PRODUCT = "PRODUCT"
    SALES = "SALES"
    SECURITY = "SECURITY"

    def __str__(self) -> str:
        return str(self.value)
