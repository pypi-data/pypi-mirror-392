from enum import Enum


class RiskManagementPublicControllerListRisksTreatmentPlan(str, Enum):
    ACCEPT = "ACCEPT"
    AVOID = "AVOID"
    MITIGATE = "MITIGATE"
    TRANSFER = "TRANSFER"
    UNTREATED = "UNTREATED"

    def __str__(self) -> str:
        return str(self.value)
