from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.framework_response_public_dto import FrameworkResponsePublicDto


T = TypeVar("T", bound="WorkspaceResponsePublicDto")


@_attrs_define
class WorkspaceResponsePublicDto:
    """
    Attributes:
        id (float): Product ID Example: 1.
        name (str): Product name Example: Drata Automation.
        description (str): Product description Example: Drata automates SOC 2 compliance.
        how_it_works (str): How does the Product Work? Example: Connect your systems to the Drata Autopilot system and
            sit back and relax!.
        url (str): Product URL Example: https://drata.com.
        logo (str): Product Logo URL Example: https://cdn-prod.imgpilot.com/logo.png.
        primary (bool): Primary Product
        frameworks (Union[Unset, list['FrameworkResponsePublicDto']]): Frameworks associated to the product. Example:
            FrameworkResponseDto[].
    """

    id: float
    name: str
    description: str
    how_it_works: str
    url: str
    logo: str
    primary: bool
    frameworks: Union[Unset, list["FrameworkResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        how_it_works = self.how_it_works

        url = self.url

        logo = self.logo

        primary = self.primary

        frameworks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.frameworks, Unset):
            frameworks = []
            for frameworks_item_data in self.frameworks:
                frameworks_item = frameworks_item_data.to_dict()
                frameworks.append(frameworks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "howItWorks": how_it_works,
                "url": url,
                "logo": logo,
                "primary": primary,
            }
        )
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.framework_response_public_dto import FrameworkResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        how_it_works = d.pop("howItWorks")

        url = d.pop("url")

        logo = d.pop("logo")

        primary = d.pop("primary")

        frameworks = []
        _frameworks = d.pop("frameworks", UNSET)
        for frameworks_item_data in _frameworks or []:
            frameworks_item = FrameworkResponsePublicDto.from_dict(frameworks_item_data)

            frameworks.append(frameworks_item)

        workspace_response_public_dto = cls(
            id=id,
            name=name,
            description=description,
            how_it_works=how_it_works,
            url=url,
            logo=logo,
            primary=primary,
            frameworks=frameworks,
        )

        workspace_response_public_dto.additional_properties = d
        return workspace_response_public_dto

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
