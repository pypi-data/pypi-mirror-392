from enum import Enum


class AssetRequestPublicDtoAssetClassTypesItem(str, Enum):
    CODE = "CODE"
    COMPUTE = "COMPUTE"
    CONTAINER = "CONTAINER"
    DATABASE = "DATABASE"
    DOCUMENT = "DOCUMENT"
    HARDWARE = "HARDWARE"
    NETWORKING = "NETWORKING"
    PERSONNEL = "PERSONNEL"
    POLICY = "POLICY"
    SOFTWARE = "SOFTWARE"
    STORAGE = "STORAGE"

    def __str__(self) -> str:
        return str(self.value)
