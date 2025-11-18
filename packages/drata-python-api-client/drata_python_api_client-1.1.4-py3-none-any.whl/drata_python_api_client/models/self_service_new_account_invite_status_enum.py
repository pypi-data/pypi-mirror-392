from enum import Enum


class SelfServiceNewAccountInviteStatusEnum(str, Enum):
    CREATED = "CREATED"
    EXPIRED = "EXPIRED"
    INVITED = "INVITED"
    INVITE_CREATED = "INVITE_CREATED"
    REVOKED = "REVOKED"

    def __str__(self) -> str:
        return str(self.value)
