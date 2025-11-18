from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.device_response_v11_public_dto import DeviceResponseV11PublicDto


T = TypeVar("T", bound="DevicesPaginatedResponsePublicDto")


@_attrs_define
class DevicesPaginatedResponsePublicDto:
    """
    Attributes:
        data (list['DeviceResponseV11PublicDto']): Get list of devices based on pagination limits Example:
            [{'externalId': '3000', 'personnelId': 206, 'userId': 207, 'id': 3, 'osVersion': 'MacOS 11', 'serialNumber':
            'q77gfdp0xg03vcu6t1fi', 'model': 'MacBook Pro 14-in(2021)', 'macAddress': '91:2b:4a:7a:51:73',
            'encryptionEnabled': None, 'firewallEnabled': None, 'gateKeeperEnabled': None, 'lastCheckedAt':
            '2024-11-25T22:16:23.479Z', 'sourceType': 'AGENT', 'createdAt': '2024-11-25T22:16:23.479Z', 'updatedAt':
            '2024-12-08T22:20:15.041Z', 'deletedAt': None, 'appsCount': None}, {'externalId': '4000', 'personnelId': 305,
            'userId': 306, 'id': 4, 'osVersion': 'MacOS 12', 'serialNumber': 'locldk8eyxn28eyb3ktj', 'model': 'MacBook Pro
            16-in(2021)', 'macAddress': '0f:8a:67:b2:90:ad', 'encryptionEnabled': None, 'firewallEnabled': None,
            'gateKeeperEnabled': None, 'lastCheckedAt': '2024-11-25T22:16:23.705Z', 'sourceType': 'AGENT', 'createdAt':
            '2024-11-25T22:16:23.705Z', 'updatedAt': '2024-12-08T22:20:15.041Z', 'deletedAt': None, 'appsCount': None}].
        page (float): Which page of data are you requesting Example: 1.
        limit (float): How many items are you requesting Example: 10.
        total (float): How many items are in the overall set Example: 100.
    """

    data: list["DeviceResponseV11PublicDto"]
    page: float
    limit: float
    total: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        page = self.page

        limit = self.limit

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "page": page,
                "limit": limit,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_response_v11_public_dto import DeviceResponseV11PublicDto

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = DeviceResponseV11PublicDto.from_dict(data_item_data)

            data.append(data_item)

        page = d.pop("page")

        limit = d.pop("limit")

        total = d.pop("total")

        devices_paginated_response_public_dto = cls(
            data=data,
            page=page,
            limit=limit,
            total=total,
        )

        devices_paginated_response_public_dto.additional_properties = d
        return devices_paginated_response_public_dto

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
