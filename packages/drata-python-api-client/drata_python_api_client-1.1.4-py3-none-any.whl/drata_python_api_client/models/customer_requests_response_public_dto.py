from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.customer_request_list_response_public_dto import CustomerRequestListResponsePublicDto


T = TypeVar("T", bound="CustomerRequestsResponsePublicDto")


@_attrs_define
class CustomerRequestsResponsePublicDto:
    """
    Attributes:
        total_unread_messages (float): Total of unread messages Example: 12.
        requests (CustomerRequestListResponsePublicDto):
    """

    total_unread_messages: float
    requests: "CustomerRequestListResponsePublicDto"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_unread_messages = self.total_unread_messages

        requests = self.requests.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "totalUnreadMessages": total_unread_messages,
                "requests": requests,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_request_list_response_public_dto import CustomerRequestListResponsePublicDto

        d = dict(src_dict)
        total_unread_messages = d.pop("totalUnreadMessages")

        requests = CustomerRequestListResponsePublicDto.from_dict(d.pop("requests"))

        customer_requests_response_public_dto = cls(
            total_unread_messages=total_unread_messages,
            requests=requests,
        )

        customer_requests_response_public_dto.additional_properties = d
        return customer_requests_response_public_dto

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
