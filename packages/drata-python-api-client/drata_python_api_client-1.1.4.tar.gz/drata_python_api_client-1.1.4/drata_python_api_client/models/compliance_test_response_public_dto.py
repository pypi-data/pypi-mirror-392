import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.compliance_test_response_public_dto_autopilot_task_type import (
    ComplianceTestResponsePublicDtoAutopilotTaskType,
)
from ..models.compliance_test_response_public_dto_check_result_status import (
    ComplianceTestResponsePublicDtoCheckResultStatus,
)
from ..models.compliance_test_response_public_dto_check_status import ComplianceTestResponsePublicDtoCheckStatus

T = TypeVar("T", bound="ComplianceTestResponsePublicDto")


@_attrs_define
class ComplianceTestResponsePublicDto:
    """
    Attributes:
        monitor_id (float): Monitor ID Example: 1.
        autopilot_task_type (ComplianceTestResponsePublicDtoAutopilotTaskType): Autopilot Task Type
        control_test_instance_id (float): Control Test Instance ID Example: 43.
        test_id (float): Test ID Example: 43.
        name (str): Test name Example: MFA on Identity Provider.
        check_status (ComplianceTestResponsePublicDtoCheckStatus): Check Status
        check_result_status (ComplianceTestResponsePublicDtoCheckResultStatus): Check Result Status
        last_check (Union[None, datetime.datetime]): Last time Drata checked for compliance Example:
            2025-07-01T16:45:55.246Z.
    """

    monitor_id: float
    autopilot_task_type: ComplianceTestResponsePublicDtoAutopilotTaskType
    control_test_instance_id: float
    test_id: float
    name: str
    check_status: ComplianceTestResponsePublicDtoCheckStatus
    check_result_status: ComplianceTestResponsePublicDtoCheckResultStatus
    last_check: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        monitor_id = self.monitor_id

        autopilot_task_type = self.autopilot_task_type.value

        control_test_instance_id = self.control_test_instance_id

        test_id = self.test_id

        name = self.name

        check_status = self.check_status.value

        check_result_status = self.check_result_status.value

        last_check: Union[None, str]
        if isinstance(self.last_check, datetime.datetime):
            last_check = self.last_check.isoformat()
        else:
            last_check = self.last_check

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "monitorId": monitor_id,
                "autopilotTaskType": autopilot_task_type,
                "controlTestInstanceId": control_test_instance_id,
                "testId": test_id,
                "name": name,
                "checkStatus": check_status,
                "checkResultStatus": check_result_status,
                "lastCheck": last_check,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        monitor_id = d.pop("monitorId")

        autopilot_task_type = ComplianceTestResponsePublicDtoAutopilotTaskType(d.pop("autopilotTaskType"))

        control_test_instance_id = d.pop("controlTestInstanceId")

        test_id = d.pop("testId")

        name = d.pop("name")

        check_status = ComplianceTestResponsePublicDtoCheckStatus(d.pop("checkStatus"))

        check_result_status = ComplianceTestResponsePublicDtoCheckResultStatus(d.pop("checkResultStatus"))

        def _parse_last_check(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_check_type_0 = isoparse(data)

                return last_check_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_check = _parse_last_check(d.pop("lastCheck"))

        compliance_test_response_public_dto = cls(
            monitor_id=monitor_id,
            autopilot_task_type=autopilot_task_type,
            control_test_instance_id=control_test_instance_id,
            test_id=test_id,
            name=name,
            check_status=check_status,
            check_result_status=check_result_status,
            last_check=last_check,
        )

        compliance_test_response_public_dto.additional_properties = d
        return compliance_test_response_public_dto

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
