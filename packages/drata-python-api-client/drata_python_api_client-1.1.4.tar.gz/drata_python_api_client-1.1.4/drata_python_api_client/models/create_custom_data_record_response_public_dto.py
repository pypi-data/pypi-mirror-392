import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_custom_data_record_response_public_dto_data import CreateCustomDataRecordResponsePublicDtoData
    from ..models.create_custom_data_record_response_public_dto_error import (
        CreateCustomDataRecordResponsePublicDtoError,
    )


T = TypeVar("T", bound="CreateCustomDataRecordResponsePublicDto")


@_attrs_define
class CreateCustomDataRecordResponsePublicDto:
    """
    Attributes:
        data (CreateCustomDataRecordResponsePublicDtoData): Custom data information
        id (Union[Unset, str]): Custom data internal id Example: 1.
        created_at (Union[Unset, datetime.datetime]): Custom data record date of creation Example:
            2025-07-01T16:45:55.246Z.
        updated_at (Union[Unset, datetime.datetime]): Custom data record date of last update Example:
            2025-07-01T16:45:55.246Z.
        status_code (Union[Unset, float]): Operation HTTP status code reference Example: 200.
        error (Union[Unset, CreateCustomDataRecordResponsePublicDtoError]): Error information
    """

    data: "CreateCustomDataRecordResponsePublicDtoData"
    id: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    status_code: Union[Unset, float] = UNSET
    error: Union[Unset, "CreateCustomDataRecordResponsePublicDtoError"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        id = self.id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        status_code = self.status_code

        error: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if status_code is not UNSET:
            field_dict["statusCode"] = status_code
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_custom_data_record_response_public_dto_data import (
            CreateCustomDataRecordResponsePublicDtoData,
        )
        from ..models.create_custom_data_record_response_public_dto_error import (
            CreateCustomDataRecordResponsePublicDtoError,
        )

        d = dict(src_dict)
        data = CreateCustomDataRecordResponsePublicDtoData.from_dict(d.pop("data"))

        id = d.pop("id", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        status_code = d.pop("statusCode", UNSET)

        _error = d.pop("error", UNSET)
        error: Union[Unset, CreateCustomDataRecordResponsePublicDtoError]
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = CreateCustomDataRecordResponsePublicDtoError.from_dict(_error)

        create_custom_data_record_response_public_dto = cls(
            data=data,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            status_code=status_code,
            error=error,
        )

        create_custom_data_record_response_public_dto.additional_properties = d
        return create_custom_data_record_response_public_dto

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
