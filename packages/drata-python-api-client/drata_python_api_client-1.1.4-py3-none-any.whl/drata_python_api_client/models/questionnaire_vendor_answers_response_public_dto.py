from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.questionnaire_response_response_public_dto import QuestionnaireResponseResponsePublicDto


T = TypeVar("T", bound="QuestionnaireVendorAnswersResponsePublicDto")


@_attrs_define
class QuestionnaireVendorAnswersResponsePublicDto:
    """
    Attributes:
        responses (list['QuestionnaireResponseResponsePublicDto']): Questionnaire responses
    """

    responses: list["QuestionnaireResponseResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        responses = []
        for responses_item_data in self.responses:
            responses_item = responses_item_data.to_dict()
            responses.append(responses_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "responses": responses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.questionnaire_response_response_public_dto import QuestionnaireResponseResponsePublicDto

        d = dict(src_dict)
        responses = []
        _responses = d.pop("responses")
        for responses_item_data in _responses:
            responses_item = QuestionnaireResponseResponsePublicDto.from_dict(responses_item_data)

            responses.append(responses_item)

        questionnaire_vendor_answers_response_public_dto = cls(
            responses=responses,
        )

        questionnaire_vendor_answers_response_public_dto.additional_properties = d
        return questionnaire_vendor_answers_response_public_dto

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
