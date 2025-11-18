from enum import Enum


class RiskLibraryPublicControllerGetRisksLibraryListSort(str, Enum):
    NAME = "NAME"
    RISK_ID = "RISK_ID"

    def __str__(self) -> str:
        return str(self.value)
