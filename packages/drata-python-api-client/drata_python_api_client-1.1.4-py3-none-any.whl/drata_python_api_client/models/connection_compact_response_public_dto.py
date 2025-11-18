import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.client_type_enum import ClientTypeEnum
from ..models.connection_compact_response_public_dto_state import ConnectionCompactResponsePublicDtoState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connection_provider_type_response_public_dto import ConnectionProviderTypeResponsePublicDto


T = TypeVar("T", bound="ConnectionCompactResponsePublicDto")


@_attrs_define
class ConnectionCompactResponsePublicDto:
    """
    Attributes:
        id (float): The connection ID Example: 1.
        client_type (ClientTypeEnum):
        state (ConnectionCompactResponsePublicDtoState): The state of the connection Example: ACTIVE.
        connected (bool): Connection status
        connected_at (Union[None, datetime.datetime]): The date when this connection was successfully established
            Example: 2025-04-10T01:15:28.504Z.
        failed_at (Union[None, datetime.datetime]): The date when this connection failed Example:
            2025-04-10T01:15:28.505Z.
        client_id (Union[None, str]): The client ID from the external system associated to this connection Example:
            drata.com.
        client_alias (Union[None, str]): Alias for the connection Example: My-connection-alias-1.
        alias_updated_at (Union[None, datetime.datetime]): Date when the connection alias was updated for manually
            updated aliases Example: 2025-04-10T01:15:28.505Z.
        deleted_at (Union[None, datetime.datetime]): Date when connection was deleted Example: 2025-04-10T01:15:28.505Z.
        code (Union[None, float]): ErrorCode Example: 10010.
        provider_types (Union[Unset, list['ConnectionProviderTypeResponsePublicDto']]): Provider types associated with
            this connection
        group_label (Union[None, Unset, str]): Used by some IDPs to only sync users from a specific group Example:
            Everyone.
    """

    id: float
    client_type: ClientTypeEnum
    state: ConnectionCompactResponsePublicDtoState
    connected: bool
    connected_at: Union[None, datetime.datetime]
    failed_at: Union[None, datetime.datetime]
    client_id: Union[None, str]
    client_alias: Union[None, str]
    alias_updated_at: Union[None, datetime.datetime]
    deleted_at: Union[None, datetime.datetime]
    code: Union[None, float]
    provider_types: Union[Unset, list["ConnectionProviderTypeResponsePublicDto"]] = UNSET
    group_label: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        client_type = self.client_type.value

        state = self.state.value

        connected = self.connected

        connected_at: Union[None, str]
        if isinstance(self.connected_at, datetime.datetime):
            connected_at = self.connected_at.isoformat()
        else:
            connected_at = self.connected_at

        failed_at: Union[None, str]
        if isinstance(self.failed_at, datetime.datetime):
            failed_at = self.failed_at.isoformat()
        else:
            failed_at = self.failed_at

        client_id: Union[None, str]
        client_id = self.client_id

        client_alias: Union[None, str]
        client_alias = self.client_alias

        alias_updated_at: Union[None, str]
        if isinstance(self.alias_updated_at, datetime.datetime):
            alias_updated_at = self.alias_updated_at.isoformat()
        else:
            alias_updated_at = self.alias_updated_at

        deleted_at: Union[None, str]
        if isinstance(self.deleted_at, datetime.datetime):
            deleted_at = self.deleted_at.isoformat()
        else:
            deleted_at = self.deleted_at

        code: Union[None, float]
        code = self.code

        provider_types: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.provider_types, Unset):
            provider_types = []
            for provider_types_item_data in self.provider_types:
                provider_types_item = provider_types_item_data.to_dict()
                provider_types.append(provider_types_item)

        group_label: Union[None, Unset, str]
        if isinstance(self.group_label, Unset):
            group_label = UNSET
        else:
            group_label = self.group_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "clientType": client_type,
                "state": state,
                "connected": connected,
                "connectedAt": connected_at,
                "failedAt": failed_at,
                "clientId": client_id,
                "clientAlias": client_alias,
                "aliasUpdatedAt": alias_updated_at,
                "deletedAt": deleted_at,
                "code": code,
            }
        )
        if provider_types is not UNSET:
            field_dict["providerTypes"] = provider_types
        if group_label is not UNSET:
            field_dict["groupLabel"] = group_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_provider_type_response_public_dto import ConnectionProviderTypeResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        client_type = ClientTypeEnum(d.pop("clientType"))

        state = ConnectionCompactResponsePublicDtoState(d.pop("state"))

        connected = d.pop("connected")

        def _parse_connected_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                connected_at_type_0 = isoparse(data)

                return connected_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        connected_at = _parse_connected_at(d.pop("connectedAt"))

        def _parse_failed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                failed_at_type_0 = isoparse(data)

                return failed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        failed_at = _parse_failed_at(d.pop("failedAt"))

        def _parse_client_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        client_id = _parse_client_id(d.pop("clientId"))

        def _parse_client_alias(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        client_alias = _parse_client_alias(d.pop("clientAlias"))

        def _parse_alias_updated_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                alias_updated_at_type_0 = isoparse(data)

                return alias_updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        alias_updated_at = _parse_alias_updated_at(d.pop("aliasUpdatedAt"))

        def _parse_deleted_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_at_type_0 = isoparse(data)

                return deleted_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        deleted_at = _parse_deleted_at(d.pop("deletedAt"))

        def _parse_code(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        code = _parse_code(d.pop("code"))

        provider_types = []
        _provider_types = d.pop("providerTypes", UNSET)
        for provider_types_item_data in _provider_types or []:
            provider_types_item = ConnectionProviderTypeResponsePublicDto.from_dict(provider_types_item_data)

            provider_types.append(provider_types_item)

        def _parse_group_label(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        group_label = _parse_group_label(d.pop("groupLabel", UNSET))

        connection_compact_response_public_dto = cls(
            id=id,
            client_type=client_type,
            state=state,
            connected=connected,
            connected_at=connected_at,
            failed_at=failed_at,
            client_id=client_id,
            client_alias=client_alias,
            alias_updated_at=alias_updated_at,
            deleted_at=deleted_at,
            code=code,
            provider_types=provider_types,
            group_label=group_label,
        )

        connection_compact_response_public_dto.additional_properties = d
        return connection_compact_response_public_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
