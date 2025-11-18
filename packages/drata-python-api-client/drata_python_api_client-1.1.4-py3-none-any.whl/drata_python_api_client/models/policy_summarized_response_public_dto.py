import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.group_response_public_dto import GroupResponsePublicDto
    from ..models.policy_owner_response_public_dto import PolicyOwnerResponsePublicDto


T = TypeVar("T", bound="PolicySummarizedResponsePublicDto")


@_attrs_define
class PolicySummarizedResponsePublicDto:
    """
    Attributes:
        id (float): The policy ID Example: 1.
        current_version_id (Union[None, float]): The current policy version ID Example: 1.
        name (str): The policy name Example: Acceptable Use Policy.
        version (Union[None, str]): The policy version Example: 1.
        minor_version (Union[None, str]): The policy minor version Example: 1.
        created_at (datetime.datetime): Policy created date timestamp Example: 2025-07-01T16:45:55.246Z.
        approved_at (Union[None, datetime.datetime]): Policy version approved at date timestamp Example:
            2025-07-01T16:45:55.246Z.
        renewal_date (Union[None, str]): Policy without version's renewal date Example: 2025-07-01T16:45:55.246Z.
        has_sla (str): Policy has SLA? Yes | No Example: Yes.
        current_owner (Union['PolicyOwnerResponsePublicDto', None]): The user that is assigned as the owner of this
            policy
        groups (list['GroupResponsePublicDto']): The identity groups assigned to the policy
        html_last_updated (Union[None, datetime.datetime]): Last time the html was saved to the DB Example:
            2025-07-01T16:45:55.246Z.
        status (Union[None, str]): Current policy version status Example: APPROVED.
        published_at (Union[None, datetime.datetime]): Current policy version published at date Example:
            2025-07-01T16:45:55.246Z.
    """

    id: float
    current_version_id: Union[None, float]
    name: str
    version: Union[None, str]
    minor_version: Union[None, str]
    created_at: datetime.datetime
    approved_at: Union[None, datetime.datetime]
    renewal_date: Union[None, str]
    has_sla: str
    current_owner: Union["PolicyOwnerResponsePublicDto", None]
    groups: list["GroupResponsePublicDto"]
    html_last_updated: Union[None, datetime.datetime]
    status: Union[None, str]
    published_at: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.policy_owner_response_public_dto import PolicyOwnerResponsePublicDto

        id = self.id

        current_version_id: Union[None, float]
        current_version_id = self.current_version_id

        name = self.name

        version: Union[None, str]
        version = self.version

        minor_version: Union[None, str]
        minor_version = self.minor_version

        created_at = self.created_at.isoformat()

        approved_at: Union[None, str]
        if isinstance(self.approved_at, datetime.datetime):
            approved_at = self.approved_at.isoformat()
        else:
            approved_at = self.approved_at

        renewal_date: Union[None, str]
        renewal_date = self.renewal_date

        has_sla = self.has_sla

        current_owner: Union[None, dict[str, Any]]
        if isinstance(self.current_owner, PolicyOwnerResponsePublicDto):
            current_owner = self.current_owner.to_dict()
        else:
            current_owner = self.current_owner

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        html_last_updated: Union[None, str]
        if isinstance(self.html_last_updated, datetime.datetime):
            html_last_updated = self.html_last_updated.isoformat()
        else:
            html_last_updated = self.html_last_updated

        status: Union[None, str]
        status = self.status

        published_at: Union[None, str]
        if isinstance(self.published_at, datetime.datetime):
            published_at = self.published_at.isoformat()
        else:
            published_at = self.published_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "currentVersionId": current_version_id,
                "name": name,
                "version": version,
                "minorVersion": minor_version,
                "createdAt": created_at,
                "approvedAt": approved_at,
                "renewalDate": renewal_date,
                "hasSla": has_sla,
                "currentOwner": current_owner,
                "groups": groups,
                "htmlLastUpdated": html_last_updated,
                "status": status,
                "publishedAt": published_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_response_public_dto import GroupResponsePublicDto
        from ..models.policy_owner_response_public_dto import PolicyOwnerResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        def _parse_current_version_id(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        current_version_id = _parse_current_version_id(d.pop("currentVersionId"))

        name = d.pop("name")

        def _parse_version(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        version = _parse_version(d.pop("version"))

        def _parse_minor_version(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        minor_version = _parse_minor_version(d.pop("minorVersion"))

        created_at = isoparse(d.pop("createdAt"))

        def _parse_approved_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                approved_at_type_0 = isoparse(data)

                return approved_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        approved_at = _parse_approved_at(d.pop("approvedAt"))

        def _parse_renewal_date(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        renewal_date = _parse_renewal_date(d.pop("renewalDate"))

        has_sla = d.pop("hasSla")

        def _parse_current_owner(data: object) -> Union["PolicyOwnerResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                current_owner_type_1 = PolicyOwnerResponsePublicDto.from_dict(data)

                return current_owner_type_1
            except:  # noqa: E722
                pass
            return cast(Union["PolicyOwnerResponsePublicDto", None], data)

        current_owner = _parse_current_owner(d.pop("currentOwner"))

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = GroupResponsePublicDto.from_dict(groups_item_data)

            groups.append(groups_item)

        def _parse_html_last_updated(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                html_last_updated_type_0 = isoparse(data)

                return html_last_updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        html_last_updated = _parse_html_last_updated(d.pop("htmlLastUpdated"))

        def _parse_status(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        status = _parse_status(d.pop("status"))

        def _parse_published_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                published_at_type_0 = isoparse(data)

                return published_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        published_at = _parse_published_at(d.pop("publishedAt"))

        policy_summarized_response_public_dto = cls(
            id=id,
            current_version_id=current_version_id,
            name=name,
            version=version,
            minor_version=minor_version,
            created_at=created_at,
            approved_at=approved_at,
            renewal_date=renewal_date,
            has_sla=has_sla,
            current_owner=current_owner,
            groups=groups,
            html_last_updated=html_last_updated,
            status=status,
            published_at=published_at,
        )

        policy_summarized_response_public_dto.additional_properties = d
        return policy_summarized_response_public_dto

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
