from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_identity_response_public_dto import UserIdentityResponsePublicDto


T = TypeVar("T", bound="UserIdentitiesResponsePublicDto")


@_attrs_define
class UserIdentitiesResponsePublicDto:
    """
    Attributes:
        identities (list['UserIdentityResponsePublicDto']): List of identities
    """

    identities: list["UserIdentityResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identities = []
        for identities_item_data in self.identities:
            identities_item = identities_item_data.to_dict()
            identities.append(identities_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identities": identities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_identity_response_public_dto import UserIdentityResponsePublicDto

        d = dict(src_dict)
        identities = []
        _identities = d.pop("identities")
        for identities_item_data in _identities:
            identities_item = UserIdentityResponsePublicDto.from_dict(identities_item_data)

            identities.append(identities_item)

        user_identities_response_public_dto = cls(
            identities=identities,
        )

        user_identities_response_public_dto.additional_properties = d
        return user_identities_response_public_dto

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
