from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CompanyInfoResponsePublicDtoNda")


@_attrs_define
class CompanyInfoResponsePublicDtoNda:
    """NDA for Trust Page

    Example:
        {'name': 'NDA', 'file': 'https://drata.com/nda.pdf'}

    Attributes:
        name (Union[Unset, str]):
        file (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    file: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        file = self.file

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        file = d.pop("file", UNSET)

        company_info_response_public_dto_nda = cls(
            name=name,
            file=file,
        )

        company_info_response_public_dto_nda.additional_properties = d
        return company_info_response_public_dto_nda

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
