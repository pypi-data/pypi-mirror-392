from enum import Enum


class UserIdentityInfrastructureToggleRequestPublicDtoToggleField(str, Enum):
    INFRASTRUCTURE_ADMIN_ACCESS = "INFRASTRUCTURE_ADMIN_ACCESS"
    INFRASTRUCTURE_DB_ACCESS = "INFRASTRUCTURE_DB_ACCESS"

    def __str__(self) -> str:
        return str(self.value)
