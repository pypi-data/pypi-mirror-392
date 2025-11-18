import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connection_response_public_dto_code import ConnectionResponsePublicDtoCode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connection_provider_type_response_public_dto import ConnectionProviderTypeResponsePublicDto
    from ..models.connection_response_public_dto_product import ConnectionResponsePublicDtoProduct
    from ..models.user_response_public_dto import UserResponsePublicDto
    from ..models.workspace_response_public_dto import WorkspaceResponsePublicDto


T = TypeVar("T", bound="ConnectionResponsePublicDto")


@_attrs_define
class ConnectionResponsePublicDto:
    """
    Attributes:
        id (float): The connection id Example: 1.
        client_type (str): The client type Example: GOOGLE.
        state (str): The state of the connection Example: ACTIVE.
        connected (bool): Connection status
        connected_at (Union[None, datetime.datetime]): When this connection was successfully established Example:
            2025-07-01T16:45:55.246Z.
        failed_at (Union[None, datetime.datetime]): When this connection failed Example: 2025-07-01T16:45:55.246Z.
        company_id (float): The associated external company id. Specific to the gusto connection Example: 12341234.
        assignment_id (str): The associated external assignment id. Specific to the curricula connection Example:
            FLk12AsS.
        user (UserResponsePublicDto):
        account_id (str): The related account id to that connection
        client_id (str): The client id from the external system associated to this connection Example: drata.com.
        client_alias (str): Alias for the connection Example: My-connection-alias-1.
        manually_updated_at (datetime.datetime): Connection manuallyUpdatedAts timestamp Example:
            2025-07-01T16:45:55.246Z.
        alias_updated_at (datetime.datetime): Connection alias updated-at timestamp for manually updated aliases
            Example: 2025-07-01T16:45:55.246Z.
        deleted_at (datetime.datetime): Connection deletedAt timestamp Example: 2025-07-01T16:45:55.246Z.
        requestor_id (float): RequestorId value Example: 328d3016-71f3-4485-af20-06ce8044da18.
        product (ConnectionResponsePublicDtoProduct): product background check
        write_access_enabled (bool): Write scope is enabled on the connection
        source_preference (str): User source preference for Jira Example: LABEL.
        security_label (str): Used in Jira to categorize tickets as security issues. Example: Jira Security Label.
        jql_query (str): Query used in Jira to categorize tickets Example: project = IT AND type = "Offboarding".
        authorized (bool): account authorized flag for Checkr Example: True.
        workspaces (list['WorkspaceResponsePublicDto']): Workspaces related to the connection Example: [{'id': 1,
            'name': 'Drata', 'description': 'Platform to track SOC 2 compliance within the organization', 'howItWorks':
            None, 'url': 'https://app.drata.com', 'logo': 'https://cdn.drata.com/icon/icon_fwhite_bblue_256.png', 'primary':
            True}].
        code (ConnectionResponsePublicDtoCode): ErrorCode Example: 10010.
        group_label (Union[None, str]): Used by some IDPs to only sync users from a specific group Example: Everyone.
        provider_types (Union[Unset, list['ConnectionProviderTypeResponsePublicDto']]): Provider types associated with
            this connection Example: [5].
    """

    id: float
    client_type: str
    state: str
    connected: bool
    connected_at: Union[None, datetime.datetime]
    failed_at: Union[None, datetime.datetime]
    company_id: float
    assignment_id: str
    user: "UserResponsePublicDto"
    account_id: str
    client_id: str
    client_alias: str
    manually_updated_at: datetime.datetime
    alias_updated_at: datetime.datetime
    deleted_at: datetime.datetime
    requestor_id: float
    product: "ConnectionResponsePublicDtoProduct"
    write_access_enabled: bool
    source_preference: str
    security_label: str
    jql_query: str
    authorized: bool
    workspaces: list["WorkspaceResponsePublicDto"]
    code: ConnectionResponsePublicDtoCode
    group_label: Union[None, str]
    provider_types: Union[Unset, list["ConnectionProviderTypeResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        client_type = self.client_type

        state = self.state

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

        company_id = self.company_id

        assignment_id = self.assignment_id

        user = self.user.to_dict()

        account_id = self.account_id

        client_id = self.client_id

        client_alias = self.client_alias

        manually_updated_at = self.manually_updated_at.isoformat()

        alias_updated_at = self.alias_updated_at.isoformat()

        deleted_at = self.deleted_at.isoformat()

        requestor_id = self.requestor_id

        product = self.product.to_dict()

        write_access_enabled = self.write_access_enabled

        source_preference = self.source_preference

        security_label = self.security_label

        jql_query = self.jql_query

        authorized = self.authorized

        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        code = self.code.value

        group_label: Union[None, str]
        group_label = self.group_label

        provider_types: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.provider_types, Unset):
            provider_types = []
            for provider_types_item_data in self.provider_types:
                provider_types_item = provider_types_item_data.to_dict()
                provider_types.append(provider_types_item)

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
                "companyId": company_id,
                "assignmentId": assignment_id,
                "user": user,
                "accountId": account_id,
                "clientId": client_id,
                "clientAlias": client_alias,
                "manuallyUpdatedAt": manually_updated_at,
                "aliasUpdatedAt": alias_updated_at,
                "deletedAt": deleted_at,
                "requestorId": requestor_id,
                "product": product,
                "writeAccessEnabled": write_access_enabled,
                "sourcePreference": source_preference,
                "securityLabel": security_label,
                "jqlQuery": jql_query,
                "authorized": authorized,
                "workspaces": workspaces,
                "code": code,
                "groupLabel": group_label,
            }
        )
        if provider_types is not UNSET:
            field_dict["providerTypes"] = provider_types

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_provider_type_response_public_dto import ConnectionProviderTypeResponsePublicDto
        from ..models.connection_response_public_dto_product import ConnectionResponsePublicDtoProduct
        from ..models.user_response_public_dto import UserResponsePublicDto
        from ..models.workspace_response_public_dto import WorkspaceResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        client_type = d.pop("clientType")

        state = d.pop("state")

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

        company_id = d.pop("companyId")

        assignment_id = d.pop("assignmentId")

        user = UserResponsePublicDto.from_dict(d.pop("user"))

        account_id = d.pop("accountId")

        client_id = d.pop("clientId")

        client_alias = d.pop("clientAlias")

        manually_updated_at = isoparse(d.pop("manuallyUpdatedAt"))

        alias_updated_at = isoparse(d.pop("aliasUpdatedAt"))

        deleted_at = isoparse(d.pop("deletedAt"))

        requestor_id = d.pop("requestorId")

        product = ConnectionResponsePublicDtoProduct.from_dict(d.pop("product"))

        write_access_enabled = d.pop("writeAccessEnabled")

        source_preference = d.pop("sourcePreference")

        security_label = d.pop("securityLabel")

        jql_query = d.pop("jqlQuery")

        authorized = d.pop("authorized")

        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = WorkspaceResponsePublicDto.from_dict(workspaces_item_data)

            workspaces.append(workspaces_item)

        code = ConnectionResponsePublicDtoCode(d.pop("code"))

        def _parse_group_label(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        group_label = _parse_group_label(d.pop("groupLabel"))

        provider_types = []
        _provider_types = d.pop("providerTypes", UNSET)
        for provider_types_item_data in _provider_types or []:
            provider_types_item = ConnectionProviderTypeResponsePublicDto.from_dict(provider_types_item_data)

            provider_types.append(provider_types_item)

        connection_response_public_dto = cls(
            id=id,
            client_type=client_type,
            state=state,
            connected=connected,
            connected_at=connected_at,
            failed_at=failed_at,
            company_id=company_id,
            assignment_id=assignment_id,
            user=user,
            account_id=account_id,
            client_id=client_id,
            client_alias=client_alias,
            manually_updated_at=manually_updated_at,
            alias_updated_at=alias_updated_at,
            deleted_at=deleted_at,
            requestor_id=requestor_id,
            product=product,
            write_access_enabled=write_access_enabled,
            source_preference=source_preference,
            security_label=security_label,
            jql_query=jql_query,
            authorized=authorized,
            workspaces=workspaces,
            code=code,
            group_label=group_label,
            provider_types=provider_types,
        )

        connection_response_public_dto.additional_properties = d
        return connection_response_public_dto

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
