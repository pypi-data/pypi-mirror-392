from enum import Enum


class VendorsPublicControllerGetVendorsStatsExcludeScopesType0Item(str, Enum):
    BUSINESSUNITS = "businessUnits"
    HASPII = "hasPii"
    IMPACTLEVEL = "impactLevel"
    ISCRITICAL = "isCritical"
    PASSWORDPOLICY = "passwordPolicy"
    REMINDER = "reminder"
    RISK = "risk"
    STATUS = "status"
    SUBPROCESSORS = "subprocessors"
    TYPE = "type"

    def __str__(self) -> str:
        return str(self.value)
