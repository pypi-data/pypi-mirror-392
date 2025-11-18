from enum import Enum


class EvidenceLibraryPublicControllerListEvidenceStatusItem(str, Enum):
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    NEEDS_SOURCE = "NEEDS_SOURCE"
    READY = "READY"

    def __str__(self) -> str:
        return str(self.value)
