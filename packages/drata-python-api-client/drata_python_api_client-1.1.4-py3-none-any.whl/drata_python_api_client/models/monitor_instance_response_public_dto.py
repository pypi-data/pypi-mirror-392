import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.monitor_instance_check_type_response_public_dto import MonitorInstanceCheckTypeResponsePublicDto
    from ..models.monitor_instance_metadata_response_public_dto import MonitorInstanceMetadataResponsePublicDto


T = TypeVar("T", bound="MonitorInstanceResponsePublicDto")


@_attrs_define
class MonitorInstanceResponsePublicDto:
    """
    Attributes:
        id (float): Monitor instance id Example: 1.
        check_result_status (str): Denotes monitor check pass/fail/issue Example: PASSED.
        check_frequency (str): How often should this monitor instance be running Example: DAILY.
        monitor_instance_check_types (list['MonitorInstanceCheckTypeResponsePublicDto']): The monitor instance
            associated check types
        autopilot_task_type (str): The autopilot task type Example: IDENTITY_PROVIDER_MFA_ENABLED.
        failed_test_description (str): The description of why this monitor instance would fail Example: This test fails
            when the SSL certificate cannot be verified.
        evidence_collection_description (str): The description of the means to gather evidence Example: Curl call to the
            website.
        remedy_description (str): The description of how to remedy this monitor instance Example: Enable SSL on your
            company website.
        metadata (list['MonitorInstanceMetadataResponsePublicDto']): A map of MonitorInstanceMetadataResponseDto objects
            mapped to their connection ids
        enabled (bool): Controls whether this monitor instance is on/off Example: True.
        url (str): The Help Desk URL for this monitor Example: https://help.drata.com.
        created_at (datetime.datetime): Monitor instance creation timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Monitor instance updated timestamp Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    check_result_status: str
    check_frequency: str
    monitor_instance_check_types: list["MonitorInstanceCheckTypeResponsePublicDto"]
    autopilot_task_type: str
    failed_test_description: str
    evidence_collection_description: str
    remedy_description: str
    metadata: list["MonitorInstanceMetadataResponsePublicDto"]
    enabled: bool
    url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        check_result_status = self.check_result_status

        check_frequency = self.check_frequency

        monitor_instance_check_types = []
        for monitor_instance_check_types_item_data in self.monitor_instance_check_types:
            monitor_instance_check_types_item = monitor_instance_check_types_item_data.to_dict()
            monitor_instance_check_types.append(monitor_instance_check_types_item)

        autopilot_task_type = self.autopilot_task_type

        failed_test_description = self.failed_test_description

        evidence_collection_description = self.evidence_collection_description

        remedy_description = self.remedy_description

        metadata = []
        for metadata_item_data in self.metadata:
            metadata_item = metadata_item_data.to_dict()
            metadata.append(metadata_item)

        enabled = self.enabled

        url = self.url

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "checkResultStatus": check_result_status,
                "checkFrequency": check_frequency,
                "monitorInstanceCheckTypes": monitor_instance_check_types,
                "autopilotTaskType": autopilot_task_type,
                "failedTestDescription": failed_test_description,
                "evidenceCollectionDescription": evidence_collection_description,
                "remedyDescription": remedy_description,
                "metadata": metadata,
                "enabled": enabled,
                "url": url,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.monitor_instance_check_type_response_public_dto import MonitorInstanceCheckTypeResponsePublicDto
        from ..models.monitor_instance_metadata_response_public_dto import MonitorInstanceMetadataResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        check_result_status = d.pop("checkResultStatus")

        check_frequency = d.pop("checkFrequency")

        monitor_instance_check_types = []
        _monitor_instance_check_types = d.pop("monitorInstanceCheckTypes")
        for monitor_instance_check_types_item_data in _monitor_instance_check_types:
            monitor_instance_check_types_item = MonitorInstanceCheckTypeResponsePublicDto.from_dict(
                monitor_instance_check_types_item_data
            )

            monitor_instance_check_types.append(monitor_instance_check_types_item)

        autopilot_task_type = d.pop("autopilotTaskType")

        failed_test_description = d.pop("failedTestDescription")

        evidence_collection_description = d.pop("evidenceCollectionDescription")

        remedy_description = d.pop("remedyDescription")

        metadata = []
        _metadata = d.pop("metadata")
        for metadata_item_data in _metadata:
            metadata_item = MonitorInstanceMetadataResponsePublicDto.from_dict(metadata_item_data)

            metadata.append(metadata_item)

        enabled = d.pop("enabled")

        url = d.pop("url")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        monitor_instance_response_public_dto = cls(
            id=id,
            check_result_status=check_result_status,
            check_frequency=check_frequency,
            monitor_instance_check_types=monitor_instance_check_types,
            autopilot_task_type=autopilot_task_type,
            failed_test_description=failed_test_description,
            evidence_collection_description=evidence_collection_description,
            remedy_description=remedy_description,
            metadata=metadata,
            enabled=enabled,
            url=url,
            created_at=created_at,
            updated_at=updated_at,
        )

        monitor_instance_response_public_dto.additional_properties = d
        return monitor_instance_response_public_dto

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
