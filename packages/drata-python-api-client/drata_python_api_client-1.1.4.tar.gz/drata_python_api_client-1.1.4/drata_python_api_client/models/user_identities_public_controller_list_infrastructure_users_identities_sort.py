from enum import Enum


class UserIdentitiesPublicControllerListInfrastructureUsersIdentitiesSort(str, Enum):
    ADMIN_ACCESS = "ADMIN_ACCESS"
    CLIENT_ALIAS = "CLIENT_ALIAS"
    CLIENT_ID = "CLIENT_ID"
    CONNECTED_AT = "CONNECTED_AT"
    CONNECTION_STATUS = "CONNECTION_STATUS"
    DB_ACCESS = "DB_ACCESS"
    DISCONNECTED_AT = "DISCONNECTED_AT"
    EMAIL = "EMAIL"
    HAS_MFA = "HAS_MFA"
    IDENTITY_ID = "IDENTITY_ID"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    USER = "USER"
    USERNAME = "USERNAME"

    def __str__(self) -> str:
        return str(self.value)
