import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_response_public_dto import PolicyResponsePublicDto
    from ..models.policy_version_response_public_dto import PolicyVersionResponsePublicDto


T = TypeVar("T", bound="UserPolicyVersionResponsePublicDto")


@_attrs_define
class UserPolicyVersionResponsePublicDto:
    """
    Attributes:
        id (float): User policy version ID Example: 1.
        policy_version (PolicyVersionResponsePublicDto):
        policy (PolicyResponsePublicDto):
        accepted_at (Union[None, Unset, datetime.datetime]): User policy version accepted at date timestamp Example:
            2025-07-01T16:45:55.246Z.
    """

    id: float
    policy_version: "PolicyVersionResponsePublicDto"
    policy: "PolicyResponsePublicDto"
    accepted_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        policy_version = self.policy_version.to_dict()

        policy = self.policy.to_dict()

        accepted_at: Union[None, Unset, str]
        if isinstance(self.accepted_at, Unset):
            accepted_at = UNSET
        elif isinstance(self.accepted_at, datetime.datetime):
            accepted_at = self.accepted_at.isoformat()
        else:
            accepted_at = self.accepted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "policyVersion": policy_version,
                "policy": policy,
            }
        )
        if accepted_at is not UNSET:
            field_dict["acceptedAt"] = accepted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_response_public_dto import PolicyResponsePublicDto
        from ..models.policy_version_response_public_dto import PolicyVersionResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        policy_version = PolicyVersionResponsePublicDto.from_dict(d.pop("policyVersion"))

        policy = PolicyResponsePublicDto.from_dict(d.pop("policy"))

        def _parse_accepted_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                accepted_at_type_0 = isoparse(data)

                return accepted_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        accepted_at = _parse_accepted_at(d.pop("acceptedAt", UNSET))

        user_policy_version_response_public_dto = cls(
            id=id,
            policy_version=policy_version,
            policy=policy,
            accepted_at=accepted_at,
        )

        user_policy_version_response_public_dto.additional_properties = d
        return user_policy_version_response_public_dto

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
