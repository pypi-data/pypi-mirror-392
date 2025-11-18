from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.questionnaire_answer_response_public_dto import QuestionnaireAnswerResponsePublicDto


T = TypeVar("T", bound="QuestionnaireResponseResponsePublicDto")


@_attrs_define
class QuestionnaireResponseResponsePublicDto:
    """
    Attributes:
        answers (list['QuestionnaireAnswerResponsePublicDto']): Questionnaire answers
    """

    answers: list["QuestionnaireAnswerResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        answers = []
        for answers_item_data in self.answers:
            answers_item = answers_item_data.to_dict()
            answers.append(answers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "answers": answers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.questionnaire_answer_response_public_dto import QuestionnaireAnswerResponsePublicDto

        d = dict(src_dict)
        answers = []
        _answers = d.pop("answers")
        for answers_item_data in _answers:
            answers_item = QuestionnaireAnswerResponsePublicDto.from_dict(answers_item_data)

            answers.append(answers_item)

        questionnaire_response_response_public_dto = cls(
            answers=answers,
        )

        questionnaire_response_response_public_dto.additional_properties = d
        return questionnaire_response_response_public_dto

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
