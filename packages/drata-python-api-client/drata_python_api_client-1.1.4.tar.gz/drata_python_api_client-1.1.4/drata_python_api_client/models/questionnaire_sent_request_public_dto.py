from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="QuestionnaireSentRequestPublicDto")


@_attrs_define
class QuestionnaireSentRequestPublicDto:
    """
    Attributes:
        email (str): The email address to receive the questionnaire Example: wc@drata.com.
        questionnaire_id (float): Vendor questionnaire ID Example: 1.
        email_content (str): The email content for the vendor Example: Hi,

            We'd like to conduct a security review and would like some information from you. Use this link to complete the
            questionnaire.

            Thank you..
    """

    email: str
    questionnaire_id: float
    email_content: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        questionnaire_id = self.questionnaire_id

        email_content = self.email_content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "questionnaireId": questionnaire_id,
                "emailContent": email_content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        questionnaire_id = d.pop("questionnaireId")

        email_content = d.pop("emailContent")

        questionnaire_sent_request_public_dto = cls(
            email=email,
            questionnaire_id=questionnaire_id,
            email_content=email_content,
        )

        questionnaire_sent_request_public_dto.additional_properties = d
        return questionnaire_sent_request_public_dto

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
