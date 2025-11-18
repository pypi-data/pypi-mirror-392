from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DashboardResponsePublicDtoRiskHeatmapItem")


@_attrs_define
class DashboardResponsePublicDtoRiskHeatmapItem:
    """
    Attributes:
        impact (Union[Unset, float]):
        total (Union[Unset, float]):
        likelihood (Union[Unset, float]):
    """

    impact: Union[Unset, float] = UNSET
    total: Union[Unset, float] = UNSET
    likelihood: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        impact = self.impact

        total = self.total

        likelihood = self.likelihood

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if impact is not UNSET:
            field_dict["impact"] = impact
        if total is not UNSET:
            field_dict["total"] = total
        if likelihood is not UNSET:
            field_dict["likelihood"] = likelihood

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        impact = d.pop("impact", UNSET)

        total = d.pop("total", UNSET)

        likelihood = d.pop("likelihood", UNSET)

        dashboard_response_public_dto_risk_heatmap_item = cls(
            impact=impact,
            total=total,
            likelihood=likelihood,
        )

        dashboard_response_public_dto_risk_heatmap_item.additional_properties = d
        return dashboard_response_public_dto_risk_heatmap_item

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
