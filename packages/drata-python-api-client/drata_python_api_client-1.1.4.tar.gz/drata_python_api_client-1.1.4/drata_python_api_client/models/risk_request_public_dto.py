import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.risk_request_public_dto_status import RiskRequestPublicDtoStatus
from ..models.risk_request_public_dto_treatment_plan import RiskRequestPublicDtoTreatmentPlan
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.category_request_public_dto import CategoryRequestPublicDto
    from ..models.control_request_public_dto import ControlRequestPublicDto
    from ..models.document_request_public_dto import DocumentRequestPublicDto
    from ..models.owner_request_public_dto import OwnerRequestPublicDto
    from ..models.reviewer_request_public_dto import ReviewerRequestPublicDto


T = TypeVar("T", bound="RiskRequestPublicDto")


@_attrs_define
class RiskRequestPublicDto:
    """
    Attributes:
        title (str): Describes the title of a risk Example: Door locks.
        description (str): Describes the problem Example: Building doors can be open and an unauthorized person can walk
            in..
        treatment_plan (RiskRequestPublicDtoTreatmentPlan): The risk treatment plan Example: TRANSFER.
        impact (Union[Unset, float]): Describes the impact Example: 3.
        likelihood (Union[Unset, float]): Describes the likelihood Example: 1.
        score (Union[Unset, float]): Assessment score Example: 3.
        categories (Union[Unset, list['CategoryRequestPublicDto']]):
        documents (Union[Unset, list['DocumentRequestPublicDto']]):
        treatment_details (Union[Unset, str]): Describes the treatment Example: Building doors can be open and an
            unauthorized person can walk in..
        anticipated_completion_date (Union[Unset, datetime.datetime]): Anticipated Completion Date. Example:
            2025-07-01T16:45:55.246Z.
        completion_date (Union[Unset, datetime.datetime]): Completion Date. Example: 2025-07-01T16:45:55.246Z.
        reviewers (Union[Unset, list['ReviewerRequestPublicDto']]):
        owners (Union[Unset, list['OwnerRequestPublicDto']]):
        residual_impact (Union[Unset, float]): Describes the score for impact Example: 3.
        residual_likelihood (Union[Unset, float]): Describes the score for likelihood Example: 1.
        residual_score (Union[Unset, float]): Assessment residual score Example: 3.
        controls (Union[Unset, list['ControlRequestPublicDto']]):
        applicable (Union[Unset, bool]): Mark if risk is applicable or not
        status (Union[Unset, RiskRequestPublicDtoStatus]): Risks status Example: ACTIVE.
    """

    title: str
    description: str
    treatment_plan: RiskRequestPublicDtoTreatmentPlan
    impact: Union[Unset, float] = UNSET
    likelihood: Union[Unset, float] = UNSET
    score: Union[Unset, float] = UNSET
    categories: Union[Unset, list["CategoryRequestPublicDto"]] = UNSET
    documents: Union[Unset, list["DocumentRequestPublicDto"]] = UNSET
    treatment_details: Union[Unset, str] = UNSET
    anticipated_completion_date: Union[Unset, datetime.datetime] = UNSET
    completion_date: Union[Unset, datetime.datetime] = UNSET
    reviewers: Union[Unset, list["ReviewerRequestPublicDto"]] = UNSET
    owners: Union[Unset, list["OwnerRequestPublicDto"]] = UNSET
    residual_impact: Union[Unset, float] = UNSET
    residual_likelihood: Union[Unset, float] = UNSET
    residual_score: Union[Unset, float] = UNSET
    controls: Union[Unset, list["ControlRequestPublicDto"]] = UNSET
    applicable: Union[Unset, bool] = UNSET
    status: Union[Unset, RiskRequestPublicDtoStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        description = self.description

        treatment_plan = self.treatment_plan.value

        impact = self.impact

        likelihood = self.likelihood

        score = self.score

        categories: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.categories, Unset):
            categories = []
            for categories_item_data in self.categories:
                categories_item = categories_item_data.to_dict()
                categories.append(categories_item)

        documents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.documents, Unset):
            documents = []
            for documents_item_data in self.documents:
                documents_item = documents_item_data.to_dict()
                documents.append(documents_item)

        treatment_details = self.treatment_details

        anticipated_completion_date: Union[Unset, str] = UNSET
        if not isinstance(self.anticipated_completion_date, Unset):
            anticipated_completion_date = self.anticipated_completion_date.isoformat()

        completion_date: Union[Unset, str] = UNSET
        if not isinstance(self.completion_date, Unset):
            completion_date = self.completion_date.isoformat()

        reviewers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.reviewers, Unset):
            reviewers = []
            for reviewers_item_data in self.reviewers:
                reviewers_item = reviewers_item_data.to_dict()
                reviewers.append(reviewers_item)

        owners: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.owners, Unset):
            owners = []
            for owners_item_data in self.owners:
                owners_item = owners_item_data.to_dict()
                owners.append(owners_item)

        residual_impact = self.residual_impact

        residual_likelihood = self.residual_likelihood

        residual_score = self.residual_score

        controls: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.controls, Unset):
            controls = []
            for controls_item_data in self.controls:
                controls_item = controls_item_data.to_dict()
                controls.append(controls_item)

        applicable = self.applicable

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "description": description,
                "treatmentPlan": treatment_plan,
            }
        )
        if impact is not UNSET:
            field_dict["impact"] = impact
        if likelihood is not UNSET:
            field_dict["likelihood"] = likelihood
        if score is not UNSET:
            field_dict["score"] = score
        if categories is not UNSET:
            field_dict["categories"] = categories
        if documents is not UNSET:
            field_dict["documents"] = documents
        if treatment_details is not UNSET:
            field_dict["treatmentDetails"] = treatment_details
        if anticipated_completion_date is not UNSET:
            field_dict["anticipatedCompletionDate"] = anticipated_completion_date
        if completion_date is not UNSET:
            field_dict["completionDate"] = completion_date
        if reviewers is not UNSET:
            field_dict["reviewers"] = reviewers
        if owners is not UNSET:
            field_dict["owners"] = owners
        if residual_impact is not UNSET:
            field_dict["residualImpact"] = residual_impact
        if residual_likelihood is not UNSET:
            field_dict["residualLikelihood"] = residual_likelihood
        if residual_score is not UNSET:
            field_dict["residualScore"] = residual_score
        if controls is not UNSET:
            field_dict["controls"] = controls
        if applicable is not UNSET:
            field_dict["applicable"] = applicable
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.category_request_public_dto import CategoryRequestPublicDto
        from ..models.control_request_public_dto import ControlRequestPublicDto
        from ..models.document_request_public_dto import DocumentRequestPublicDto
        from ..models.owner_request_public_dto import OwnerRequestPublicDto
        from ..models.reviewer_request_public_dto import ReviewerRequestPublicDto

        d = dict(src_dict)
        title = d.pop("title")

        description = d.pop("description")

        treatment_plan = RiskRequestPublicDtoTreatmentPlan(d.pop("treatmentPlan"))

        impact = d.pop("impact", UNSET)

        likelihood = d.pop("likelihood", UNSET)

        score = d.pop("score", UNSET)

        categories = []
        _categories = d.pop("categories", UNSET)
        for categories_item_data in _categories or []:
            categories_item = CategoryRequestPublicDto.from_dict(categories_item_data)

            categories.append(categories_item)

        documents = []
        _documents = d.pop("documents", UNSET)
        for documents_item_data in _documents or []:
            documents_item = DocumentRequestPublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        treatment_details = d.pop("treatmentDetails", UNSET)

        _anticipated_completion_date = d.pop("anticipatedCompletionDate", UNSET)
        anticipated_completion_date: Union[Unset, datetime.datetime]
        if isinstance(_anticipated_completion_date, Unset):
            anticipated_completion_date = UNSET
        else:
            anticipated_completion_date = isoparse(_anticipated_completion_date)

        _completion_date = d.pop("completionDate", UNSET)
        completion_date: Union[Unset, datetime.datetime]
        if isinstance(_completion_date, Unset):
            completion_date = UNSET
        else:
            completion_date = isoparse(_completion_date)

        reviewers = []
        _reviewers = d.pop("reviewers", UNSET)
        for reviewers_item_data in _reviewers or []:
            reviewers_item = ReviewerRequestPublicDto.from_dict(reviewers_item_data)

            reviewers.append(reviewers_item)

        owners = []
        _owners = d.pop("owners", UNSET)
        for owners_item_data in _owners or []:
            owners_item = OwnerRequestPublicDto.from_dict(owners_item_data)

            owners.append(owners_item)

        residual_impact = d.pop("residualImpact", UNSET)

        residual_likelihood = d.pop("residualLikelihood", UNSET)

        residual_score = d.pop("residualScore", UNSET)

        controls = []
        _controls = d.pop("controls", UNSET)
        for controls_item_data in _controls or []:
            controls_item = ControlRequestPublicDto.from_dict(controls_item_data)

            controls.append(controls_item)

        applicable = d.pop("applicable", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, RiskRequestPublicDtoStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = RiskRequestPublicDtoStatus(_status)

        risk_request_public_dto = cls(
            title=title,
            description=description,
            treatment_plan=treatment_plan,
            impact=impact,
            likelihood=likelihood,
            score=score,
            categories=categories,
            documents=documents,
            treatment_details=treatment_details,
            anticipated_completion_date=anticipated_completion_date,
            completion_date=completion_date,
            reviewers=reviewers,
            owners=owners,
            residual_impact=residual_impact,
            residual_likelihood=residual_likelihood,
            residual_score=residual_score,
            controls=controls,
            applicable=applicable,
            status=status,
        )

        risk_request_public_dto.additional_properties = d
        return risk_request_public_dto

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
