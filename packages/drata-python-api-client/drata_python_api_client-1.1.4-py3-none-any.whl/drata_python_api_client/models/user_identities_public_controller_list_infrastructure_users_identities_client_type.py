from enum import Enum


class UserIdentitiesPublicControllerListInfrastructureUsersIdentitiesClientType(str, Enum):
    AWS = "AWS"
    AWS_GOV_CLOUD = "AWS_GOV_CLOUD"
    AWS_ORG_UNITS = "AWS_ORG_UNITS"
    AZURE = "AZURE"
    AZURE_ORG_UNITS = "AZURE_ORG_UNITS"
    CLOUDFLARE = "CLOUDFLARE"
    DIGITAL_OCEAN = "DIGITAL_OCEAN"
    GCP = "GCP"
    HEROKU = "HEROKU"
    MONGO_DB_ATLAS = "MONGO_DB_ATLAS"

    def __str__(self) -> str:
        return str(self.value)
