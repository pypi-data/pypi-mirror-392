from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VendorDirectoryResponsePublicDtoLastQuestionnaireType0")


@_attrs_define
class VendorDirectoryResponsePublicDtoLastQuestionnaireType0:
    """The last questionnaire associated with the vendor

    Attributes:
        vendor_id (Union[Unset, float]):
        send_at (Union[Unset, str]):
        sent_email (Union[Unset, str]):
        file (Union[Unset, str]):
        responded_at (Union[Unset, str]):
        response_id (Union[Unset, float]):
        is_manual_upload (Union[Unset, bool]):
        completed_by (Union[Unset, str]):
    """

    vendor_id: Union[Unset, float] = UNSET
    send_at: Union[Unset, str] = UNSET
    sent_email: Union[Unset, str] = UNSET
    file: Union[Unset, str] = UNSET
    responded_at: Union[Unset, str] = UNSET
    response_id: Union[Unset, float] = UNSET
    is_manual_upload: Union[Unset, bool] = UNSET
    completed_by: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vendor_id = self.vendor_id

        send_at = self.send_at

        sent_email = self.sent_email

        file = self.file

        responded_at = self.responded_at

        response_id = self.response_id

        is_manual_upload = self.is_manual_upload

        completed_by = self.completed_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vendor_id is not UNSET:
            field_dict["vendorId"] = vendor_id
        if send_at is not UNSET:
            field_dict["sendAt"] = send_at
        if sent_email is not UNSET:
            field_dict["sentEmail"] = sent_email
        if file is not UNSET:
            field_dict["file"] = file
        if responded_at is not UNSET:
            field_dict["respondedAt"] = responded_at
        if response_id is not UNSET:
            field_dict["responseId"] = response_id
        if is_manual_upload is not UNSET:
            field_dict["isManualUpload"] = is_manual_upload
        if completed_by is not UNSET:
            field_dict["completedBy"] = completed_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vendor_id = d.pop("vendorId", UNSET)

        send_at = d.pop("sendAt", UNSET)

        sent_email = d.pop("sentEmail", UNSET)

        file = d.pop("file", UNSET)

        responded_at = d.pop("respondedAt", UNSET)

        response_id = d.pop("responseId", UNSET)

        is_manual_upload = d.pop("isManualUpload", UNSET)

        completed_by = d.pop("completedBy", UNSET)

        vendor_directory_response_public_dto_last_questionnaire_type_0 = cls(
            vendor_id=vendor_id,
            send_at=send_at,
            sent_email=sent_email,
            file=file,
            responded_at=responded_at,
            response_id=response_id,
            is_manual_upload=is_manual_upload,
            completed_by=completed_by,
        )

        vendor_directory_response_public_dto_last_questionnaire_type_0.additional_properties = d
        return vendor_directory_response_public_dto_last_questionnaire_type_0

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
