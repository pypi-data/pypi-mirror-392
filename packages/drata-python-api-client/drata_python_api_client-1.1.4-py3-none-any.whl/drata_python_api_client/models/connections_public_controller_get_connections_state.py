from enum import Enum


class ConnectionsPublicControllerGetConnectionsState(str, Enum):
    ACTIVE = "ACTIVE"
    CONFIGURED_PENDING_CONFIRMATION = "CONFIGURED_PENDING_CONFIRMATION"
    IN_PROGRESS = "IN_PROGRESS"
    MISCONFIGURED = "MISCONFIGURED"

    def __str__(self) -> str:
        return str(self.value)
