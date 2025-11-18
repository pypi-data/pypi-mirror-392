from enum import Enum


class VendorsPublicControllerListVendorsSort(str, Enum):
    CATEGORY = "CATEGORY"
    IMPACT_LEVEL = "IMPACT_LEVEL"
    NAME = "NAME"
    POLICY = "POLICY"
    RISK = "RISK"
    STATUS = "STATUS"
    TYPE = "TYPE"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
