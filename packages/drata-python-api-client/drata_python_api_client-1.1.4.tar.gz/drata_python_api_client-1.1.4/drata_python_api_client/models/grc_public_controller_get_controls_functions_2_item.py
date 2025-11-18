from enum import Enum


class GRCPublicControllerGetControlsFunctions2Item(str, Enum):
    NISTCSF2_DETECT_DE = "NISTCSF2_DETECT_DE"
    NISTCSF2_GOVERN_GV = "NISTCSF2_GOVERN_GV"
    NISTCSF2_IDENTIFY_ID = "NISTCSF2_IDENTIFY_ID"
    NISTCSF2_PROTECT_PR = "NISTCSF2_PROTECT_PR"
    NISTCSF2_RECOVER_RC = "NISTCSF2_RECOVER_RC"
    NISTCSF2_RESPOND_RS = "NISTCSF2_RESPOND_RS"

    def __str__(self) -> str:
        return str(self.value)
