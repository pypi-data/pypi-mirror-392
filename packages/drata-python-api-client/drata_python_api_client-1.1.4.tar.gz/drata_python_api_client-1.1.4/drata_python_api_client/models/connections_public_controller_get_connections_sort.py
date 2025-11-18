from enum import Enum


class ConnectionsPublicControllerGetConnectionsSort(str, Enum):
    CONNECTED_AT = "CONNECTED_AT"
    CONNECTION_CLIENT_TYPE = "CONNECTION_CLIENT_TYPE"
    CONNECTION_PROVIDER_TYPE = "CONNECTION_PROVIDER_TYPE"
    CONNECTION_STATE = "CONNECTION_STATE"
    CREATED_AT = "CREATED_AT"

    def __str__(self) -> str:
        return str(self.value)
