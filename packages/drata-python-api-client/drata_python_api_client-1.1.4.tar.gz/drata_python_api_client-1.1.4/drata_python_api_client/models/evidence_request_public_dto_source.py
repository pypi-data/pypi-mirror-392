from enum import Enum


class EvidenceRequestPublicDtoSource(str, Enum):
    BOX = "BOX"
    DROPBOX = "DROPBOX"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    NONE = "NONE"
    ONE_DRIVE = "ONE_DRIVE"
    S3_FILE = "S3_FILE"
    SHARE_POINT = "SHARE_POINT"
    TEST_RESULT = "TEST_RESULT"
    TICKET_PROVIDER = "TICKET_PROVIDER"
    URL = "URL"

    def __str__(self) -> str:
        return str(self.value)
