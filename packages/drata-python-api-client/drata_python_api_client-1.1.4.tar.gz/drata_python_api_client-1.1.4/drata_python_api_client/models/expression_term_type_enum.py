from enum import Enum


class ExpressionTermTypeEnum(str, Enum):
    CONSTANT = "CONSTANT"
    CUSTOM_FIELD = "CUSTOM_FIELD"
    DRATA_FIELD = "DRATA_FIELD"
    OPERATOR = "OPERATOR"

    def __str__(self) -> str:
        return str(self.value)
