from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.block_public_dto_accessory import BlockPublicDtoAccessory
    from ..models.block_public_dto_text import BlockPublicDtoText
    from ..models.element_public_dto import ElementPublicDto
    from ..models.label_public_dto import LabelPublicDto


T = TypeVar("T", bound="BlockPublicDto")


@_attrs_define
class BlockPublicDto:
    """
    Attributes:
        type_ (str):
        block_id (str):
        label (Union[Unset, LabelPublicDto]):
        optional (Union[Unset, bool]):
        dispatch_action (Union[Unset, bool]):
        element (Union[Unset, ElementPublicDto]):
        text (Union[Unset, BlockPublicDtoText]):
        accessory (Union[Unset, BlockPublicDtoAccessory]):
    """

    type_: str
    block_id: str
    label: Union[Unset, "LabelPublicDto"] = UNSET
    optional: Union[Unset, bool] = UNSET
    dispatch_action: Union[Unset, bool] = UNSET
    element: Union[Unset, "ElementPublicDto"] = UNSET
    text: Union[Unset, "BlockPublicDtoText"] = UNSET
    accessory: Union[Unset, "BlockPublicDtoAccessory"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        block_id = self.block_id

        label: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.label, Unset):
            label = self.label.to_dict()

        optional = self.optional

        dispatch_action = self.dispatch_action

        element: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.element, Unset):
            element = self.element.to_dict()

        text: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.text, Unset):
            text = self.text.to_dict()

        accessory: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.accessory, Unset):
            accessory = self.accessory.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "block_id": block_id,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if optional is not UNSET:
            field_dict["optional"] = optional
        if dispatch_action is not UNSET:
            field_dict["dispatch_action"] = dispatch_action
        if element is not UNSET:
            field_dict["element"] = element
        if text is not UNSET:
            field_dict["text"] = text
        if accessory is not UNSET:
            field_dict["accessory"] = accessory

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.block_public_dto_accessory import BlockPublicDtoAccessory
        from ..models.block_public_dto_text import BlockPublicDtoText
        from ..models.element_public_dto import ElementPublicDto
        from ..models.label_public_dto import LabelPublicDto

        d = dict(src_dict)
        type_ = d.pop("type")

        block_id = d.pop("block_id")

        _label = d.pop("label", UNSET)
        label: Union[Unset, LabelPublicDto]
        if isinstance(_label, Unset):
            label = UNSET
        else:
            label = LabelPublicDto.from_dict(_label)

        optional = d.pop("optional", UNSET)

        dispatch_action = d.pop("dispatch_action", UNSET)

        _element = d.pop("element", UNSET)
        element: Union[Unset, ElementPublicDto]
        if isinstance(_element, Unset):
            element = UNSET
        else:
            element = ElementPublicDto.from_dict(_element)

        _text = d.pop("text", UNSET)
        text: Union[Unset, BlockPublicDtoText]
        if isinstance(_text, Unset):
            text = UNSET
        else:
            text = BlockPublicDtoText.from_dict(_text)

        _accessory = d.pop("accessory", UNSET)
        accessory: Union[Unset, BlockPublicDtoAccessory]
        if isinstance(_accessory, Unset):
            accessory = UNSET
        else:
            accessory = BlockPublicDtoAccessory.from_dict(_accessory)

        block_public_dto = cls(
            type_=type_,
            block_id=block_id,
            label=label,
            optional=optional,
            dispatch_action=dispatch_action,
            element=element,
            text=text,
            accessory=accessory,
        )

        block_public_dto.additional_properties = d
        return block_public_dto

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
