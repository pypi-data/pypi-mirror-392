from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.monitor_instance_metadata_response_public_dto_groups_item import (
        MonitorInstanceMetadataResponsePublicDtoGroupsItem,
    )
    from ..models.monitor_metadata_data_response_public_dto import MonitorMetadataDataResponsePublicDto
    from ..models.monitor_metadata_exclusion_response_public_dto import MonitorMetadataExclusionResponsePublicDto


T = TypeVar("T", bound="MonitorInstanceMetadataResponsePublicDto")


@_attrs_define
class MonitorInstanceMetadataResponsePublicDto:
    """
    Attributes:
        check_result_status (str): Denotes monitor check pass/fail/issue Example: PASSED.
        type_ (str): The monitor data type Example: LIST.
        source (str): The monitor data source Example: AWS.
        connection_id (float): The source connection id Example: 1.
        client_id (str): The source connection client id Example: drata-acme.
        client_alias (str): The alias of the connection. Example: my-connection-alias.
        client_type (str): The source connection client type string representation Example: AWS.
        pass_ (list['MonitorMetadataDataResponsePublicDto']): A list of of passed MonitorMetadataDataResponseDto
        fail (list['MonitorMetadataDataResponsePublicDto']): A list of of failed MonitorMetadataDataResponseDto
        exclusions (list['MonitorMetadataExclusionResponsePublicDto']): A list of of
            MonitorMetadataExclusionsResponseDto
        message (str): The metadata message string
        policy_scope (str): The Policy Scope of the monitor if required
        policy_name (str): The Policy Name of the monitor if required
        groups (list['MonitorInstanceMetadataResponsePublicDtoGroupsItem']): The Policy group of the monitor if required
    """

    check_result_status: str
    type_: str
    source: str
    connection_id: float
    client_id: str
    client_alias: str
    client_type: str
    pass_: list["MonitorMetadataDataResponsePublicDto"]
    fail: list["MonitorMetadataDataResponsePublicDto"]
    exclusions: list["MonitorMetadataExclusionResponsePublicDto"]
    message: str
    policy_scope: str
    policy_name: str
    groups: list["MonitorInstanceMetadataResponsePublicDtoGroupsItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        check_result_status = self.check_result_status

        type_ = self.type_

        source = self.source

        connection_id = self.connection_id

        client_id = self.client_id

        client_alias = self.client_alias

        client_type = self.client_type

        pass_ = []
        for pass_item_data in self.pass_:
            pass_item = pass_item_data.to_dict()
            pass_.append(pass_item)

        fail = []
        for fail_item_data in self.fail:
            fail_item = fail_item_data.to_dict()
            fail.append(fail_item)

        exclusions = []
        for exclusions_item_data in self.exclusions:
            exclusions_item = exclusions_item_data.to_dict()
            exclusions.append(exclusions_item)

        message = self.message

        policy_scope = self.policy_scope

        policy_name = self.policy_name

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checkResultStatus": check_result_status,
                "type": type_,
                "source": source,
                "connectionId": connection_id,
                "clientId": client_id,
                "clientAlias": client_alias,
                "clientType": client_type,
                "pass": pass_,
                "fail": fail,
                "exclusions": exclusions,
                "message": message,
                "policyScope": policy_scope,
                "policyName": policy_name,
                "groups": groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.monitor_instance_metadata_response_public_dto_groups_item import (
            MonitorInstanceMetadataResponsePublicDtoGroupsItem,
        )
        from ..models.monitor_metadata_data_response_public_dto import MonitorMetadataDataResponsePublicDto
        from ..models.monitor_metadata_exclusion_response_public_dto import MonitorMetadataExclusionResponsePublicDto

        d = dict(src_dict)
        check_result_status = d.pop("checkResultStatus")

        type_ = d.pop("type")

        source = d.pop("source")

        connection_id = d.pop("connectionId")

        client_id = d.pop("clientId")

        client_alias = d.pop("clientAlias")

        client_type = d.pop("clientType")

        pass_ = []
        _pass_ = d.pop("pass")
        for pass_item_data in _pass_:
            pass_item = MonitorMetadataDataResponsePublicDto.from_dict(pass_item_data)

            pass_.append(pass_item)

        fail = []
        _fail = d.pop("fail")
        for fail_item_data in _fail:
            fail_item = MonitorMetadataDataResponsePublicDto.from_dict(fail_item_data)

            fail.append(fail_item)

        exclusions = []
        _exclusions = d.pop("exclusions")
        for exclusions_item_data in _exclusions:
            exclusions_item = MonitorMetadataExclusionResponsePublicDto.from_dict(exclusions_item_data)

            exclusions.append(exclusions_item)

        message = d.pop("message")

        policy_scope = d.pop("policyScope")

        policy_name = d.pop("policyName")

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = MonitorInstanceMetadataResponsePublicDtoGroupsItem.from_dict(groups_item_data)

            groups.append(groups_item)

        monitor_instance_metadata_response_public_dto = cls(
            check_result_status=check_result_status,
            type_=type_,
            source=source,
            connection_id=connection_id,
            client_id=client_id,
            client_alias=client_alias,
            client_type=client_type,
            pass_=pass_,
            fail=fail,
            exclusions=exclusions,
            message=message,
            policy_scope=policy_scope,
            policy_name=policy_name,
            groups=groups,
        )

        monitor_instance_metadata_response_public_dto.additional_properties = d
        return monitor_instance_metadata_response_public_dto

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
