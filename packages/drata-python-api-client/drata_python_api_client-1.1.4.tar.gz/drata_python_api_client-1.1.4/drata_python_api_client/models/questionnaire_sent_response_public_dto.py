import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="QuestionnaireSentResponsePublicDto")


@_attrs_define
class QuestionnaireSentResponsePublicDto:
    """
    Attributes:
        id (float): Questionnaire ID Example: 1.
        completed_by (Union[None, str]): Who answer the questionnaire Example: Acme.
        recipient_email (str): The email address to receive the questionnaire Example: wc@drata.com.
        is_completed (bool): The status of the questionnaire Example: true.
        date_sent (datetime.datetime): Date when the questionnaire was sent Example: 2025-07-01T16:45:55.246Z.
        is_manual_upload (bool): Flag to know if the file is a manual uploaded questionnaire Example: true.
        response_id (Union[None, float]): The questionnaire response id to the questionnaire data file Example: 1.
        title (Union[Unset, str]): Vendor questionnaire title Example: Vendor Questionnaire.
    """

    id: float
    completed_by: Union[None, str]
    recipient_email: str
    is_completed: bool
    date_sent: datetime.datetime
    is_manual_upload: bool
    response_id: Union[None, float]
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        completed_by: Union[None, str]
        completed_by = self.completed_by

        recipient_email = self.recipient_email

        is_completed = self.is_completed

        date_sent = self.date_sent.isoformat()

        is_manual_upload = self.is_manual_upload

        response_id: Union[None, float]
        response_id = self.response_id

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "completedBy": completed_by,
                "recipientEmail": recipient_email,
                "isCompleted": is_completed,
                "dateSent": date_sent,
                "isManualUpload": is_manual_upload,
                "responseId": response_id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_completed_by(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        completed_by = _parse_completed_by(d.pop("completedBy"))

        recipient_email = d.pop("recipientEmail")

        is_completed = d.pop("isCompleted")

        date_sent = isoparse(d.pop("dateSent"))

        is_manual_upload = d.pop("isManualUpload")

        def _parse_response_id(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        response_id = _parse_response_id(d.pop("responseId"))

        title = d.pop("title", UNSET)

        questionnaire_sent_response_public_dto = cls(
            id=id,
            completed_by=completed_by,
            recipient_email=recipient_email,
            is_completed=is_completed,
            date_sent=date_sent,
            is_manual_upload=is_manual_upload,
            response_id=response_id,
            title=title,
        )

        questionnaire_sent_response_public_dto.additional_properties = d
        return questionnaire_sent_response_public_dto

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
