from enum import Enum


class GRCPublicControllerGetControlsDoraChaptersItem(str, Enum):
    DORA_ICT_RMF_RTS = "DORA_ICT_RMF_RTS"
    DORA_REGULATION = "DORA_REGULATION"

    def __str__(self) -> str:
        return str(self.value)
