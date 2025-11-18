from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ticket_create_response_public_dto_transition_type_0 import (
        TicketCreateResponsePublicDtoTransitionType0,
    )


T = TypeVar("T", bound="TicketCreateResponsePublicDto")


@_attrs_define
class TicketCreateResponsePublicDto:
    """
    Attributes:
        key (str): Issue key Example: SF-332.
        self_ (str): Issue self Example:
            https://api.atlassian.com/ex/jira/97b4114f-0065-4a2b-a9e0-8a37cae80ddd/rest/api/3/issue/42210.
        transition (Union['TicketCreateResponsePublicDtoTransitionType0', None]): Issue transition
    """

    key: str
    self_: str
    transition: Union["TicketCreateResponsePublicDtoTransitionType0", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ticket_create_response_public_dto_transition_type_0 import (
            TicketCreateResponsePublicDtoTransitionType0,
        )

        key = self.key

        self_ = self.self_

        transition: Union[None, dict[str, Any]]
        if isinstance(self.transition, TicketCreateResponsePublicDtoTransitionType0):
            transition = self.transition.to_dict()
        else:
            transition = self.transition

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "self": self_,
                "transition": transition,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ticket_create_response_public_dto_transition_type_0 import (
            TicketCreateResponsePublicDtoTransitionType0,
        )

        d = dict(src_dict)
        key = d.pop("key")

        self_ = d.pop("self")

        def _parse_transition(data: object) -> Union["TicketCreateResponsePublicDtoTransitionType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transition_type_0 = TicketCreateResponsePublicDtoTransitionType0.from_dict(data)

                return transition_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TicketCreateResponsePublicDtoTransitionType0", None], data)

        transition = _parse_transition(d.pop("transition"))

        ticket_create_response_public_dto = cls(
            key=key,
            self_=self_,
            transition=transition,
        )

        ticket_create_response_public_dto.additional_properties = d
        return ticket_create_response_public_dto

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
