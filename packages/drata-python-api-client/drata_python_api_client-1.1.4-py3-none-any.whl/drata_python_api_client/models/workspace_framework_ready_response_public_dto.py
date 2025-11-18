from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.framework_response_public_dto import FrameworkResponsePublicDto


T = TypeVar("T", bound="WorkspaceFrameworkReadyResponsePublicDto")


@_attrs_define
class WorkspaceFrameworkReadyResponsePublicDto:
    """
    Attributes:
        frameworks (Union[Unset, list['FrameworkResponsePublicDto']]): Frameworks associated to the workspace.
    """

    frameworks: Union[Unset, list["FrameworkResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        frameworks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.frameworks, Unset):
            frameworks = []
            for frameworks_item_data in self.frameworks:
                frameworks_item = frameworks_item_data.to_dict()
                frameworks.append(frameworks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.framework_response_public_dto import FrameworkResponsePublicDto

        d = dict(src_dict)
        frameworks = []
        _frameworks = d.pop("frameworks", UNSET)
        for frameworks_item_data in _frameworks or []:
            frameworks_item = FrameworkResponsePublicDto.from_dict(frameworks_item_data)

            frameworks.append(frameworks_item)

        workspace_framework_ready_response_public_dto = cls(
            frameworks=frameworks,
        )

        workspace_framework_ready_response_public_dto.additional_properties = d
        return workspace_framework_ready_response_public_dto

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
