import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.risk_response_public_dto_status import RiskResponsePublicDtoStatus

if TYPE_CHECKING:
    from ..models.document_response_public_dto import DocumentResponsePublicDto
    from ..models.global_note_response_public_dto import GlobalNoteResponsePublicDto
    from ..models.risk_category_response_public_dto import RiskCategoryResponsePublicDto
    from ..models.risk_control_response_public_dto import RiskControlResponsePublicDto
    from ..models.risk_user_response_public_dto import RiskUserResponsePublicDto


T = TypeVar("T", bound="RiskResponsePublicDto")


@_attrs_define
class RiskResponsePublicDto:
    """
    Attributes:
        id (float): Risk Id Example: 1.
        risk_id (str): Human readable risk id Example: AC-04.
        title (str): Title of the risk Example: Password Management - Password Cracking.
        description (str): Description of the risk Example: An attacker attempts to gain access to organizational
            information by guessing of passwords..
        treatment_plan (str): The risk treatment plan Example: UNTREATED.
        treatment_details (str): The risk treatment details Example: Building doors can be open and an unauthorized
            person can walk in..
        anticipated_completion_date (datetime.datetime): Anticipated Completion Date. Example: 2025-07-01T16:45:55.246Z.
        completion_date (datetime.datetime): Completion Date. Example: 2025-07-01T16:45:55.246Z.
        impact (float): The risk impact Example: 5.
        likelihood (float): The risk likelihood Example: 5.
        score (float): The risk score Example: 5.
        residual_impact (float): The risk residual impact Example: 5.
        residual_likelihood (float): The risk residual likelihood Example: 5.
        residual_score (float): The risk residual score Example: 5.
        applicable (bool): Risk applicable or not Example: True.
        status (RiskResponsePublicDtoStatus): Risk status Example: ACTIVE.
        controls (list['RiskControlResponsePublicDto']): Controls attached to the risk
        categories (list['RiskCategoryResponsePublicDto']): Categories attached to the risk
        owners (list['RiskUserResponsePublicDto']): List of owners for the risk
        reviewers (list['RiskUserResponsePublicDto']): List of reviewers for the risk
        documents (list['DocumentResponsePublicDto']): List of documents
        notes (list['GlobalNoteResponsePublicDto']): List of notes
    """

    id: float
    risk_id: str
    title: str
    description: str
    treatment_plan: str
    treatment_details: str
    anticipated_completion_date: datetime.datetime
    completion_date: datetime.datetime
    impact: float
    likelihood: float
    score: float
    residual_impact: float
    residual_likelihood: float
    residual_score: float
    applicable: bool
    status: RiskResponsePublicDtoStatus
    controls: list["RiskControlResponsePublicDto"]
    categories: list["RiskCategoryResponsePublicDto"]
    owners: list["RiskUserResponsePublicDto"]
    reviewers: list["RiskUserResponsePublicDto"]
    documents: list["DocumentResponsePublicDto"]
    notes: list["GlobalNoteResponsePublicDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        risk_id = self.risk_id

        title = self.title

        description = self.description

        treatment_plan = self.treatment_plan

        treatment_details = self.treatment_details

        anticipated_completion_date = self.anticipated_completion_date.isoformat()

        completion_date = self.completion_date.isoformat()

        impact = self.impact

        likelihood = self.likelihood

        score = self.score

        residual_impact = self.residual_impact

        residual_likelihood = self.residual_likelihood

        residual_score = self.residual_score

        applicable = self.applicable

        status = self.status.value

        controls = []
        for controls_item_data in self.controls:
            controls_item = controls_item_data.to_dict()
            controls.append(controls_item)

        categories = []
        for categories_item_data in self.categories:
            categories_item = categories_item_data.to_dict()
            categories.append(categories_item)

        owners = []
        for owners_item_data in self.owners:
            owners_item = owners_item_data.to_dict()
            owners.append(owners_item)

        reviewers = []
        for reviewers_item_data in self.reviewers:
            reviewers_item = reviewers_item_data.to_dict()
            reviewers.append(reviewers_item)

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        notes = []
        for notes_item_data in self.notes:
            notes_item = notes_item_data.to_dict()
            notes.append(notes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "riskId": risk_id,
                "title": title,
                "description": description,
                "treatmentPlan": treatment_plan,
                "treatmentDetails": treatment_details,
                "anticipatedCompletionDate": anticipated_completion_date,
                "completionDate": completion_date,
                "impact": impact,
                "likelihood": likelihood,
                "score": score,
                "residualImpact": residual_impact,
                "residualLikelihood": residual_likelihood,
                "residualScore": residual_score,
                "applicable": applicable,
                "status": status,
                "controls": controls,
                "categories": categories,
                "owners": owners,
                "reviewers": reviewers,
                "documents": documents,
                "notes": notes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response_public_dto import DocumentResponsePublicDto
        from ..models.global_note_response_public_dto import GlobalNoteResponsePublicDto
        from ..models.risk_category_response_public_dto import RiskCategoryResponsePublicDto
        from ..models.risk_control_response_public_dto import RiskControlResponsePublicDto
        from ..models.risk_user_response_public_dto import RiskUserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        risk_id = d.pop("riskId")

        title = d.pop("title")

        description = d.pop("description")

        treatment_plan = d.pop("treatmentPlan")

        treatment_details = d.pop("treatmentDetails")

        anticipated_completion_date = isoparse(d.pop("anticipatedCompletionDate"))

        completion_date = isoparse(d.pop("completionDate"))

        impact = d.pop("impact")

        likelihood = d.pop("likelihood")

        score = d.pop("score")

        residual_impact = d.pop("residualImpact")

        residual_likelihood = d.pop("residualLikelihood")

        residual_score = d.pop("residualScore")

        applicable = d.pop("applicable")

        status = RiskResponsePublicDtoStatus(d.pop("status"))

        controls = []
        _controls = d.pop("controls")
        for controls_item_data in _controls:
            controls_item = RiskControlResponsePublicDto.from_dict(controls_item_data)

            controls.append(controls_item)

        categories = []
        _categories = d.pop("categories")
        for categories_item_data in _categories:
            categories_item = RiskCategoryResponsePublicDto.from_dict(categories_item_data)

            categories.append(categories_item)

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = RiskUserResponsePublicDto.from_dict(owners_item_data)

            owners.append(owners_item)

        reviewers = []
        _reviewers = d.pop("reviewers")
        for reviewers_item_data in _reviewers:
            reviewers_item = RiskUserResponsePublicDto.from_dict(reviewers_item_data)

            reviewers.append(reviewers_item)

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = DocumentResponsePublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        notes = []
        _notes = d.pop("notes")
        for notes_item_data in _notes:
            notes_item = GlobalNoteResponsePublicDto.from_dict(notes_item_data)

            notes.append(notes_item)

        risk_response_public_dto = cls(
            id=id,
            risk_id=risk_id,
            title=title,
            description=description,
            treatment_plan=treatment_plan,
            treatment_details=treatment_details,
            anticipated_completion_date=anticipated_completion_date,
            completion_date=completion_date,
            impact=impact,
            likelihood=likelihood,
            score=score,
            residual_impact=residual_impact,
            residual_likelihood=residual_likelihood,
            residual_score=residual_score,
            applicable=applicable,
            status=status,
            controls=controls,
            categories=categories,
            owners=owners,
            reviewers=reviewers,
            documents=documents,
            notes=notes,
        )

        risk_response_public_dto.additional_properties = d
        return risk_response_public_dto

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
