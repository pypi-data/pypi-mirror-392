from enum import Enum


class TrustCenterRequestRequestPublicDtoFlowType(str, Enum):
    DIGITAL_SIGNATURE = "DIGITAL_SIGNATURE"
    NO_NDA_REQUIRED = "NO_NDA_REQUIRED"
    SALESFORCE_CRM = "SALESFORCE_CRM"
    SELF = "SELF"

    def __str__(self) -> str:
        return str(self.value)
