from enum import Enum


class GRCPublicControllerGetControlsStatutesItem(str, Enum):
    CCPA_INDIVIDUAL_RIGHTS = "CCPA_INDIVIDUAL_RIGHTS"
    CCPA_SECURITY = "CCPA_SECURITY"
    CCPA_SERVICE_PROVIDER = "CCPA_SERVICE_PROVIDER"

    def __str__(self) -> str:
        return str(self.value)
