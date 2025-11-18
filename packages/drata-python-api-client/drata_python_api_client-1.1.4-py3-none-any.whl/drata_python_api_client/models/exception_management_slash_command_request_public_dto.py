from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExceptionManagementSlashCommandRequestPublicDto")


@_attrs_define
class ExceptionManagementSlashCommandRequestPublicDto:
    """
    Attributes:
        trigger_id (str): The trigger id from the slack slash command request Example:
            7734259451425.3661857653522.b78c8844c0341316972b64fb7970b7a5.
        team_id (str): The team/workspace id from the slack slash command request Example: T03KFR7K7FZ.
    """

    trigger_id: str
    team_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trigger_id = self.trigger_id

        team_id = self.team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "trigger_id": trigger_id,
                "team_id": team_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        trigger_id = d.pop("trigger_id")

        team_id = d.pop("team_id")

        exception_management_slash_command_request_public_dto = cls(
            trigger_id=trigger_id,
            team_id=team_id,
        )

        exception_management_slash_command_request_public_dto.additional_properties = d
        return exception_management_slash_command_request_public_dto

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
