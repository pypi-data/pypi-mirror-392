from enum import Enum


class VendorsPublicControllerListVendorsPasswordPolicy(str, Enum):
    LDAP = "LDAP"
    NONE = "NONE"
    SSO = "SSO"
    USERNAME_PASSWORD = "USERNAME_PASSWORD"

    def __str__(self) -> str:
        return str(self.value)
