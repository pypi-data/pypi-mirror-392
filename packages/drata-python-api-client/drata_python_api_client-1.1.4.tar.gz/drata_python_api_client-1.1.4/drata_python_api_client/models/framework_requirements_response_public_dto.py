from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.requirement_detail_response_public_dto import RequirementDetailResponsePublicDto


T = TypeVar("T", bound="FrameworkRequirementsResponsePublicDto")


@_attrs_define
class FrameworkRequirementsResponsePublicDto:
    """
    Attributes:
        framework_tag (str): The framework tag this requirement is associated to Example: HIPAA.
        requirements (list['RequirementDetailResponsePublicDto']): A list of requirements associated to this framework
            Example: PaginationResponseDto<ControlListRequirement>.
    """

    framework_tag: str
    requirements: list["RequirementDetailResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        framework_tag = self.framework_tag

        requirements = []
        for requirements_item_data in self.requirements:
            requirements_item = requirements_item_data.to_dict()
            requirements.append(requirements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "frameworkTag": framework_tag,
                "requirements": requirements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.requirement_detail_response_public_dto import RequirementDetailResponsePublicDto

        d = dict(src_dict)
        framework_tag = d.pop("frameworkTag")

        requirements = []
        _requirements = d.pop("requirements")
        for requirements_item_data in _requirements:
            requirements_item = RequirementDetailResponsePublicDto.from_dict(requirements_item_data)

            requirements.append(requirements_item)

        framework_requirements_response_public_dto = cls(
            framework_tag=framework_tag,
            requirements=requirements,
        )

        framework_requirements_response_public_dto.additional_properties = d
        return framework_requirements_response_public_dto

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
