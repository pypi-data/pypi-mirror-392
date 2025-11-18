from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.exception_response_dto_debug_info import ExceptionResponseDtoDebugInfo


T = TypeVar("T", bound="ExceptionResponseDto")


@_attrs_define
class ExceptionResponseDto:
    """
    Attributes:
        name (str):
        status_code (float):
        message (str):
        code (float):
        debug_info (Union[Unset, ExceptionResponseDtoDebugInfo]):
    """

    name: str
    status_code: float
    message: str
    code: float
    debug_info: Union[Unset, "ExceptionResponseDtoDebugInfo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status_code = self.status_code

        message = self.message

        code = self.code

        debug_info: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.debug_info, Unset):
            debug_info = self.debug_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "statusCode": status_code,
                "message": message,
                "code": code,
            }
        )
        if debug_info is not UNSET:
            field_dict["debugInfo"] = debug_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exception_response_dto_debug_info import ExceptionResponseDtoDebugInfo

        d = dict(src_dict)
        if name := d.pop("name", UNSET) is UNSET:
            name = None

        status_code = d.pop("statusCode")

        message = d.pop("message")

        code = d.pop("code")

        _debug_info = d.pop("debugInfo", UNSET)
        debug_info: Union[Unset, ExceptionResponseDtoDebugInfo]
        if isinstance(_debug_info, Unset):
            debug_info = UNSET
        else:
            debug_info = ExceptionResponseDtoDebugInfo.from_dict(_debug_info)

        exception_response_dto = cls(
            name=name,
            status_code=status_code,
            message=message,
            code=code,
            debug_info=debug_info,
        )

        exception_response_dto.additional_properties = d
        return exception_response_dto

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
