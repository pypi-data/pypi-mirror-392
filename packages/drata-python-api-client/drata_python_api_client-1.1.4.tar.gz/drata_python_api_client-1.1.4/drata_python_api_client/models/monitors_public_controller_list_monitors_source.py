from enum import Enum


class MonitorsPublicControllerListMonitorsSource(str, Enum):
    ACORN = "ACORN"
    CUSTOM = "CUSTOM"
    DRATA = "DRATA"
    EXTERNAL = "EXTERNAL"

    def __str__(self) -> str:
        return str(self.value)
