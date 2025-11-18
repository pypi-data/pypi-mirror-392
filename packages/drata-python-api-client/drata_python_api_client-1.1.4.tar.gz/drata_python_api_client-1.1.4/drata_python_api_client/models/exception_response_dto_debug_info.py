from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExceptionResponseDtoDebugInfo")


@_attrs_define
class ExceptionResponseDtoDebugInfo:
    """
    Attributes:
        name (str):
        message (str):
        stack (Union[Unset, str]):
    """

    name: str
    message: str
    stack: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        message = self.message

        stack = self.stack

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "message": message,
            }
        )
        if stack is not UNSET:
            field_dict["stack"] = stack

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        message = d.pop("message")

        stack = d.pop("stack", UNSET)

        exception_response_dto_debug_info = cls(
            name=name,
            message=message,
            stack=stack,
        )

        exception_response_dto_debug_info.additional_properties = d
        return exception_response_dto_debug_info

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
