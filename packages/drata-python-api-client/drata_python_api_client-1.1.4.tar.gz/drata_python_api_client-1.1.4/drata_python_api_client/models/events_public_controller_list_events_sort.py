from enum import Enum


class EventsPublicControllerListEventsSort(str, Enum):
    CATEGORY = "CATEGORY"
    CHECK_RESULTS_STATUS = "CHECK_RESULTS_STATUS"
    CREATED = "CREATED"
    DESCRIPTION = "DESCRIPTION"
    TYPE = "TYPE"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
