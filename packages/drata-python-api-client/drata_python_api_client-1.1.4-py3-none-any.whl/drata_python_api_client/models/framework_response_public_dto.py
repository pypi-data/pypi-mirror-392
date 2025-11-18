import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FrameworkResponsePublicDto")


@_attrs_define
class FrameworkResponsePublicDto:
    """
    Attributes:
        id (float): Framework id Example: 123.
        name (str): Framework name Example: SOC2.
        has_level (bool): Does the framework have a level Example: True.
        level_label (Union[None, str]): What is the framework level Example: True.
        selected_level (Union[None, str]): id of the level tag Example: 42.
        privacy (Union[None, bool]): privacy flag for NIST80053 Example: True.
        description (str): Framework description Example: Report on controls at a Service Organization.
        long_description (str): A longer description describing the framework in detail
        slug (str): Framework Slug used to identify the framework Example: soc2-slug.
        tag (str): A tag representing the framework Example: SOC2.
        label (str): A pill name representing the framework Example: SOC 2.
        total_in_scope_controls (float): The number of associated Drata controls Example: 42.
        num_in_scope_requirements (float): The number of associated Drata requirements that are in scope Example: 42.
        num_ready_in_scope_requirements (float): The number of associated Drata requirements that are "ready" Example:
            42.
        enabled_at (Union[None, datetime.datetime]): State of the framework for the tenant Example: True.
        framework_enabled (bool): State of the framework for the tenant Example: True.
        controls_enabled (bool): State of the controls for this framework for the tenant Example: True.
        color (str): The font color assigned for this framework Example: #174880.
        bg_color (str): The background color assigned for this framework Example: #174880.
        active_logo (str): The URL of the active logo Example: https://drata.com.
        inactive_logo (str): The URL of the inactive logo Example: https://drata.com.
        created_at (datetime.datetime): Account created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Account updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        is_ready (bool): Is the framework ready Example: True.
        custom_framework_id (str): Custom framework id Example: 123e4567-e89b-12d3-a456-426614174000.
        type_ (str): The type of the auditor framework Example: CUSTOM.
        product_framework_enabled (Union[Unset, bool]): State of the framework for the product Example: True.
    """

    id: float
    name: str
    has_level: bool
    level_label: Union[None, str]
    selected_level: Union[None, str]
    privacy: Union[None, bool]
    description: str
    long_description: str
    slug: str
    tag: str
    label: str
    total_in_scope_controls: float
    num_in_scope_requirements: float
    num_ready_in_scope_requirements: float
    enabled_at: Union[None, datetime.datetime]
    framework_enabled: bool
    controls_enabled: bool
    color: str
    bg_color: str
    active_logo: str
    inactive_logo: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_ready: bool
    custom_framework_id: str
    type_: str
    product_framework_enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        has_level = self.has_level

        level_label: Union[None, str]
        level_label = self.level_label

        selected_level: Union[None, str]
        selected_level = self.selected_level

        privacy: Union[None, bool]
        privacy = self.privacy

        description = self.description

        long_description = self.long_description

        slug = self.slug

        tag = self.tag

        label = self.label

        total_in_scope_controls = self.total_in_scope_controls

        num_in_scope_requirements = self.num_in_scope_requirements

        num_ready_in_scope_requirements = self.num_ready_in_scope_requirements

        enabled_at: Union[None, str]
        if isinstance(self.enabled_at, datetime.datetime):
            enabled_at = self.enabled_at.isoformat()
        else:
            enabled_at = self.enabled_at

        framework_enabled = self.framework_enabled

        controls_enabled = self.controls_enabled

        color = self.color

        bg_color = self.bg_color

        active_logo = self.active_logo

        inactive_logo = self.inactive_logo

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        is_ready = self.is_ready

        custom_framework_id = self.custom_framework_id

        type_ = self.type_

        product_framework_enabled = self.product_framework_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "hasLevel": has_level,
                "levelLabel": level_label,
                "selectedLevel": selected_level,
                "privacy": privacy,
                "description": description,
                "longDescription": long_description,
                "slug": slug,
                "tag": tag,
                "label": label,
                "totalInScopeControls": total_in_scope_controls,
                "numInScopeRequirements": num_in_scope_requirements,
                "numReadyInScopeRequirements": num_ready_in_scope_requirements,
                "enabledAt": enabled_at,
                "frameworkEnabled": framework_enabled,
                "controlsEnabled": controls_enabled,
                "color": color,
                "bgColor": bg_color,
                "activeLogo": active_logo,
                "inactiveLogo": inactive_logo,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "isReady": is_ready,
                "customFrameworkId": custom_framework_id,
                "type": type_,
            }
        )
        if product_framework_enabled is not UNSET:
            field_dict["productFrameworkEnabled"] = product_framework_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        has_level = d.pop("hasLevel")

        def _parse_level_label(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        level_label = _parse_level_label(d.pop("levelLabel"))

        def _parse_selected_level(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        selected_level = _parse_selected_level(d.pop("selectedLevel"))

        def _parse_privacy(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        privacy = _parse_privacy(d.pop("privacy"))

        description = d.pop("description")

        long_description = d.pop("longDescription")

        slug = d.pop("slug")

        tag = d.pop("tag")

        label = d.pop("label")

        total_in_scope_controls = d.pop("totalInScopeControls")

        num_in_scope_requirements = d.pop("numInScopeRequirements")

        num_ready_in_scope_requirements = d.pop("numReadyInScopeRequirements")

        def _parse_enabled_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                enabled_at_type_0 = isoparse(data)

                return enabled_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        enabled_at = _parse_enabled_at(d.pop("enabledAt"))

        framework_enabled = d.pop("frameworkEnabled")

        controls_enabled = d.pop("controlsEnabled")

        color = d.pop("color")

        bg_color = d.pop("bgColor")

        active_logo = d.pop("activeLogo")

        inactive_logo = d.pop("inactiveLogo")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        is_ready = d.pop("isReady")

        custom_framework_id = d.pop("customFrameworkId")

        type_ = d.pop("type")

        product_framework_enabled = d.pop("productFrameworkEnabled", UNSET)

        framework_response_public_dto = cls(
            id=id,
            name=name,
            has_level=has_level,
            level_label=level_label,
            selected_level=selected_level,
            privacy=privacy,
            description=description,
            long_description=long_description,
            slug=slug,
            tag=tag,
            label=label,
            total_in_scope_controls=total_in_scope_controls,
            num_in_scope_requirements=num_in_scope_requirements,
            num_ready_in_scope_requirements=num_ready_in_scope_requirements,
            enabled_at=enabled_at,
            framework_enabled=framework_enabled,
            controls_enabled=controls_enabled,
            color=color,
            bg_color=bg_color,
            active_logo=active_logo,
            inactive_logo=inactive_logo,
            created_at=created_at,
            updated_at=updated_at,
            is_ready=is_ready,
            custom_framework_id=custom_framework_id,
            type_=type_,
            product_framework_enabled=product_framework_enabled,
        )

        framework_response_public_dto.additional_properties = d
        return framework_response_public_dto

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
