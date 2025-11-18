from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.copy_risks_from_library_request_public_dto_bulk_action_type import (
    CopyRisksFromLibraryRequestPublicDtoBulkActionType,
)
from ..models.copy_risks_from_library_request_public_dto_risk_groups_item import (
    CopyRisksFromLibraryRequestPublicDtoRiskGroupsItem,
)

T = TypeVar("T", bound="CopyRisksFromLibraryRequestPublicDto")


@_attrs_define
class CopyRisksFromLibraryRequestPublicDto:
    """
    Attributes:
        bulk_action_type (CopyRisksFromLibraryRequestPublicDtoBulkActionType): The copy action to perform on from risk
            library to the risk module. Example: COPY_BY_IDS.
        risks_ids (list[str]): An array of the risks ids that you want to copy from risk library to the risk module.
            Example: ['AA-01', 'AA-02', 'AA-03'].
        risk_groups (list[CopyRisksFromLibraryRequestPublicDtoRiskGroupsItem]): An array of the risk groups that you
            want to copy from risk library to the risk module. Example: ['CLOUD_ENVIRONMENT'].
    """

    bulk_action_type: CopyRisksFromLibraryRequestPublicDtoBulkActionType
    risks_ids: list[str]
    risk_groups: list[CopyRisksFromLibraryRequestPublicDtoRiskGroupsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bulk_action_type = self.bulk_action_type.value

        risks_ids = self.risks_ids

        risk_groups = []
        for risk_groups_item_data in self.risk_groups:
            risk_groups_item = risk_groups_item_data.value
            risk_groups.append(risk_groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bulkActionType": bulk_action_type,
                "risksIds": risks_ids,
                "riskGroups": risk_groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bulk_action_type = CopyRisksFromLibraryRequestPublicDtoBulkActionType(d.pop("bulkActionType"))

        risks_ids = cast(list[str], d.pop("risksIds"))

        risk_groups = []
        _risk_groups = d.pop("riskGroups")
        for risk_groups_item_data in _risk_groups:
            risk_groups_item = CopyRisksFromLibraryRequestPublicDtoRiskGroupsItem(risk_groups_item_data)

            risk_groups.append(risk_groups_item)

        copy_risks_from_library_request_public_dto = cls(
            bulk_action_type=bulk_action_type,
            risks_ids=risks_ids,
            risk_groups=risk_groups,
        )

        copy_risks_from_library_request_public_dto.additional_properties = d
        return copy_risks_from_library_request_public_dto

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
