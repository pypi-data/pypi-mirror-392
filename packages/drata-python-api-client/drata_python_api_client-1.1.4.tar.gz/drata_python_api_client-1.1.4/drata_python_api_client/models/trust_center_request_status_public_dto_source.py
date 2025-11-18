from enum import Enum


class TrustCenterRequestStatusPublicDtoSource(str, Enum):
    DOCUSIGN = "DOCUSIGN"
    SALESFORCE = "SALESFORCE"
    SELF = "SELF"

    def __str__(self) -> str:
        return str(self.value)
