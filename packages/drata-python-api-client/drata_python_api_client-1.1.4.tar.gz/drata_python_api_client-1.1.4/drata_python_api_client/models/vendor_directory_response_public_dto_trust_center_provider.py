from enum import Enum


class VendorDirectoryResponsePublicDtoTrustCenterProvider(str, Enum):
    ANECDOTES = "ANECDOTES"
    CONVEYOR = "CONVEYOR"
    DRATA = "DRATA"
    HYPERCOMPLY = "HYPERCOMPLY"
    SAFEBASE = "SAFEBASE"
    SCRUT = "SCRUT"
    SECUREFRAME = "SECUREFRAME"
    SECURITYPAL = "SECURITYPAL"
    SKYPHER = "SKYPHER"
    SPRINTO = "SPRINTO"
    TRUSTARC = "TRUSTARC"
    TRUSTCLOUD = "TRUSTCLOUD"
    VANTA = "VANTA"
    WHISTIC = "WHISTIC"
    ZENGRC = "ZENGRC"

    def __str__(self) -> str:
        return str(self.value)
