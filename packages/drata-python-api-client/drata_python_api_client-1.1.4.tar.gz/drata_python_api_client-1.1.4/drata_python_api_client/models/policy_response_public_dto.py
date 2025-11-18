import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_response_public_dto import GroupResponsePublicDto
    from ..models.policy_grace_period_sla_response_public_dto import PolicyGracePeriodSLAResponsePublicDto
    from ..models.policy_p3_matrix_sla_response_public_dto import PolicyP3MatrixSLAResponsePublicDto
    from ..models.policy_version_response_public_dto import PolicyVersionResponsePublicDto
    from ..models.policy_week_time_frame_sla_response_public_dto import PolicyWeekTimeFrameSLAResponsePublicDto
    from ..models.reminder_response_public_dto import ReminderResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="PolicyResponsePublicDto")


@_attrs_define
class PolicyResponsePublicDto:
    """
    Attributes:
        id (float): Policy ID Example: 1.
        template_id (Union[None, float]): The template id used to create this policy, null for custom policies Example:
            1.
        name (str): The policy name Example: Acceptable Use Policy.
        current_description (str): The current version's policy description Example: This policy defines how you do XYZ.
        html_last_updated (datetime.datetime): Last time the html was saved to the DB Example: 2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): Policy created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Policy last updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        current_owner (UserResponsePublicDto):
        versions (list['PolicyVersionResponsePublicDto']): The versions of the policy Example:
            PolicyVersionResponsePublicDto[].
        groups (list['GroupResponsePublicDto']): The identity groups assigned to the policy
        assigned_to (str): The type of policy scope Example: ALL.
        notify_groups (bool): Indicates if a notification to a group is send on the policy
        reminders (list['ReminderResponsePublicDto']): The set of incomplete reminders for this policy Example:
            ReminderResponsePublicDto[].
        policy_status (str): The current status of the policy (ACTIVE, ARCHIVED, REPLACED) Example: ACTIVE.
        policy_week_time_frame_sl_as (Union[Unset, list['PolicyWeekTimeFrameSLAResponsePublicDto']]): The set of policy
            week timeframe SLAs for this policy Example: PolicyWeekTimeFrameSLAResponsePublicDto[].
        policy_grace_period_sl_as (Union[Unset, list['PolicyGracePeriodSLAResponsePublicDto']]): The set of policy grace
            period SLAs for this policy Example: PolicyGracePeriodSLAResponsePublicDto[].
        policy_p3_matrix_sl_as (Union[Unset, list['PolicyP3MatrixSLAResponsePublicDto']]): The set of policy week
            timeframe SLAs for this policy Example: PolicyP3MatrixSLAResponsePublicDto[].
    """

    id: float
    template_id: Union[None, float]
    name: str
    current_description: str
    html_last_updated: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    current_owner: "UserResponsePublicDto"
    versions: list["PolicyVersionResponsePublicDto"]
    groups: list["GroupResponsePublicDto"]
    assigned_to: str
    notify_groups: bool
    reminders: list["ReminderResponsePublicDto"]
    policy_status: str
    policy_week_time_frame_sl_as: Union[Unset, list["PolicyWeekTimeFrameSLAResponsePublicDto"]] = UNSET
    policy_grace_period_sl_as: Union[Unset, list["PolicyGracePeriodSLAResponsePublicDto"]] = UNSET
    policy_p3_matrix_sl_as: Union[Unset, list["PolicyP3MatrixSLAResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        template_id: Union[None, float]
        template_id = self.template_id

        name = self.name

        current_description = self.current_description

        html_last_updated = self.html_last_updated.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        current_owner = self.current_owner.to_dict()

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        assigned_to = self.assigned_to

        notify_groups = self.notify_groups

        reminders = []
        for reminders_item_data in self.reminders:
            reminders_item = reminders_item_data.to_dict()
            reminders.append(reminders_item)

        policy_status = self.policy_status

        policy_week_time_frame_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policy_week_time_frame_sl_as, Unset):
            policy_week_time_frame_sl_as = []
            for policy_week_time_frame_sl_as_item_data in self.policy_week_time_frame_sl_as:
                policy_week_time_frame_sl_as_item = policy_week_time_frame_sl_as_item_data.to_dict()
                policy_week_time_frame_sl_as.append(policy_week_time_frame_sl_as_item)

        policy_grace_period_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policy_grace_period_sl_as, Unset):
            policy_grace_period_sl_as = []
            for policy_grace_period_sl_as_item_data in self.policy_grace_period_sl_as:
                policy_grace_period_sl_as_item = policy_grace_period_sl_as_item_data.to_dict()
                policy_grace_period_sl_as.append(policy_grace_period_sl_as_item)

        policy_p3_matrix_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policy_p3_matrix_sl_as, Unset):
            policy_p3_matrix_sl_as = []
            for policy_p3_matrix_sl_as_item_data in self.policy_p3_matrix_sl_as:
                policy_p3_matrix_sl_as_item = policy_p3_matrix_sl_as_item_data.to_dict()
                policy_p3_matrix_sl_as.append(policy_p3_matrix_sl_as_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "templateId": template_id,
                "name": name,
                "currentDescription": current_description,
                "htmlLastUpdated": html_last_updated,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "currentOwner": current_owner,
                "versions": versions,
                "groups": groups,
                "assignedTo": assigned_to,
                "notifyGroups": notify_groups,
                "reminders": reminders,
                "policyStatus": policy_status,
            }
        )
        if policy_week_time_frame_sl_as is not UNSET:
            field_dict["policyWeekTimeFrameSLAs"] = policy_week_time_frame_sl_as
        if policy_grace_period_sl_as is not UNSET:
            field_dict["policyGracePeriodSLAs"] = policy_grace_period_sl_as
        if policy_p3_matrix_sl_as is not UNSET:
            field_dict["policyP3MatrixSLAs"] = policy_p3_matrix_sl_as

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_response_public_dto import GroupResponsePublicDto
        from ..models.policy_grace_period_sla_response_public_dto import PolicyGracePeriodSLAResponsePublicDto
        from ..models.policy_p3_matrix_sla_response_public_dto import PolicyP3MatrixSLAResponsePublicDto
        from ..models.policy_version_response_public_dto import PolicyVersionResponsePublicDto
        from ..models.policy_week_time_frame_sla_response_public_dto import PolicyWeekTimeFrameSLAResponsePublicDto
        from ..models.reminder_response_public_dto import ReminderResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        def _parse_template_id(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        template_id = _parse_template_id(d.pop("templateId"))

        name = d.pop("name")

        current_description = d.pop("currentDescription")

        html_last_updated = isoparse(d.pop("htmlLastUpdated"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        current_owner = UserResponsePublicDto.from_dict(d.pop("currentOwner"))

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = PolicyVersionResponsePublicDto.from_dict(versions_item_data)

            versions.append(versions_item)

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = GroupResponsePublicDto.from_dict(groups_item_data)

            groups.append(groups_item)

        assigned_to = d.pop("assignedTo")

        notify_groups = d.pop("notifyGroups")

        reminders = []
        _reminders = d.pop("reminders")
        for reminders_item_data in _reminders:
            reminders_item = ReminderResponsePublicDto.from_dict(reminders_item_data)

            reminders.append(reminders_item)

        policy_status = d.pop("policyStatus")

        policy_week_time_frame_sl_as = []
        _policy_week_time_frame_sl_as = d.pop("policyWeekTimeFrameSLAs", UNSET)
        for policy_week_time_frame_sl_as_item_data in _policy_week_time_frame_sl_as or []:
            policy_week_time_frame_sl_as_item = PolicyWeekTimeFrameSLAResponsePublicDto.from_dict(
                policy_week_time_frame_sl_as_item_data
            )

            policy_week_time_frame_sl_as.append(policy_week_time_frame_sl_as_item)

        policy_grace_period_sl_as = []
        _policy_grace_period_sl_as = d.pop("policyGracePeriodSLAs", UNSET)
        for policy_grace_period_sl_as_item_data in _policy_grace_period_sl_as or []:
            policy_grace_period_sl_as_item = PolicyGracePeriodSLAResponsePublicDto.from_dict(
                policy_grace_period_sl_as_item_data
            )

            policy_grace_period_sl_as.append(policy_grace_period_sl_as_item)

        policy_p3_matrix_sl_as = []
        _policy_p3_matrix_sl_as = d.pop("policyP3MatrixSLAs", UNSET)
        for policy_p3_matrix_sl_as_item_data in _policy_p3_matrix_sl_as or []:
            policy_p3_matrix_sl_as_item = PolicyP3MatrixSLAResponsePublicDto.from_dict(policy_p3_matrix_sl_as_item_data)

            policy_p3_matrix_sl_as.append(policy_p3_matrix_sl_as_item)

        policy_response_public_dto = cls(
            id=id,
            template_id=template_id,
            name=name,
            current_description=current_description,
            html_last_updated=html_last_updated,
            created_at=created_at,
            updated_at=updated_at,
            current_owner=current_owner,
            versions=versions,
            groups=groups,
            assigned_to=assigned_to,
            notify_groups=notify_groups,
            reminders=reminders,
            policy_status=policy_status,
            policy_week_time_frame_sl_as=policy_week_time_frame_sl_as,
            policy_grace_period_sl_as=policy_grace_period_sl_as,
            policy_p3_matrix_sl_as=policy_p3_matrix_sl_as,
        )

        policy_response_public_dto.additional_properties = d
        return policy_response_public_dto

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
