from enum import Enum


class ComplianceCheckResponsePublicDtoCheckFrequency(str, Enum):
    BIWEEKLY = "BIWEEKLY"
    DAILY = "DAILY"
    HOURLY = "HOURLY"
    MONTHLY = "MONTHLY"
    ONCE = "ONCE"
    QID = "QID"
    QUARTERLY = "QUARTERLY"
    WEEKLY = "WEEKLY"
    YEARLY = "YEARLY"

    def __str__(self) -> str:
        return str(self.value)
