from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evidence_library_version_metadata_response_public_dto import (
        EvidenceLibraryVersionMetadataResponsePublicDto,
    )


T = TypeVar("T", bound="EvidenceLibraryVersionResponsePublicDto")


@_attrs_define
class EvidenceLibraryVersionResponsePublicDto:
    """
    Attributes:
        id (float): Library document version id Example: 1.
        source (str): Library document version source Example: http://www.example.com.
        type_ (str): Library document version type Example: URL.
        version (float): Library document version Example: 1.
        current (bool): Set if the version is the current Example: True.
        metadata (EvidenceLibraryVersionMetadataResponsePublicDto):
        filed_at (Union[None, Unset, str]): Library document version creation date Example: 2020-07-06.
    """

    id: float
    source: str
    type_: str
    version: float
    current: bool
    metadata: "EvidenceLibraryVersionMetadataResponsePublicDto"
    filed_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        source = self.source

        type_ = self.type_

        version = self.version

        current = self.current

        metadata = self.metadata.to_dict()

        filed_at: Union[None, Unset, str]
        if isinstance(self.filed_at, Unset):
            filed_at = UNSET
        else:
            filed_at = self.filed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "source": source,
                "type": type_,
                "version": version,
                "current": current,
                "metadata": metadata,
            }
        )
        if filed_at is not UNSET:
            field_dict["filedAt"] = filed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evidence_library_version_metadata_response_public_dto import (
            EvidenceLibraryVersionMetadataResponsePublicDto,
        )

        d = dict(src_dict)
        id = d.pop("id")

        source = d.pop("source")

        type_ = d.pop("type")

        version = d.pop("version")

        current = d.pop("current")

        metadata = EvidenceLibraryVersionMetadataResponsePublicDto.from_dict(d.pop("metadata"))

        def _parse_filed_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filed_at = _parse_filed_at(d.pop("filedAt", UNSET))

        evidence_library_version_response_public_dto = cls(
            id=id,
            source=source,
            type_=type_,
            version=version,
            current=current,
            metadata=metadata,
            filed_at=filed_at,
        )

        evidence_library_version_response_public_dto.additional_properties = d
        return evidence_library_version_response_public_dto

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
