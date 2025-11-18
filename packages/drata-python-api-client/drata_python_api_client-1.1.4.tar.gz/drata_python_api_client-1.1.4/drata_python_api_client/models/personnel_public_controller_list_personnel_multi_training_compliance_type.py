from enum import Enum


class PersonnelPublicControllerListPersonnelMultiTrainingComplianceType(str, Enum):
    HIPAA_TRAINING = "HIPAA_TRAINING"
    NIST_AI_TRAINING = "NIST_AI_TRAINING"
    SECURITY_TRAINING = "SECURITY_TRAINING"

    def __str__(self) -> str:
        return str(self.value)
