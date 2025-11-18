from enum import Enum


class EventsPublicControllerListEventsSource(str, Enum):
    APP = "APP"
    AUTOPILOT = "AUTOPILOT"
    DRATA_POLICY = "DRATA_POLICY"
    PUBLIC_API = "PUBLIC_API"
    SCHEDULED = "SCHEDULED"
    VENDOR_QUESTIONNAIRE = "VENDOR_QUESTIONNAIRE"
    WORKFLOW = "WORKFLOW"

    def __str__(self) -> str:
        return str(self.value)
