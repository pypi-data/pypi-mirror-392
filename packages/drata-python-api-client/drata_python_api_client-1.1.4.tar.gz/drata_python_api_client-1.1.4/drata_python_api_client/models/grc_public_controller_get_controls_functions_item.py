from enum import Enum


class GRCPublicControllerGetControlsFunctionsItem(str, Enum):
    NISTCSF_DETECT = "NISTCSF_DETECT"
    NISTCSF_IDENTIFY = "NISTCSF_IDENTIFY"
    NISTCSF_PROTECT = "NISTCSF_PROTECT"
    NISTCSF_RECOVER = "NISTCSF_RECOVER"
    NISTCSF_RESPOND = "NISTCSF_RESPOND"

    def __str__(self) -> str:
        return str(self.value)
