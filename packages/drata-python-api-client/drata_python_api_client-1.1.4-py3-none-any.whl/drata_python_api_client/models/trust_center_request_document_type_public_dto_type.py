from enum import Enum


class TrustCenterRequestDocumentTypePublicDtoType(str, Enum):
    COMPLIANCE = "COMPLIANCE"
    POLICY = "POLICY"
    SECURITY_REPORT = "SECURITY_REPORT"

    def __str__(self) -> str:
        return str(self.value)
