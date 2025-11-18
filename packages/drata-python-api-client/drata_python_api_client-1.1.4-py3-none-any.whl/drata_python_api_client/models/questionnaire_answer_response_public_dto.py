from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="QuestionnaireAnswerResponsePublicDto")


@_attrs_define
class QuestionnaireAnswerResponsePublicDto:
    """
    Attributes:
        id (float): Questionnaire answer ID Example: 1.
        question (str): Questionnaire question Example: Is there a publicly available URL for your Privacy Policy?.
        answer (str): Questionnaire answer Example: Yes, you can get to this right here!.
        type_ (str): Questionnaire answer type
    """

    id: float
    question: str
    answer: str
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        question = self.question

        answer = self.answer

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "question": question,
                "answer": answer,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        question = d.pop("question")

        answer = d.pop("answer")

        type_ = d.pop("type")

        questionnaire_answer_response_public_dto = cls(
            id=id,
            question=question,
            answer=answer,
            type_=type_,
        )

        questionnaire_answer_response_public_dto.additional_properties = d
        return questionnaire_answer_response_public_dto

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
