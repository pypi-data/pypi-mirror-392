from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.block_public_dto import BlockPublicDto
    from ..models.exception_management_state_values_public_dto import ExceptionManagementStateValuesPublicDto
    from ..models.slack_view_request_public_dto_close import SlackViewRequestPublicDtoClose
    from ..models.slack_view_request_public_dto_submit import SlackViewRequestPublicDtoSubmit
    from ..models.title_public_dto import TitlePublicDto


T = TypeVar("T", bound="SlackViewRequestPublicDto")


@_attrs_define
class SlackViewRequestPublicDto:
    """
    Attributes:
        id (str):
        team_id (str):
        type_ (str):
        blocks (list['BlockPublicDto']):
        private_metadata (str):
        callback_id (str):
        state (ExceptionManagementStateValuesPublicDto):
        hash_ (str):
        title (TitlePublicDto):
        clear_on_close (bool):
        notify_on_close (bool):
        root_view_id (str):
        app_id (str):
        external_id (str):
        app_installed_team_id (str):
        bot_id (str):
        close (Union[Unset, SlackViewRequestPublicDtoClose]):
        submit (Union[Unset, SlackViewRequestPublicDtoSubmit]):
        previous_view_id (Union[Unset, str]):
    """

    id: str
    team_id: str
    type_: str
    blocks: list["BlockPublicDto"]
    private_metadata: str
    callback_id: str
    state: "ExceptionManagementStateValuesPublicDto"
    hash_: str
    title: "TitlePublicDto"
    clear_on_close: bool
    notify_on_close: bool
    root_view_id: str
    app_id: str
    external_id: str
    app_installed_team_id: str
    bot_id: str
    close: Union[Unset, "SlackViewRequestPublicDtoClose"] = UNSET
    submit: Union[Unset, "SlackViewRequestPublicDtoSubmit"] = UNSET
    previous_view_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        team_id = self.team_id

        type_ = self.type_

        blocks = []
        for blocks_item_data in self.blocks:
            blocks_item = blocks_item_data.to_dict()
            blocks.append(blocks_item)

        private_metadata = self.private_metadata

        callback_id = self.callback_id

        state = self.state.to_dict()

        hash_ = self.hash_

        title = self.title.to_dict()

        clear_on_close = self.clear_on_close

        notify_on_close = self.notify_on_close

        root_view_id = self.root_view_id

        app_id = self.app_id

        external_id = self.external_id

        app_installed_team_id = self.app_installed_team_id

        bot_id = self.bot_id

        close: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.close, Unset):
            close = self.close.to_dict()

        submit: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.submit, Unset):
            submit = self.submit.to_dict()

        previous_view_id = self.previous_view_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "team_id": team_id,
                "type": type_,
                "blocks": blocks,
                "private_metadata": private_metadata,
                "callback_id": callback_id,
                "state": state,
                "hash": hash_,
                "title": title,
                "clear_on_close": clear_on_close,
                "notify_on_close": notify_on_close,
                "root_view_id": root_view_id,
                "app_id": app_id,
                "external_id": external_id,
                "app_installed_team_id": app_installed_team_id,
                "bot_id": bot_id,
            }
        )
        if close is not UNSET:
            field_dict["close"] = close
        if submit is not UNSET:
            field_dict["submit"] = submit
        if previous_view_id is not UNSET:
            field_dict["previous_view_id"] = previous_view_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.block_public_dto import BlockPublicDto
        from ..models.exception_management_state_values_public_dto import ExceptionManagementStateValuesPublicDto
        from ..models.slack_view_request_public_dto_close import SlackViewRequestPublicDtoClose
        from ..models.slack_view_request_public_dto_submit import SlackViewRequestPublicDtoSubmit
        from ..models.title_public_dto import TitlePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        team_id = d.pop("team_id")

        type_ = d.pop("type")

        blocks = []
        _blocks = d.pop("blocks")
        for blocks_item_data in _blocks:
            blocks_item = BlockPublicDto.from_dict(blocks_item_data)

            blocks.append(blocks_item)

        private_metadata = d.pop("private_metadata")

        callback_id = d.pop("callback_id")

        state = ExceptionManagementStateValuesPublicDto.from_dict(d.pop("state"))

        hash_ = d.pop("hash")

        title = TitlePublicDto.from_dict(d.pop("title"))

        clear_on_close = d.pop("clear_on_close")

        notify_on_close = d.pop("notify_on_close")

        root_view_id = d.pop("root_view_id")

        app_id = d.pop("app_id")

        external_id = d.pop("external_id")

        app_installed_team_id = d.pop("app_installed_team_id")

        bot_id = d.pop("bot_id")

        _close = d.pop("close", UNSET)
        close: Union[Unset, SlackViewRequestPublicDtoClose]
        if isinstance(_close, Unset):
            close = UNSET
        else:
            close = SlackViewRequestPublicDtoClose.from_dict(_close)

        _submit = d.pop("submit", UNSET)
        submit: Union[Unset, SlackViewRequestPublicDtoSubmit]
        if isinstance(_submit, Unset):
            submit = UNSET
        else:
            submit = SlackViewRequestPublicDtoSubmit.from_dict(_submit)

        previous_view_id = d.pop("previous_view_id", UNSET)

        slack_view_request_public_dto = cls(
            id=id,
            team_id=team_id,
            type_=type_,
            blocks=blocks,
            private_metadata=private_metadata,
            callback_id=callback_id,
            state=state,
            hash_=hash_,
            title=title,
            clear_on_close=clear_on_close,
            notify_on_close=notify_on_close,
            root_view_id=root_view_id,
            app_id=app_id,
            external_id=external_id,
            app_installed_team_id=app_installed_team_id,
            bot_id=bot_id,
            close=close,
            submit=submit,
            previous_view_id=previous_view_id,
        )

        slack_view_request_public_dto.additional_properties = d
        return slack_view_request_public_dto

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
