from enum import Enum


class CopyRisksFromLibraryRequestPublicDtoBulkActionType(str, Enum):
    COPY_BY_GROUPS = "COPY_BY_GROUPS"
    COPY_BY_IDS = "COPY_BY_IDS"

    def __str__(self) -> str:
        return str(self.value)
