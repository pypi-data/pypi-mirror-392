from enum import Enum


class PolicyVersionResponsePublicDtoStatus(str, Enum):
    APPROVED = "APPROVED"
    DISCARDED = "DISCARDED"
    DRAFT = "DRAFT"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    PUBLISHED = "PUBLISHED"

    def __str__(self) -> str:
        return str(self.value)
