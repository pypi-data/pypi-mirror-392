from enum import Enum


class UserDocumentRequestPublicDtoType(str, Enum):
    HIPAA_TRAINING_EVIDENCE = "HIPAA_TRAINING_EVIDENCE"
    MFA_EVIDENCE = "MFA_EVIDENCE"
    OFFBOARDING_EVIDENCE = "OFFBOARDING_EVIDENCE"
    SEC_TRAINING = "SEC_TRAINING"

    def __str__(self) -> str:
        return str(self.value)
