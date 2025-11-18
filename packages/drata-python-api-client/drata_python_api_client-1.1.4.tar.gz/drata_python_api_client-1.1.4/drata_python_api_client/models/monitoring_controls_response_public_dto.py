from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.monitoring_controls_response_public_dto_controls import MonitoringControlsResponsePublicDtoControls


T = TypeVar("T", bound="MonitoringControlsResponsePublicDto")


@_attrs_define
class MonitoringControlsResponsePublicDto:
    """
    Attributes:
        is_sla_displayed (bool): SLA is or not displayed
        sla_time (float): Time of compliance
        controls (MonitoringControlsResponsePublicDtoControls): Controls of the tenant
    """

    is_sla_displayed: bool
    sla_time: float
    controls: "MonitoringControlsResponsePublicDtoControls"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_sla_displayed = self.is_sla_displayed

        sla_time = self.sla_time

        controls = self.controls.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isSLADisplayed": is_sla_displayed,
                "slaTime": sla_time,
                "controls": controls,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.monitoring_controls_response_public_dto_controls import (
            MonitoringControlsResponsePublicDtoControls,
        )

        d = dict(src_dict)
        is_sla_displayed = d.pop("isSLADisplayed")

        sla_time = d.pop("slaTime")

        controls = MonitoringControlsResponsePublicDtoControls.from_dict(d.pop("controls"))

        monitoring_controls_response_public_dto = cls(
            is_sla_displayed=is_sla_displayed,
            sla_time=sla_time,
            controls=controls,
        )

        monitoring_controls_response_public_dto.additional_properties = d
        return monitoring_controls_response_public_dto

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
