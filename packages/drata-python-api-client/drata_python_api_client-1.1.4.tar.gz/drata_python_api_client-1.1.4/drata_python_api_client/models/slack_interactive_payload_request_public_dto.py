from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.slack_action_request_public_dto import SlackActionRequestPublicDto
    from ..models.slack_interactive_payload_request_public_dto_enterprise import (
        SlackInteractivePayloadRequestPublicDtoEnterprise,
    )
    from ..models.slack_team_request_public_dto import SlackTeamRequestPublicDto
    from ..models.slack_user_request_public_dto import SlackUserRequestPublicDto
    from ..models.slack_view_request_public_dto import SlackViewRequestPublicDto


T = TypeVar("T", bound="SlackInteractivePayloadRequestPublicDto")


@_attrs_define
class SlackInteractivePayloadRequestPublicDto:
    """
    Attributes:
        type_ (str):
        team (SlackTeamRequestPublicDto):
        user (SlackUserRequestPublicDto):
        api_app_id (str):
        token (str):
        trigger_id (str):
        view (SlackViewRequestPublicDto):
        response_urls (list[str]):
        is_enterprise_install (bool):
        enterprise (Union[Unset, SlackInteractivePayloadRequestPublicDtoEnterprise]):
        actions (Union[Unset, list['SlackActionRequestPublicDto']]):
    """

    type_: str
    team: "SlackTeamRequestPublicDto"
    user: "SlackUserRequestPublicDto"
    api_app_id: str
    token: str
    trigger_id: str
    view: "SlackViewRequestPublicDto"
    response_urls: list[str]
    is_enterprise_install: bool
    enterprise: Union[Unset, "SlackInteractivePayloadRequestPublicDtoEnterprise"] = UNSET
    actions: Union[Unset, list["SlackActionRequestPublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        team = self.team.to_dict()

        user = self.user.to_dict()

        api_app_id = self.api_app_id

        token = self.token

        trigger_id = self.trigger_id

        view = self.view.to_dict()

        response_urls = self.response_urls

        is_enterprise_install = self.is_enterprise_install

        enterprise: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.enterprise, Unset):
            enterprise = self.enterprise.to_dict()

        actions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "team": team,
                "user": user,
                "api_app_id": api_app_id,
                "token": token,
                "trigger_id": trigger_id,
                "view": view,
                "response_urls": response_urls,
                "is_enterprise_install": is_enterprise_install,
            }
        )
        if enterprise is not UNSET:
            field_dict["enterprise"] = enterprise
        if actions is not UNSET:
            field_dict["actions"] = actions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_action_request_public_dto import SlackActionRequestPublicDto
        from ..models.slack_interactive_payload_request_public_dto_enterprise import (
            SlackInteractivePayloadRequestPublicDtoEnterprise,
        )
        from ..models.slack_team_request_public_dto import SlackTeamRequestPublicDto
        from ..models.slack_user_request_public_dto import SlackUserRequestPublicDto
        from ..models.slack_view_request_public_dto import SlackViewRequestPublicDto

        d = dict(src_dict)
        type_ = d.pop("type")

        team = SlackTeamRequestPublicDto.from_dict(d.pop("team"))

        user = SlackUserRequestPublicDto.from_dict(d.pop("user"))

        api_app_id = d.pop("api_app_id")

        token = d.pop("token")

        trigger_id = d.pop("trigger_id")

        view = SlackViewRequestPublicDto.from_dict(d.pop("view"))

        response_urls = cast(list[str], d.pop("response_urls"))

        is_enterprise_install = d.pop("is_enterprise_install")

        _enterprise = d.pop("enterprise", UNSET)
        enterprise: Union[Unset, SlackInteractivePayloadRequestPublicDtoEnterprise]
        if isinstance(_enterprise, Unset):
            enterprise = UNSET
        else:
            enterprise = SlackInteractivePayloadRequestPublicDtoEnterprise.from_dict(_enterprise)

        actions = []
        _actions = d.pop("actions", UNSET)
        for actions_item_data in _actions or []:
            actions_item = SlackActionRequestPublicDto.from_dict(actions_item_data)

            actions.append(actions_item)

        slack_interactive_payload_request_public_dto = cls(
            type_=type_,
            team=team,
            user=user,
            api_app_id=api_app_id,
            token=token,
            trigger_id=trigger_id,
            view=view,
            response_urls=response_urls,
            is_enterprise_install=is_enterprise_install,
            enterprise=enterprise,
            actions=actions,
        )

        slack_interactive_payload_request_public_dto.additional_properties = d
        return slack_interactive_payload_request_public_dto

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
