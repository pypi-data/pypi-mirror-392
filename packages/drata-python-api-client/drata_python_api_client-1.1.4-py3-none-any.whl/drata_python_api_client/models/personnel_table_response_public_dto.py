from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.personnel_details_table_response_public_dto import PersonnelDetailsTableResponsePublicDto
    from ..models.personnel_table_response_public_dto_data_all import PersonnelTableResponsePublicDtoDataAll


T = TypeVar("T", bound="PersonnelTableResponsePublicDto")


@_attrs_define
class PersonnelTableResponsePublicDto:
    """
    Attributes:
        data (list['PersonnelDetailsTableResponsePublicDto']): Data set based on the pagination limits
        page (float): Which page of data are you requesting Example: 1.
        limit (float): How many items are you requesting Example: 10.
        total (float): How many items are in the overall set Example: 100.
        data_all (PersonnelTableResponsePublicDtoDataAll): Object containing properties that apply to the whole no
            paginated set of data
    """

    data: list["PersonnelDetailsTableResponsePublicDto"]
    page: float
    limit: float
    total: float
    data_all: "PersonnelTableResponsePublicDtoDataAll"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        page = self.page

        limit = self.limit

        total = self.total

        data_all = self.data_all.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "page": page,
                "limit": limit,
                "total": total,
                "dataAll": data_all,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.personnel_details_table_response_public_dto import PersonnelDetailsTableResponsePublicDto
        from ..models.personnel_table_response_public_dto_data_all import PersonnelTableResponsePublicDtoDataAll

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = PersonnelDetailsTableResponsePublicDto.from_dict(data_item_data)

            data.append(data_item)

        page = d.pop("page")

        limit = d.pop("limit")

        total = d.pop("total")

        data_all = PersonnelTableResponsePublicDtoDataAll.from_dict(d.pop("dataAll"))

        personnel_table_response_public_dto = cls(
            data=data,
            page=page,
            limit=limit,
            total=total,
            data_all=data_all,
        )

        personnel_table_response_public_dto.additional_properties = d
        return personnel_table_response_public_dto

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
