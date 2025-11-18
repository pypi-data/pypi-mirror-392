from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.element_public_dto_dispatch_action_config import ElementPublicDtoDispatchActionConfig
    from ..models.element_public_dto_options_item import ElementPublicDtoOptionsItem
    from ..models.placeholder_public_dto import PlaceholderPublicDto


T = TypeVar("T", bound="ElementPublicDto")


@_attrs_define
class ElementPublicDto:
    """
    Attributes:
        type_ (str):
        action_id (str):
        placeholder (Union[Unset, PlaceholderPublicDto]):
        dispatch_action_config (Union[Unset, ElementPublicDtoDispatchActionConfig]):
        multiline (Union[Unset, bool]):
        options (Union[Unset, list['ElementPublicDtoOptionsItem']]):
        initial_date_time (Union[Unset, float]):
    """

    type_: str
    action_id: str
    placeholder: Union[Unset, "PlaceholderPublicDto"] = UNSET
    dispatch_action_config: Union[Unset, "ElementPublicDtoDispatchActionConfig"] = UNSET
    multiline: Union[Unset, bool] = UNSET
    options: Union[Unset, list["ElementPublicDtoOptionsItem"]] = UNSET
    initial_date_time: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        action_id = self.action_id

        placeholder: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.placeholder, Unset):
            placeholder = self.placeholder.to_dict()

        dispatch_action_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.dispatch_action_config, Unset):
            dispatch_action_config = self.dispatch_action_config.to_dict()

        multiline = self.multiline

        options: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()
                options.append(options_item)

        initial_date_time = self.initial_date_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "action_id": action_id,
            }
        )
        if placeholder is not UNSET:
            field_dict["placeholder"] = placeholder
        if dispatch_action_config is not UNSET:
            field_dict["dispatch_action_config"] = dispatch_action_config
        if multiline is not UNSET:
            field_dict["multiline"] = multiline
        if options is not UNSET:
            field_dict["options"] = options
        if initial_date_time is not UNSET:
            field_dict["initial_date_time"] = initial_date_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.element_public_dto_dispatch_action_config import ElementPublicDtoDispatchActionConfig
        from ..models.element_public_dto_options_item import ElementPublicDtoOptionsItem
        from ..models.placeholder_public_dto import PlaceholderPublicDto

        d = dict(src_dict)
        type_ = d.pop("type")

        action_id = d.pop("action_id")

        _placeholder = d.pop("placeholder", UNSET)
        placeholder: Union[Unset, PlaceholderPublicDto]
        if isinstance(_placeholder, Unset):
            placeholder = UNSET
        else:
            placeholder = PlaceholderPublicDto.from_dict(_placeholder)

        _dispatch_action_config = d.pop("dispatch_action_config", UNSET)
        dispatch_action_config: Union[Unset, ElementPublicDtoDispatchActionConfig]
        if isinstance(_dispatch_action_config, Unset):
            dispatch_action_config = UNSET
        else:
            dispatch_action_config = ElementPublicDtoDispatchActionConfig.from_dict(_dispatch_action_config)

        multiline = d.pop("multiline", UNSET)

        options = []
        _options = d.pop("options", UNSET)
        for options_item_data in _options or []:
            options_item = ElementPublicDtoOptionsItem.from_dict(options_item_data)

            options.append(options_item)

        initial_date_time = d.pop("initial_date_time", UNSET)

        element_public_dto = cls(
            type_=type_,
            action_id=action_id,
            placeholder=placeholder,
            dispatch_action_config=dispatch_action_config,
            multiline=multiline,
            options=options,
            initial_date_time=initial_date_time,
        )

        element_public_dto.additional_properties = d
        return element_public_dto

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
