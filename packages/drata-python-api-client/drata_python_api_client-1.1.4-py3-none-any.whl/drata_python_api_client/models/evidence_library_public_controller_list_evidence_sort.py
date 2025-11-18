from enum import Enum


class EvidenceLibraryPublicControllerListEvidenceSort(str, Enum):
    CREATED_AT = "CREATED_AT"
    DATE = "DATE"
    DESCRIPTION = "DESCRIPTION"
    EVIDENCE_TYPE = "EVIDENCE_TYPE"
    NAME = "NAME"
    RENEWAL_DATE = "RENEWAL_DATE"
    STATUS = "STATUS"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
