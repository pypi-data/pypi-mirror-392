from enum import Enum


class AssetsPublicControllerListAssetsSort(str, Enum):
    APPROVED_AT = "APPROVED_AT"
    ASSET_PROVIDER = "ASSET_PROVIDER"
    ASSET_TYPE = "ASSET_TYPE"
    COMPANY_NAME = "COMPANY_NAME"
    CREATED = "CREATED"
    DESCRIPTION = "DESCRIPTION"
    EMPLOYMENT_STATUS = "EMPLOYMENT_STATUS"
    NAME = "NAME"
    REMOVED_AT = "REMOVED_AT"
    UPDATED = "UPDATED"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
