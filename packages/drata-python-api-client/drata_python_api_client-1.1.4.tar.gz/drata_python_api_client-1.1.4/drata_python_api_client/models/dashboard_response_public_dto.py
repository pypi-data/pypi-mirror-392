from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.dashboard_response_public_dto_category_breakdown_item import (
        DashboardResponsePublicDtoCategoryBreakdownItem,
    )
    from ..models.dashboard_response_public_dto_risk_heatmap_item import DashboardResponsePublicDtoRiskHeatmapItem
    from ..models.dashboard_response_public_dto_risk_posture import DashboardResponsePublicDtoRiskPosture
    from ..models.dashboard_response_public_dto_treatment_overview import DashboardResponsePublicDtoTreatmentOverview


T = TypeVar("T", bound="DashboardResponsePublicDto")


@_attrs_define
class DashboardResponsePublicDto:
    """
    Attributes:
        risk_posture (DashboardResponsePublicDtoRiskPosture): Count of risks grouped by severity Example: {'LOW': 23,
            'CRITICAL': 13}.
        treatment_overview (DashboardResponsePublicDtoTreatmentOverview): Count of risks grouped by treatment Example:
            {'ACCEPT': 23, 'TRANSFER': 13}.
        risk_heatmap (list['DashboardResponsePublicDtoRiskHeatmapItem']): The count of risks by impact and likelihood
            Example: [{'total': 11, 'impact': 2, 'likelihood': 2}].
        category_breakdown (list['DashboardResponsePublicDtoCategoryBreakdownItem']): The amount of assessed risks
            Example: [{'severity': {'MEDIUM': 1, 'CRITICAL': 2}, 'category': {'id': 2, 'name': 'Access Control'}}].
        scored (float): The amount of risks that have been scored Example: 63.
        remaining (float): The amount of risks that are not scored Example: 8.
    """

    risk_posture: "DashboardResponsePublicDtoRiskPosture"
    treatment_overview: "DashboardResponsePublicDtoTreatmentOverview"
    risk_heatmap: list["DashboardResponsePublicDtoRiskHeatmapItem"]
    category_breakdown: list["DashboardResponsePublicDtoCategoryBreakdownItem"]
    scored: float
    remaining: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        risk_posture = self.risk_posture.to_dict()

        treatment_overview = self.treatment_overview.to_dict()

        risk_heatmap = []
        for risk_heatmap_item_data in self.risk_heatmap:
            risk_heatmap_item = risk_heatmap_item_data.to_dict()
            risk_heatmap.append(risk_heatmap_item)

        category_breakdown = []
        for category_breakdown_item_data in self.category_breakdown:
            category_breakdown_item = category_breakdown_item_data.to_dict()
            category_breakdown.append(category_breakdown_item)

        scored = self.scored

        remaining = self.remaining

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "riskPosture": risk_posture,
                "treatmentOverview": treatment_overview,
                "riskHeatmap": risk_heatmap,
                "categoryBreakdown": category_breakdown,
                "scored": scored,
                "remaining": remaining,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard_response_public_dto_category_breakdown_item import (
            DashboardResponsePublicDtoCategoryBreakdownItem,
        )
        from ..models.dashboard_response_public_dto_risk_heatmap_item import DashboardResponsePublicDtoRiskHeatmapItem
        from ..models.dashboard_response_public_dto_risk_posture import DashboardResponsePublicDtoRiskPosture
        from ..models.dashboard_response_public_dto_treatment_overview import (
            DashboardResponsePublicDtoTreatmentOverview,
        )

        d = dict(src_dict)
        risk_posture = DashboardResponsePublicDtoRiskPosture.from_dict(d.pop("riskPosture"))

        treatment_overview = DashboardResponsePublicDtoTreatmentOverview.from_dict(d.pop("treatmentOverview"))

        risk_heatmap = []
        _risk_heatmap = d.pop("riskHeatmap")
        for risk_heatmap_item_data in _risk_heatmap:
            risk_heatmap_item = DashboardResponsePublicDtoRiskHeatmapItem.from_dict(risk_heatmap_item_data)

            risk_heatmap.append(risk_heatmap_item)

        category_breakdown = []
        _category_breakdown = d.pop("categoryBreakdown")
        for category_breakdown_item_data in _category_breakdown:
            category_breakdown_item = DashboardResponsePublicDtoCategoryBreakdownItem.from_dict(
                category_breakdown_item_data
            )

            category_breakdown.append(category_breakdown_item)

        scored = d.pop("scored")

        remaining = d.pop("remaining")

        dashboard_response_public_dto = cls(
            risk_posture=risk_posture,
            treatment_overview=treatment_overview,
            risk_heatmap=risk_heatmap,
            category_breakdown=category_breakdown,
            scored=scored,
            remaining=remaining,
        )

        dashboard_response_public_dto.additional_properties = d
        return dashboard_response_public_dto

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
