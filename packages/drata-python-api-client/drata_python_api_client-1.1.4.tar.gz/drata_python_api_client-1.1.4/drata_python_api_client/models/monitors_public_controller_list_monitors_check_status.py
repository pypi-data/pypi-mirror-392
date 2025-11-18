from enum import Enum


class MonitorsPublicControllerListMonitorsCheckStatus(str, Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    NEW = "NEW"
    TESTING = "TESTING"
    UNUSED = "UNUSED"

    def __str__(self) -> str:
        return str(self.value)
