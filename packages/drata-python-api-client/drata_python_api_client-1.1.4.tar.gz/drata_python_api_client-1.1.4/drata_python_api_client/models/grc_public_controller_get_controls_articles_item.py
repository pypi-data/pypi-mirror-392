from enum import Enum


class GRCPublicControllerGetControlsArticlesItem(str, Enum):
    NIS2_GOVERNANCE = "NIS2_GOVERNANCE"
    NIS2_REPORTING = "NIS2_REPORTING"
    NIS2_RISK_MANAGEMENT = "NIS2_RISK_MANAGEMENT"

    def __str__(self) -> str:
        return str(self.value)
