from enum import Enum


class RiskManagementPublicControllerGetDashboardRiskFilter(str, Enum):
    CUSTOM_ONLY = "CUSTOM_ONLY"
    EXTERNAL_ONLY = "EXTERNAL_ONLY"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"

    def __str__(self) -> str:
        return str(self.value)
