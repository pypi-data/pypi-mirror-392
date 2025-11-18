import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.requirement_detail_response_public_dto_controls_item import (
        RequirementDetailResponsePublicDtoControlsItem,
    )


T = TypeVar("T", bound="RequirementDetailResponsePublicDto")


@_attrs_define
class RequirementDetailResponsePublicDto:
    """
    Attributes:
        id (float): Requirement id Example: 1213123.
        name (str): Requirement name Example: CC1.1.
        description (str): Requirement description Example: The entity demonstrates a commitment to integrity and
            ethical values..
        long_description (str): Requirement long description Example: The entity demonstrates a commitment to integrity
            and ethical values..
        additional_info (str): Additional info surrounding requirement Example: The entity demonstrates a commitment to
            integrity and ethical values..
        additional_info_2 (str): Additional info surrounding requirement 2 Example: The entity demonstrates a commitment
            to integrity and ethical values 2..
        additional_info_3 (str): Additional info surrounding requirement 3 Example: The entity demonstrates a commitment
            to integrity and ethical values 3..
        is_ready (bool): Is requirement "ready" Example: true.
        framework_name (str): The framework name this requirement is associated to Example: SOC 2.
        controls (list['RequirementDetailResponsePublicDtoControlsItem']): Necessary control properties mapped to this
            requirement, sorted by isReady and then controlNumber
        topic (str):
        category (str):
        sub_category (str):
        rationale (Union[Unset, str]): Requirement rationale for out of scope. Example: This requirement is not needed..
        archived_at (Union[Unset, datetime.datetime]): Date the requirement was marked out of scope Example: 2020-07-06.
        custom_framework_id (Union[Unset, float]): Custom Framework ID Example: 123e4567-e89b-12d3-a456-426614174000.
        custom_category (Union[Unset, str]):
    """

    id: float
    name: str
    description: str
    long_description: str
    additional_info: str
    additional_info_2: str
    additional_info_3: str
    is_ready: bool
    framework_name: str
    controls: list["RequirementDetailResponsePublicDtoControlsItem"]
    topic: str
    category: str
    sub_category: str
    rationale: Union[Unset, str] = UNSET
    archived_at: Union[Unset, datetime.datetime] = UNSET
    custom_framework_id: Union[Unset, float] = UNSET
    custom_category: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        long_description = self.long_description

        additional_info = self.additional_info

        additional_info_2 = self.additional_info_2

        additional_info_3 = self.additional_info_3

        is_ready = self.is_ready

        framework_name = self.framework_name

        controls = []
        for controls_item_data in self.controls:
            controls_item = controls_item_data.to_dict()
            controls.append(controls_item)

        topic = self.topic

        category = self.category

        sub_category = self.sub_category

        rationale = self.rationale

        archived_at: Union[Unset, str] = UNSET
        if not isinstance(self.archived_at, Unset):
            archived_at = self.archived_at.isoformat()

        custom_framework_id = self.custom_framework_id

        custom_category = self.custom_category

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "longDescription": long_description,
                "additionalInfo": additional_info,
                "additionalInfo2": additional_info_2,
                "additionalInfo3": additional_info_3,
                "isReady": is_ready,
                "frameworkName": framework_name,
                "controls": controls,
                "topic": topic,
                "category": category,
                "subCategory": sub_category,
            }
        )
        if rationale is not UNSET:
            field_dict["rationale"] = rationale
        if archived_at is not UNSET:
            field_dict["archivedAt"] = archived_at
        if custom_framework_id is not UNSET:
            field_dict["customFrameworkId"] = custom_framework_id
        if custom_category is not UNSET:
            field_dict["customCategory"] = custom_category

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.requirement_detail_response_public_dto_controls_item import (
            RequirementDetailResponsePublicDtoControlsItem,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        long_description = d.pop("longDescription")

        additional_info = d.pop("additionalInfo")

        additional_info_2 = d.pop("additionalInfo2")

        additional_info_3 = d.pop("additionalInfo3")

        is_ready = d.pop("isReady")

        framework_name = d.pop("frameworkName")

        controls = []
        _controls = d.pop("controls")
        for controls_item_data in _controls:
            controls_item = RequirementDetailResponsePublicDtoControlsItem.from_dict(controls_item_data)

            controls.append(controls_item)

        topic = d.pop("topic")

        category = d.pop("category")

        sub_category = d.pop("subCategory")

        rationale = d.pop("rationale", UNSET)

        _archived_at = d.pop("archivedAt", UNSET)
        archived_at: Union[Unset, datetime.datetime]
        if isinstance(_archived_at, Unset):
            archived_at = UNSET
        else:
            archived_at = isoparse(_archived_at)

        custom_framework_id = d.pop("customFrameworkId", UNSET)

        custom_category = d.pop("customCategory", UNSET)

        requirement_detail_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            long_description=long_description,
            additional_info=additional_info,
            additional_info_2=additional_info_2,
            additional_info_3=additional_info_3,
            is_ready=is_ready,
            framework_name=framework_name,
            controls=controls,
            topic=topic,
            category=category,
            sub_category=sub_category,
            rationale=rationale,
            archived_at=archived_at,
            custom_framework_id=custom_framework_id,
            custom_category=custom_category,
        )

        requirement_detail_response_public_dto.additional_properties = d
        return requirement_detail_response_public_dto

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
