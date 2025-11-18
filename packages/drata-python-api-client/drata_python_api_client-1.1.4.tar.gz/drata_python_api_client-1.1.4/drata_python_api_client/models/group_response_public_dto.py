from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GroupResponsePublicDto")


@_attrs_define
class GroupResponsePublicDto:
    """
    Attributes:
        id (float): Group ID Example: 1.
        name (str): The group name Example: Operations.
        description (str): The group description Example: This is an example.
        email (str): Owner email Example: email@email.com.
        external_id (str): External ID Example: 23kemoi23em.
        source (str): The string enum source Example: GOOGLE.
        domain (str): Domain of the group Example: email.com.
        type_ (str): Group type Example: GROUP.
        org_unit_path (str): Org unit path Example: asdas/qweqwe/asdasd.
        members_count (float): Members count Example: 10.
    """

    id: float
    name: str
    description: str
    email: str
    external_id: str
    source: str
    domain: str
    type_: str
    org_unit_path: str
    members_count: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        email = self.email

        external_id = self.external_id

        source = self.source

        domain = self.domain

        type_ = self.type_

        org_unit_path = self.org_unit_path

        members_count = self.members_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "email": email,
                "externalId": external_id,
                "source": source,
                "domain": domain,
                "type": type_,
                "orgUnitPath": org_unit_path,
                "membersCount": members_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        email = d.pop("email")

        external_id = d.pop("externalId")

        source = d.pop("source")

        domain = d.pop("domain")

        type_ = d.pop("type")

        org_unit_path = d.pop("orgUnitPath")

        members_count = d.pop("membersCount")

        group_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            email=email,
            external_id=external_id,
            source=source,
            domain=domain,
            type_=type_,
            org_unit_path=org_unit_path,
            members_count=members_count,
        )

        group_response_public_dto.additional_properties = d
        return group_response_public_dto

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
