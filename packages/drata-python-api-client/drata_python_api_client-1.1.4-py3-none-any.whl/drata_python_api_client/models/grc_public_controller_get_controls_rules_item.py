from enum import Enum


class GRCPublicControllerGetControlsRulesItem(str, Enum):
    HIPAA_BREACH_NOTIFICATION = "HIPAA_BREACH_NOTIFICATION"
    HIPAA_PRIVACY = "HIPAA_PRIVACY"
    HIPAA_SECURITY = "HIPAA_SECURITY"

    def __str__(self) -> str:
        return str(self.value)
