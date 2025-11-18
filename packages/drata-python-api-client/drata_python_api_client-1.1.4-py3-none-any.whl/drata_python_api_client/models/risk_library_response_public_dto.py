from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.risk_category_response_public_dto import RiskCategoryResponsePublicDto
    from ..models.risk_control_response_public_dto import RiskControlResponsePublicDto


T = TypeVar("T", bound="RiskLibraryResponsePublicDto")


@_attrs_define
class RiskLibraryResponsePublicDto:
    """
    Attributes:
        id (float): Risk Id Example: 1.
        risk_id (str): Human readable risk id Example: AC-04.
        title (str): Title of the risk Example: Password Management - Password Cracking.
        description (str): Description of the risk Example: An attacker attempts to gain access to organizational
            information by guessing of passwords..
        controls (list['RiskControlResponsePublicDto']): Controls attached to the risk
        categories (list['RiskCategoryResponsePublicDto']): Categories attached to the risk
    """

    id: float
    risk_id: str
    title: str
    description: str
    controls: list["RiskControlResponsePublicDto"]
    categories: list["RiskCategoryResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        risk_id = self.risk_id

        title = self.title

        description = self.description

        controls = []
        for controls_item_data in self.controls:
            controls_item = controls_item_data.to_dict()
            controls.append(controls_item)

        categories = []
        for categories_item_data in self.categories:
            categories_item = categories_item_data.to_dict()
            categories.append(categories_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "riskId": risk_id,
                "title": title,
                "description": description,
                "controls": controls,
                "categories": categories,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.risk_category_response_public_dto import RiskCategoryResponsePublicDto
        from ..models.risk_control_response_public_dto import RiskControlResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        risk_id = d.pop("riskId")

        title = d.pop("title")

        description = d.pop("description")

        controls = []
        _controls = d.pop("controls")
        for controls_item_data in _controls:
            controls_item = RiskControlResponsePublicDto.from_dict(controls_item_data)

            controls.append(controls_item)

        categories = []
        _categories = d.pop("categories")
        for categories_item_data in _categories:
            categories_item = RiskCategoryResponsePublicDto.from_dict(categories_item_data)

            categories.append(categories_item)

        risk_library_response_public_dto = cls(
            id=id,
            risk_id=risk_id,
            title=title,
            description=description,
            controls=controls,
            categories=categories,
        )

        risk_library_response_public_dto.additional_properties = d
        return risk_library_response_public_dto

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
