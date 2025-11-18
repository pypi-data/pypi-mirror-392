from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.request_owner_response_public_dto import RequestOwnerResponsePublicDto


T = TypeVar("T", bound="UpdateCustomerRequestDetailsResponsePublicDto")


@_attrs_define
class UpdateCustomerRequestDetailsResponsePublicDto:
    """
    Attributes:
        id (float): Customer request id Example: 1.
        code (str): Customer request details code Example: 000001.
        title (str): Customer request details title Example: This is the title.
        owners (list['RequestOwnerResponsePublicDto']): Customer List of owners
        description (Union[None, Unset, str]): Customer request details description Example: This is the description.
    """

    id: float
    code: str
    title: str
    owners: list["RequestOwnerResponsePublicDto"]
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        title = self.title

        owners = []
        for owners_item_data in self.owners:
            owners_item = owners_item_data.to_dict()
            owners.append(owners_item)

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "title": title,
                "owners": owners,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_owner_response_public_dto import RequestOwnerResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        title = d.pop("title")

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = RequestOwnerResponsePublicDto.from_dict(owners_item_data)

            owners.append(owners_item)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        update_customer_request_details_response_public_dto = cls(
            id=id,
            code=code,
            title=title,
            owners=owners,
            description=description,
        )

        update_customer_request_details_response_public_dto.additional_properties = d
        return update_customer_request_details_response_public_dto

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
