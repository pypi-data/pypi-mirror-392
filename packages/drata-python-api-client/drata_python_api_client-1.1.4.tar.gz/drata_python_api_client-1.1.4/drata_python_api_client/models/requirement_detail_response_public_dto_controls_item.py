import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RequirementDetailResponsePublicDtoControlsItem")


@_attrs_define
class RequirementDetailResponsePublicDtoControlsItem:
    """
    Attributes:
        id (Union[Unset, float]):
        code (Union[Unset, str]):
        is_ready (Union[Unset, bool]):
        control_number (Union[Unset, float]):
        archived_at (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, float] = UNSET
    code: Union[Unset, str] = UNSET
    is_ready: Union[Unset, bool] = UNSET
    control_number: Union[Unset, float] = UNSET
    archived_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        is_ready = self.is_ready

        control_number = self.control_number

        archived_at: Union[Unset, str] = UNSET
        if not isinstance(self.archived_at, Unset):
            archived_at = self.archived_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if code is not UNSET:
            field_dict["code"] = code
        if is_ready is not UNSET:
            field_dict["isReady"] = is_ready
        if control_number is not UNSET:
            field_dict["controlNumber"] = control_number
        if archived_at is not UNSET:
            field_dict["archivedAt"] = archived_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        code = d.pop("code", UNSET)

        is_ready = d.pop("isReady", UNSET)

        control_number = d.pop("controlNumber", UNSET)

        _archived_at = d.pop("archivedAt", UNSET)
        archived_at: Union[Unset, datetime.datetime]
        if isinstance(_archived_at, Unset):
            archived_at = UNSET
        else:
            archived_at = isoparse(_archived_at)

        requirement_detail_response_public_dto_controls_item = cls(
            id=id,
            code=code,
            is_ready=is_ready,
            control_number=control_number,
            archived_at=archived_at,
        )

        requirement_detail_response_public_dto_controls_item.additional_properties = d
        return requirement_detail_response_public_dto_controls_item

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
