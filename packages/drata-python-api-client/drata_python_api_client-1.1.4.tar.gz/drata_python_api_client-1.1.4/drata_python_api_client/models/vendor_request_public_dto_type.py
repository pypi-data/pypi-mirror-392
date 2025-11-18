from enum import Enum


class VendorRequestPublicDtoType(str, Enum):
    CONTRACTOR = "CONTRACTOR"
    NONE = "NONE"
    OTHER = "OTHER"
    PARTNER = "PARTNER"
    SUPPLIER = "SUPPLIER"
    VENDOR = "VENDOR"

    def __str__(self) -> str:
        return str(self.value)
