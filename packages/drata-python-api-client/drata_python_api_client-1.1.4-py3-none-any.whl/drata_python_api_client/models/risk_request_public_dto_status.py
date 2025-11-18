from enum import Enum


class RiskRequestPublicDtoStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    CLOSED = "CLOSED"

    def __str__(self) -> str:
        return str(self.value)
