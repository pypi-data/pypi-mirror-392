from enum import Enum


class TrustCenterRequestStatusPublicDtoStatus(str, Enum):
    ACCESS_EXPIRED = "ACCESS_EXPIRED"
    APPROVED = "APPROVED"
    AUTO_APPROVED = "AUTO_APPROVED"
    DENIED = "DENIED"
    FILES_SENT = "FILES_SENT"
    NDA_EXPIRED = "NDA_EXPIRED"
    NDA_SENT = "NDA_SENT"
    NDA_SIGNED = "NDA_SIGNED"
    PENDING = "PENDING"
    PROCESS_ERROR = "PROCESS_ERROR"
    REVOKED = "REVOKED"

    def __str__(self) -> str:
        return str(self.value)
