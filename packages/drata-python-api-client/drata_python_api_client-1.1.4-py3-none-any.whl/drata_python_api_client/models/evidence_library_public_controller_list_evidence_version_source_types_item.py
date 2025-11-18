from enum import Enum


class EvidenceLibraryPublicControllerListEvidenceVersionSourceTypesItem(str, Enum):
    FILE = "FILE"
    TEST = "TEST"
    TICKET = "TICKET"
    URL = "URL"

    def __str__(self) -> str:
        return str(self.value)
