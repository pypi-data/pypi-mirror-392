from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.personnel_data_public_dto import PersonnelDataPublicDto


T = TypeVar("T", bound="UpdateConnectionJsonIdpRequestPublicDto")


@_attrs_define
class UpdateConnectionJsonIdpRequestPublicDto:
    """
    Attributes:
        personnel_data (list['PersonnelDataPublicDto']): The list of personnel
    """

    personnel_data: list["PersonnelDataPublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        personnel_data = []
        for personnel_data_item_data in self.personnel_data:
            personnel_data_item = personnel_data_item_data.to_dict()
            personnel_data.append(personnel_data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "personnelData": personnel_data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.personnel_data_public_dto import PersonnelDataPublicDto

        d = dict(src_dict)
        personnel_data = []
        _personnel_data = d.pop("personnelData")
        for personnel_data_item_data in _personnel_data:
            personnel_data_item = PersonnelDataPublicDto.from_dict(personnel_data_item_data)

            personnel_data.append(personnel_data_item)

        update_connection_json_idp_request_public_dto = cls(
            personnel_data=personnel_data,
        )

        update_connection_json_idp_request_public_dto.additional_properties = d
        return update_connection_json_idp_request_public_dto

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
