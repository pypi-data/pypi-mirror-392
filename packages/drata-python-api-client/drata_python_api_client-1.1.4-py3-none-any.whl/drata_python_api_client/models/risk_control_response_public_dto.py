import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RiskControlResponsePublicDto")


@_attrs_define
class RiskControlResponsePublicDto:
    """
    Attributes:
        id (float): Control Id Example: 23.
        code (str): Control code Example: DCF-01.
        name (str): Control name Example: Hello.
        description (str): Control description Example: this is a description.
        is_ready (bool): Control ready or not Example: True.
        control_number (Union[None, Unset, float]): Control number Example: 1.
        archived_at (Union[None, Unset, datetime.datetime]): Control out of scope Example: 1.
    """

    id: float
    code: str
    name: str
    description: str
    is_ready: bool
    control_number: Union[None, Unset, float] = UNSET
    archived_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        description = self.description

        is_ready = self.is_ready

        control_number: Union[None, Unset, float]
        if isinstance(self.control_number, Unset):
            control_number = UNSET
        else:
            control_number = self.control_number

        archived_at: Union[None, Unset, str]
        if isinstance(self.archived_at, Unset):
            archived_at = UNSET
        elif isinstance(self.archived_at, datetime.datetime):
            archived_at = self.archived_at.isoformat()
        else:
            archived_at = self.archived_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "description": description,
                "isReady": is_ready,
            }
        )
        if control_number is not UNSET:
            field_dict["controlNumber"] = control_number
        if archived_at is not UNSET:
            field_dict["archivedAt"] = archived_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        description = d.pop("description")

        is_ready = d.pop("isReady")

        def _parse_control_number(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        control_number = _parse_control_number(d.pop("controlNumber", UNSET))

        def _parse_archived_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                archived_at_type_0 = isoparse(data)

                return archived_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        archived_at = _parse_archived_at(d.pop("archivedAt", UNSET))

        risk_control_response_public_dto = cls(
            id=id,
            code=code,
            name=name,
            description=description,
            is_ready=is_ready,
            control_number=control_number,
            archived_at=archived_at,
        )

        risk_control_response_public_dto.additional_properties = d
        return risk_control_response_public_dto

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
