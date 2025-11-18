from enum import Enum


class EvidenceLibraryRenewalSchemaResponsePublicDtoRenewalScheduleType(str, Enum):
    CUSTOM = "CUSTOM"
    NONE = "NONE"
    ONE_MONTH = "ONE_MONTH"
    ONE_YEAR = "ONE_YEAR"
    SIX_MONTHS = "SIX_MONTHS"
    THREE_MONTHS = "THREE_MONTHS"
    TWO_MONTHS = "TWO_MONTHS"

    def __str__(self) -> str:
        return str(self.value)
