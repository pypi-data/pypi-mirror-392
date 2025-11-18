from enum import Enum


class GRCPublicControllerGetControlsHasTicket(str, Enum):
    ARCHIVED = "ARCHIVED"
    IN_PROGRESS = "IN_PROGRESS"

    def __str__(self) -> str:
        return str(self.value)
