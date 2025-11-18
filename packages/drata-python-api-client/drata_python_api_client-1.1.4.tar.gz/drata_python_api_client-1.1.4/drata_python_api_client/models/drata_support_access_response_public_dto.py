import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="DrataSupportAccessResponsePublicDto")


@_attrs_define
class DrataSupportAccessResponsePublicDto:
    """
    Attributes:
        enabled_at (datetime.datetime): When the admin enabled access for Drata Support Example:
            2025-07-01T16:45:55.246Z.
        expires_at (Union[None, datetime.datetime]): When the time window expires for Drata Support Example:
            2025-07-01T16:45:55.246Z.
        type_ (str): The type of access granted for Drata Support Example: READ_ONLY.
    """

    enabled_at: datetime.datetime
    expires_at: Union[None, datetime.datetime]
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled_at = self.enabled_at.isoformat()

        expires_at: Union[None, str]
        if isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enabledAt": enabled_at,
                "expiresAt": expires_at,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled_at = isoparse(d.pop("enabledAt"))

        def _parse_expires_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expiresAt"))

        type_ = d.pop("type")

        drata_support_access_response_public_dto = cls(
            enabled_at=enabled_at,
            expires_at=expires_at,
            type_=type_,
        )

        drata_support_access_response_public_dto.additional_properties = d
        return drata_support_access_response_public_dto

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
