from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.questionnaire_vendor_response_public_dto import QuestionnaireVendorResponsePublicDto


T = TypeVar("T", bound="QuestionnairesVendorsResponsePublicDto")


@_attrs_define
class QuestionnairesVendorsResponsePublicDto:
    """
    Attributes:
        questionnaires_vendors (list['QuestionnaireVendorResponsePublicDto']): List of questionnaire formIds sent to a
            vendor
    """

    questionnaires_vendors: list["QuestionnaireVendorResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        questionnaires_vendors = []
        for questionnaires_vendors_item_data in self.questionnaires_vendors:
            questionnaires_vendors_item = questionnaires_vendors_item_data.to_dict()
            questionnaires_vendors.append(questionnaires_vendors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "questionnairesVendors": questionnaires_vendors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.questionnaire_vendor_response_public_dto import QuestionnaireVendorResponsePublicDto

        d = dict(src_dict)
        questionnaires_vendors = []
        _questionnaires_vendors = d.pop("questionnairesVendors")
        for questionnaires_vendors_item_data in _questionnaires_vendors:
            questionnaires_vendors_item = QuestionnaireVendorResponsePublicDto.from_dict(
                questionnaires_vendors_item_data
            )

            questionnaires_vendors.append(questionnaires_vendors_item)

        questionnaires_vendors_response_public_dto = cls(
            questionnaires_vendors=questionnaires_vendors,
        )

        questionnaires_vendors_response_public_dto.additional_properties = d
        return questionnaires_vendors_response_public_dto

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
