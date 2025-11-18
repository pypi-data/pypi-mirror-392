from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.risk_response_public_dto import RiskResponsePublicDto


T = TypeVar("T", bound="RisksResponsePublicDto")


@_attrs_define
class RisksResponsePublicDto:
    """
    Attributes:
        risks (list['RiskResponsePublicDto']): Risks
    """

    risks: list["RiskResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        risks = []
        for risks_item_data in self.risks:
            risks_item = risks_item_data.to_dict()
            risks.append(risks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "risks": risks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.risk_response_public_dto import RiskResponsePublicDto

        d = dict(src_dict)
        risks = []
        _risks = d.pop("risks")
        for risks_item_data in _risks:
            risks_item = RiskResponsePublicDto.from_dict(risks_item_data)

            risks.append(risks_item)

        risks_response_public_dto = cls(
            risks=risks,
        )

        risks_response_public_dto.additional_properties = d
        return risks_response_public_dto

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
