from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DashboardResponsePublicDtoTreatmentOverview")


@_attrs_define
class DashboardResponsePublicDtoTreatmentOverview:
    """Count of risks grouped by treatment

    Example:
        {'ACCEPT': 23, 'TRANSFER': 13}

    Attributes:
        untreated (Union[Unset, float]):
        accept (Union[Unset, float]):
        transfer (Union[Unset, float]):
        avoid (Union[Unset, float]):
        mitigate (Union[Unset, float]):
    """

    untreated: Union[Unset, float] = UNSET
    accept: Union[Unset, float] = UNSET
    transfer: Union[Unset, float] = UNSET
    avoid: Union[Unset, float] = UNSET
    mitigate: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        untreated = self.untreated

        accept = self.accept

        transfer = self.transfer

        avoid = self.avoid

        mitigate = self.mitigate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if untreated is not UNSET:
            field_dict["UNTREATED"] = untreated
        if accept is not UNSET:
            field_dict["ACCEPT"] = accept
        if transfer is not UNSET:
            field_dict["TRANSFER"] = transfer
        if avoid is not UNSET:
            field_dict["AVOID"] = avoid
        if mitigate is not UNSET:
            field_dict["MITIGATE"] = mitigate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        untreated = d.pop("UNTREATED", UNSET)

        accept = d.pop("ACCEPT", UNSET)

        transfer = d.pop("TRANSFER", UNSET)

        avoid = d.pop("AVOID", UNSET)

        mitigate = d.pop("MITIGATE", UNSET)

        dashboard_response_public_dto_treatment_overview = cls(
            untreated=untreated,
            accept=accept,
            transfer=transfer,
            avoid=avoid,
            mitigate=mitigate,
        )

        dashboard_response_public_dto_treatment_overview.additional_properties = d
        return dashboard_response_public_dto_treatment_overview

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
