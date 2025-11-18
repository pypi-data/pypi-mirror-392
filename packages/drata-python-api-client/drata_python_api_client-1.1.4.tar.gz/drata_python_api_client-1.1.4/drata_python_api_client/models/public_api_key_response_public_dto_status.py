from enum import Enum


class PublicApiKeyResponsePublicDtoStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    EXPIRES_SOON = "EXPIRES_SOON"
    REVOKED = "REVOKED"

    def __str__(self) -> str:
        return str(self.value)
