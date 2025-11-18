from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.external_evidence_response_public_dto import ExternalEvidenceResponsePublicDto


T = TypeVar("T", bound="MappedExternalEvidenceResponsePublicDto")


@_attrs_define
class MappedExternalEvidenceResponsePublicDto:
    """
    Attributes:
        id (float): Control id Example: 123.
        slug (str): Control slug Example: databases-monitored-and-alarmed.
        external_evidence (list['ExternalEvidenceResponsePublicDto']): ExternalEvidences array Example:
            ExternalEvidenceResponseDto[].
    """

    id: float
    slug: str
    external_evidence: list["ExternalEvidenceResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        slug = self.slug

        external_evidence = []
        for external_evidence_item_data in self.external_evidence:
            external_evidence_item = external_evidence_item_data.to_dict()
            external_evidence.append(external_evidence_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "slug": slug,
                "externalEvidence": external_evidence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_evidence_response_public_dto import ExternalEvidenceResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        slug = d.pop("slug")

        external_evidence = []
        _external_evidence = d.pop("externalEvidence")
        for external_evidence_item_data in _external_evidence:
            external_evidence_item = ExternalEvidenceResponsePublicDto.from_dict(external_evidence_item_data)

            external_evidence.append(external_evidence_item)

        mapped_external_evidence_response_public_dto = cls(
            id=id,
            slug=slug,
            external_evidence=external_evidence,
        )

        mapped_external_evidence_response_public_dto.additional_properties = d
        return mapped_external_evidence_response_public_dto

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
