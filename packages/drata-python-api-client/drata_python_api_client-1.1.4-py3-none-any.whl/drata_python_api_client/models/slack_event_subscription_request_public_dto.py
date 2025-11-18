from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.authorization_request_public_dto import AuthorizationRequestPublicDto
    from ..models.slack_event_subscription_request_public_dto_event import SlackEventSubscriptionRequestPublicDtoEvent


T = TypeVar("T", bound="SlackEventSubscriptionRequestPublicDto")


@_attrs_define
class SlackEventSubscriptionRequestPublicDto:
    """
    Attributes:
        token (str):
        team_id (str):
        api_app_id (str):
        event (SlackEventSubscriptionRequestPublicDtoEvent):
        type_ (str):
        event_id (str):
        event_time (float):
        authorizations (list['AuthorizationRequestPublicDto']):
        is_ext_shared_channel (bool):
    """

    token: str
    team_id: str
    api_app_id: str
    event: "SlackEventSubscriptionRequestPublicDtoEvent"
    type_: str
    event_id: str
    event_time: float
    authorizations: list["AuthorizationRequestPublicDto"]
    is_ext_shared_channel: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        team_id = self.team_id

        api_app_id = self.api_app_id

        event = self.event.to_dict()

        type_ = self.type_

        event_id = self.event_id

        event_time = self.event_time

        authorizations = []
        for authorizations_item_data in self.authorizations:
            authorizations_item = authorizations_item_data.to_dict()
            authorizations.append(authorizations_item)

        is_ext_shared_channel = self.is_ext_shared_channel

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "token": token,
                "team_id": team_id,
                "api_app_id": api_app_id,
                "event": event,
                "type": type_,
                "event_id": event_id,
                "event_time": event_time,
                "authorizations": authorizations,
                "is_ext_shared_channel": is_ext_shared_channel,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_request_public_dto import AuthorizationRequestPublicDto
        from ..models.slack_event_subscription_request_public_dto_event import (
            SlackEventSubscriptionRequestPublicDtoEvent,
        )

        d = dict(src_dict)
        token = d.pop("token")

        team_id = d.pop("team_id")

        api_app_id = d.pop("api_app_id")

        event = SlackEventSubscriptionRequestPublicDtoEvent.from_dict(d.pop("event"))

        type_ = d.pop("type")

        event_id = d.pop("event_id")

        event_time = d.pop("event_time")

        authorizations = []
        _authorizations = d.pop("authorizations")
        for authorizations_item_data in _authorizations:
            authorizations_item = AuthorizationRequestPublicDto.from_dict(authorizations_item_data)

            authorizations.append(authorizations_item)

        is_ext_shared_channel = d.pop("is_ext_shared_channel")

        slack_event_subscription_request_public_dto = cls(
            token=token,
            team_id=team_id,
            api_app_id=api_app_id,
            event=event,
            type_=type_,
            event_id=event_id,
            event_time=event_time,
            authorizations=authorizations,
            is_ext_shared_channel=is_ext_shared_channel,
        )

        slack_event_subscription_request_public_dto.additional_properties = d
        return slack_event_subscription_request_public_dto

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
