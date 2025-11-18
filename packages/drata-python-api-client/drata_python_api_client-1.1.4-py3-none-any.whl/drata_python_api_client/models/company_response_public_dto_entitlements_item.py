from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.company_response_public_dto_entitlements_item_metadata import (
        CompanyResponsePublicDtoEntitlementsItemMetadata,
    )


T = TypeVar("T", bound="CompanyResponsePublicDtoEntitlementsItem")


@_attrs_define
class CompanyResponsePublicDtoEntitlementsItem:
    """
    Attributes:
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        type_ (Union[Unset, str]):
        feature_id (Union[None, Unset, float]):
        metadata (Union[Unset, CompanyResponsePublicDtoEntitlementsItemMetadata]):
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    feature_id: Union[None, Unset, float] = UNSET
    metadata: Union[Unset, "CompanyResponsePublicDtoEntitlementsItemMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        type_ = self.type_

        feature_id: Union[None, Unset, float]
        if isinstance(self.feature_id, Unset):
            feature_id = UNSET
        else:
            feature_id = self.feature_id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if type_ is not UNSET:
            field_dict["type"] = type_
        if feature_id is not UNSET:
            field_dict["featureId"] = feature_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.company_response_public_dto_entitlements_item_metadata import (
            CompanyResponsePublicDtoEntitlementsItemMetadata,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        type_ = d.pop("type", UNSET)

        def _parse_feature_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        feature_id = _parse_feature_id(d.pop("featureId", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CompanyResponsePublicDtoEntitlementsItemMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CompanyResponsePublicDtoEntitlementsItemMetadata.from_dict(_metadata)

        company_response_public_dto_entitlements_item = cls(
            name=name,
            description=description,
            type_=type_,
            feature_id=feature_id,
            metadata=metadata,
        )

        company_response_public_dto_entitlements_item.additional_properties = d
        return company_response_public_dto_entitlements_item

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
