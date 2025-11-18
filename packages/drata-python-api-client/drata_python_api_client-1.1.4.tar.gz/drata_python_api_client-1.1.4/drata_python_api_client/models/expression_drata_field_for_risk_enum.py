from enum import Enum


class ExpressionDrataFieldForRiskEnum(str, Enum):
    INHERENT_IMPACT = "INHERENT_IMPACT"
    INHERENT_LIKELIHOOD = "INHERENT_LIKELIHOOD"
    RESIDUAL_IMPACT = "RESIDUAL_IMPACT"
    RESIDUAL_LIKELIHOOD = "RESIDUAL_LIKELIHOOD"

    def __str__(self) -> str:
        return str(self.value)
