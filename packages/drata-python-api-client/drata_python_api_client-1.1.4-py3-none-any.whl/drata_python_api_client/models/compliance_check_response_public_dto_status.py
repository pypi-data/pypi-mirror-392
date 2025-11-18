from enum import Enum


class ComplianceCheckResponsePublicDtoStatus(str, Enum):
    EXCLUDED = "EXCLUDED"
    FAIL = "FAIL"
    MISCONFIGURED = "MISCONFIGURED"
    PASS = "PASS"

    def __str__(self) -> str:
        return str(self.value)
