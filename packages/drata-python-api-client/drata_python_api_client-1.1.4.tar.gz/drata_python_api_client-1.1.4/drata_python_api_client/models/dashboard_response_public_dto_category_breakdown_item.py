from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dashboard_response_public_dto_category_breakdown_item_category import (
        DashboardResponsePublicDtoCategoryBreakdownItemCategory,
    )
    from ..models.dashboard_response_public_dto_category_breakdown_item_severity import (
        DashboardResponsePublicDtoCategoryBreakdownItemSeverity,
    )


T = TypeVar("T", bound="DashboardResponsePublicDtoCategoryBreakdownItem")


@_attrs_define
class DashboardResponsePublicDtoCategoryBreakdownItem:
    """
    Attributes:
        category (Union[Unset, DashboardResponsePublicDtoCategoryBreakdownItemCategory]):
        severity (Union[Unset, DashboardResponsePublicDtoCategoryBreakdownItemSeverity]):
    """

    category: Union[Unset, "DashboardResponsePublicDtoCategoryBreakdownItemCategory"] = UNSET
    severity: Union[Unset, "DashboardResponsePublicDtoCategoryBreakdownItemSeverity"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        category: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.to_dict()

        severity: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if category is not UNSET:
            field_dict["category"] = category
        if severity is not UNSET:
            field_dict["severity"] = severity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard_response_public_dto_category_breakdown_item_category import (
            DashboardResponsePublicDtoCategoryBreakdownItemCategory,
        )
        from ..models.dashboard_response_public_dto_category_breakdown_item_severity import (
            DashboardResponsePublicDtoCategoryBreakdownItemSeverity,
        )

        d = dict(src_dict)
        _category = d.pop("category", UNSET)
        category: Union[Unset, DashboardResponsePublicDtoCategoryBreakdownItemCategory]
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = DashboardResponsePublicDtoCategoryBreakdownItemCategory.from_dict(_category)

        _severity = d.pop("severity", UNSET)
        severity: Union[Unset, DashboardResponsePublicDtoCategoryBreakdownItemSeverity]
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = DashboardResponsePublicDtoCategoryBreakdownItemSeverity.from_dict(_severity)

        dashboard_response_public_dto_category_breakdown_item = cls(
            category=category,
            severity=severity,
        )

        dashboard_response_public_dto_category_breakdown_item.additional_properties = d
        return dashboard_response_public_dto_category_breakdown_item

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
