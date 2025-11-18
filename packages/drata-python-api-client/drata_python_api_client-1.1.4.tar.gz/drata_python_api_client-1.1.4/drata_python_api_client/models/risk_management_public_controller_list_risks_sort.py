from enum import Enum


class RiskManagementPublicControllerListRisksSort(str, Enum):
    ID = "ID"
    IDENTIFIED_DATE = "IDENTIFIED_DATE"
    RISK_SCORE = "RISK_SCORE"

    def __str__(self) -> str:
        return str(self.value)
