from enum import Enum


class MonitorsPublicControllerListMonitorsReportInterval(str, Enum):
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"

    def __str__(self) -> str:
        return str(self.value)
