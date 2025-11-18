from enum import Enum


class UserIdentityVersionControlToggleRequestPublicDtoToggleField(str, Enum):
    VERSION_CONTROL_PUSH_PROD_CODE_ACCESS = "VERSION_CONTROL_PUSH_PROD_CODE_ACCESS"
    VERSION_CONTROL_WRITE_ACCESS = "VERSION_CONTROL_WRITE_ACCESS"

    def __str__(self) -> str:
        return str(self.value)
