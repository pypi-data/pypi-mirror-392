from enum import Enum


class UserIdentitiesPublicControllerListUsersIdentitiesVersionControlSort(str, Enum):
    CLIENT_ID = "CLIENT_ID"
    CONNECTED_AT = "CONNECTED_AT"
    CONNECTION_STATUS = "CONNECTION_STATUS"
    DISCONNECTED_AT = "DISCONNECTED_AT"
    EMAIL = "EMAIL"
    HAS_MFA = "HAS_MFA"
    IDENTITY_ID = "IDENTITY_ID"
    PUSH_PROD_CODE_ACCESS = "PUSH_PROD_CODE_ACCESS"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    USER = "USER"
    USERNAME = "USERNAME"
    WRITE_ACCESS = "WRITE_ACCESS"

    def __str__(self) -> str:
        return str(self.value)
