from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateCustomerRequestDetailsRequestPublicDto")


@_attrs_define
class UpdateCustomerRequestDetailsRequestPublicDto:
    """
    Attributes:
        title (str): Customer request details title Example: 000001.
        owner_ids (list[float]): Array of owner ids Example: [1, 2, 3].
        description (Union[Unset, str]): Customer request details description Example: This is the description.
    """

    title: str
    owner_ids: list[float]
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        owner_ids = self.owner_ids

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "ownerIds": owner_ids,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        owner_ids = cast(list[float], d.pop("ownerIds"))

        description = d.pop("description", UNSET)

        update_customer_request_details_request_public_dto = cls(
            title=title,
            owner_ids=owner_ids,
            description=description,
        )

        update_customer_request_details_request_public_dto.additional_properties = d
        return update_customer_request_details_request_public_dto

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
