from enum import Enum


class RiskManagementPublicControllerGetDashboardStatusItem(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    CLOSED = "CLOSED"

    def __str__(self) -> str:
        return str(self.value)
