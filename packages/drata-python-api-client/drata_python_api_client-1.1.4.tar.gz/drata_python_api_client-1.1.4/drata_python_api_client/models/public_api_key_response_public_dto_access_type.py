from enum import Enum


class PublicApiKeyResponsePublicDtoAccessType(str, Enum):
    ALL_READ = "ALL_READ"
    ALL_READ_AND_WRITE = "ALL_READ_AND_WRITE"

    def __str__(self) -> str:
        return str(self.value)
