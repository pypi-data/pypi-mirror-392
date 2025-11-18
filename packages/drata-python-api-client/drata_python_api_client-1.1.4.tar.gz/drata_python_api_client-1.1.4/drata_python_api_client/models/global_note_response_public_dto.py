import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.user_card_response_public_dto import UserCardResponsePublicDto


T = TypeVar("T", bound="GlobalNoteResponsePublicDto")


@_attrs_define
class GlobalNoteResponsePublicDto:
    """
    Attributes:
        id (float): Note ID Example: 1.
        comment (str): The comment of the note Example: Good comment.
        created_at (datetime.datetime): Note created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Note updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        owner (UserCardResponsePublicDto):
    """

    id: float
    comment: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: "UserCardResponsePublicDto"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        comment = self.comment

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        owner = self.owner.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "comment": comment,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "owner": owner,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_card_response_public_dto import UserCardResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        comment = d.pop("comment")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        owner = UserCardResponsePublicDto.from_dict(d.pop("owner"))

        global_note_response_public_dto = cls(
            id=id,
            comment=comment,
            created_at=created_at,
            updated_at=updated_at,
            owner=owner,
        )

        global_note_response_public_dto.additional_properties = d
        return global_note_response_public_dto

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
