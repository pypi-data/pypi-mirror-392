import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.control_monitor_response_public_dto import ControlMonitorResponsePublicDto
    from ..models.monitor_instance_response_public_dto import MonitorInstanceResponsePublicDto
    from ..models.monitor_metadata_exclusion_response_public_dto import MonitorMetadataExclusionResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="ControlTestInstanceResponsePublicDto")


@_attrs_define
class ControlTestInstanceResponsePublicDto:
    """
    Attributes:
        id (float): Control Test Instance ID Example: 1.
        name (str): Name of control test instance Example: A Version Control System is being Used.
        description (str): The description of the control test instance Example: Inspected Drata's version control
            system....
        check_result_status (str): The compliance status of this control test instance Example: PASSED.
        last_check (datetime.datetime): Timestamp since this control test has been evaluated for compliance Example:
            2025-07-01T16:45:55.246Z.
        check_status (str): The system status of this control test instance Example: ENABLED.
        disabled_message (str): Description regarding why this control test instance is disabled Example: Disabled since
            it is not applicable to the company.
        priority (str): The priority of this control test instance relative to the rest Example: NORMAL.
        auto_enabled_at (datetime.datetime): Control test instance auto enabled timestamp Example:
            2025-07-01T16:45:55.246Z.
        test_id (float): A unique identifier for the control test instance Example: 42.
        created_at (datetime.datetime): Control test instance created timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Control test instance update timestamp Example: 2025-07-01T16:45:55.246Z.
        monitor_instances (list['MonitorInstanceResponsePublicDto']): Monitor instances associated to this control test
            instance Example: MonitorInstanceResponseDto[].
        disabling_user (UserResponsePublicDto):
        controls (list['ControlMonitorResponsePublicDto']): Controls associated to this control test instance - usually
            at least one Example: ControlMonitorResponseDto[].
        monitor_instance_exclusions (list['MonitorMetadataExclusionResponsePublicDto']): Monitor instance exclusions for
            this control test instance Example: ExclusionDto[].
    """

    id: float
    name: str
    description: str
    check_result_status: str
    last_check: datetime.datetime
    check_status: str
    disabled_message: str
    priority: str
    auto_enabled_at: datetime.datetime
    test_id: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    monitor_instances: list["MonitorInstanceResponsePublicDto"]
    disabling_user: "UserResponsePublicDto"
    controls: list["ControlMonitorResponsePublicDto"]
    monitor_instance_exclusions: list["MonitorMetadataExclusionResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        check_result_status = self.check_result_status

        last_check = self.last_check.isoformat()

        check_status = self.check_status

        disabled_message = self.disabled_message

        priority = self.priority

        auto_enabled_at = self.auto_enabled_at.isoformat()

        test_id = self.test_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        monitor_instances = []
        for monitor_instances_item_data in self.monitor_instances:
            monitor_instances_item = monitor_instances_item_data.to_dict()
            monitor_instances.append(monitor_instances_item)

        disabling_user = self.disabling_user.to_dict()

        controls = []
        for controls_item_data in self.controls:
            controls_item = controls_item_data.to_dict()
            controls.append(controls_item)

        monitor_instance_exclusions = []
        for monitor_instance_exclusions_item_data in self.monitor_instance_exclusions:
            monitor_instance_exclusions_item = monitor_instance_exclusions_item_data.to_dict()
            monitor_instance_exclusions.append(monitor_instance_exclusions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "checkResultStatus": check_result_status,
                "lastCheck": last_check,
                "checkStatus": check_status,
                "disabledMessage": disabled_message,
                "priority": priority,
                "autoEnabledAt": auto_enabled_at,
                "testId": test_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "monitorInstances": monitor_instances,
                "disablingUser": disabling_user,
                "controls": controls,
                "monitorInstanceExclusions": monitor_instance_exclusions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.control_monitor_response_public_dto import ControlMonitorResponsePublicDto
        from ..models.monitor_instance_response_public_dto import MonitorInstanceResponsePublicDto
        from ..models.monitor_metadata_exclusion_response_public_dto import MonitorMetadataExclusionResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        check_result_status = d.pop("checkResultStatus")

        last_check = isoparse(d.pop("lastCheck"))

        check_status = d.pop("checkStatus")

        disabled_message = d.pop("disabledMessage")

        priority = d.pop("priority")

        auto_enabled_at = isoparse(d.pop("autoEnabledAt"))

        test_id = d.pop("testId")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        monitor_instances = []
        _monitor_instances = d.pop("monitorInstances")
        for monitor_instances_item_data in _monitor_instances:
            monitor_instances_item = MonitorInstanceResponsePublicDto.from_dict(monitor_instances_item_data)

            monitor_instances.append(monitor_instances_item)

        disabling_user = UserResponsePublicDto.from_dict(d.pop("disablingUser"))

        controls = []
        _controls = d.pop("controls")
        for controls_item_data in _controls:
            controls_item = ControlMonitorResponsePublicDto.from_dict(controls_item_data)

            controls.append(controls_item)

        monitor_instance_exclusions = []
        _monitor_instance_exclusions = d.pop("monitorInstanceExclusions")
        for monitor_instance_exclusions_item_data in _monitor_instance_exclusions:
            monitor_instance_exclusions_item = MonitorMetadataExclusionResponsePublicDto.from_dict(
                monitor_instance_exclusions_item_data
            )

            monitor_instance_exclusions.append(monitor_instance_exclusions_item)

        control_test_instance_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            check_result_status=check_result_status,
            last_check=last_check,
            check_status=check_status,
            disabled_message=disabled_message,
            priority=priority,
            auto_enabled_at=auto_enabled_at,
            test_id=test_id,
            created_at=created_at,
            updated_at=updated_at,
            monitor_instances=monitor_instances,
            disabling_user=disabling_user,
            controls=controls,
            monitor_instance_exclusions=monitor_instance_exclusions,
        )

        control_test_instance_response_public_dto.additional_properties = d
        return control_test_instance_response_public_dto

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
