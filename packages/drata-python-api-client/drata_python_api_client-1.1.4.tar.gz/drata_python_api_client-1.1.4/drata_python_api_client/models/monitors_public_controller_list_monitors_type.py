from enum import Enum


class MonitorsPublicControllerListMonitorsType(str, Enum):
    AGENT = "AGENT"
    CUSTOM = "CUSTOM"
    HRIS = "HRIS"
    IDENTITY = "IDENTITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    IN_DRATA = "IN_DRATA"
    OBSERVABILITY = "OBSERVABILITY"
    POLICY = "POLICY"
    TICKETING = "TICKETING"
    VERSION_CONTROL = "VERSION_CONTROL"

    def __str__(self) -> str:
        return str(self.value)
