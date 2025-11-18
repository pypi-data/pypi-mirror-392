import json
from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="CreateControlRequestPublicDto")


@_attrs_define
class CreateControlRequestPublicDto:
    """
    Attributes:
        name (str): The name of the control Example: Good Control Name.
        description (str): The description of the control Example: A very good description.
        question (Union[Unset, str]): The question of the control Example: A very good question.
        code (Union[Unset, str]): The control code Example: DRA-69.
        activity (Union[Unset, str]): The activity of the control Example: A very good activity.
        external_evidence_metadata (Union[Unset, str]): JSON string of metadata of uploaded evidence Example:
            [{'originalFile': 'old-filename.pdf', 'filename': 'excellent-filename.pdf', 'description': 'This is a very good
            file that everyone likes.', 'creationDate': '2020-07-06 12:00:00.000000', 'name': 'Evidence Name',
            'renewalDate': '2020-07-06', 'renewalScheduleType': 'ONE_YEAR'}].
        report_ids (Union[Unset, list[float]]): Array of report ids Example: [1, 2, 3].
        policy_ids (Union[Unset, list[float]]): Array of policy ids Example: [1, 2, 3].
        requirement_ids (Union[Unset, list[float]]): Array of requirement ids Example: [1, 2, 3].
        owners (Union[Unset, list[float]]): Array of owner ids Example: [1, 2, 3].
        test_ids (Union[Unset, list[float]]): Array of control test ids Example: [1, 2, 3].
        external_evidence (Union[Unset, list[File]]): External evidence files Example: ["-F 'file=<<Your-Relative-File-
            Path>>'"].
        base_64_files (Union[Unset, str]): JSON string with aray of external evidence in Base64 format. Example:
            [{'base64String': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABg', 'filename': 'excellent-filename'}].
    """

    name: str
    description: str
    question: Union[Unset, str] = UNSET
    code: Union[Unset, str] = UNSET
    activity: Union[Unset, str] = UNSET
    external_evidence_metadata: Union[Unset, str] = UNSET
    report_ids: Union[Unset, list[float]] = UNSET
    policy_ids: Union[Unset, list[float]] = UNSET
    requirement_ids: Union[Unset, list[float]] = UNSET
    owners: Union[Unset, list[float]] = UNSET
    test_ids: Union[Unset, list[float]] = UNSET
    external_evidence: Union[Unset, list[File]] = UNSET
    base_64_files: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        question = self.question

        code = self.code

        activity = self.activity

        external_evidence_metadata = self.external_evidence_metadata

        report_ids: Union[Unset, list[float]] = UNSET
        if not isinstance(self.report_ids, Unset):
            report_ids = self.report_ids

        policy_ids: Union[Unset, list[float]] = UNSET
        if not isinstance(self.policy_ids, Unset):
            policy_ids = self.policy_ids

        requirement_ids: Union[Unset, list[float]] = UNSET
        if not isinstance(self.requirement_ids, Unset):
            requirement_ids = self.requirement_ids

        owners: Union[Unset, list[float]] = UNSET
        if not isinstance(self.owners, Unset):
            owners = self.owners

        test_ids: Union[Unset, list[float]] = UNSET
        if not isinstance(self.test_ids, Unset):
            test_ids = self.test_ids

        external_evidence: Union[Unset, list[FileJsonType]] = UNSET
        if not isinstance(self.external_evidence, Unset):
            external_evidence = []
            for external_evidence_item_data in self.external_evidence:
                external_evidence_item = external_evidence_item_data.to_tuple()

                external_evidence.append(external_evidence_item)

        base_64_files = self.base_64_files

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )
        if question is not UNSET:
            field_dict["question"] = question
        if code is not UNSET:
            field_dict["code"] = code
        if activity is not UNSET:
            field_dict["activity"] = activity
        if external_evidence_metadata is not UNSET:
            field_dict["externalEvidenceMetadata"] = external_evidence_metadata
        if report_ids is not UNSET:
            field_dict["reportIds"] = report_ids
        if policy_ids is not UNSET:
            field_dict["policyIds"] = policy_ids
        if requirement_ids is not UNSET:
            field_dict["requirementIds"] = requirement_ids
        if owners is not UNSET:
            field_dict["owners"] = owners
        if test_ids is not UNSET:
            field_dict["testIds"] = test_ids
        if external_evidence is not UNSET:
            field_dict["externalEvidence"] = external_evidence
        if base_64_files is not UNSET:
            field_dict["base64Files"] = base_64_files

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        name = (None, str(self.name).encode(), "text/plain")

        description = (None, str(self.description).encode(), "text/plain")

        question = (
            self.question if isinstance(self.question, Unset) else (None, str(self.question).encode(), "text/plain")
        )

        code = self.code if isinstance(self.code, Unset) else (None, str(self.code).encode(), "text/plain")

        activity = (
            self.activity if isinstance(self.activity, Unset) else (None, str(self.activity).encode(), "text/plain")
        )

        external_evidence_metadata = (
            self.external_evidence_metadata
            if isinstance(self.external_evidence_metadata, Unset)
            else (None, str(self.external_evidence_metadata).encode(), "text/plain")
        )

        report_ids: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.report_ids, Unset):
            _temp_report_ids = self.report_ids
            report_ids = (None, json.dumps(_temp_report_ids).encode(), "application/json")

        policy_ids: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.policy_ids, Unset):
            _temp_policy_ids = self.policy_ids
            policy_ids = (None, json.dumps(_temp_policy_ids).encode(), "application/json")

        requirement_ids: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.requirement_ids, Unset):
            _temp_requirement_ids = self.requirement_ids
            requirement_ids = (None, json.dumps(_temp_requirement_ids).encode(), "application/json")

        owners: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.owners, Unset):
            _temp_owners = self.owners
            owners = (None, json.dumps(_temp_owners).encode(), "application/json")

        test_ids: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.test_ids, Unset):
            _temp_test_ids = self.test_ids
            test_ids = (None, json.dumps(_temp_test_ids).encode(), "application/json")

        external_evidence: Union[Unset, tuple[None, bytes, str]] = UNSET
        if not isinstance(self.external_evidence, Unset):
            _temp_external_evidence = []
            for external_evidence_item_data in self.external_evidence:
                external_evidence_item = external_evidence_item_data.to_tuple()

                _temp_external_evidence.append(external_evidence_item)
            external_evidence = (None, json.dumps(_temp_external_evidence).encode(), "application/json")

        base_64_files = (
            self.base_64_files
            if isinstance(self.base_64_files, Unset)
            else (None, str(self.base_64_files).encode(), "text/plain")
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )
        if question is not UNSET:
            field_dict["question"] = question
        if code is not UNSET:
            field_dict["code"] = code
        if activity is not UNSET:
            field_dict["activity"] = activity
        if external_evidence_metadata is not UNSET:
            field_dict["externalEvidenceMetadata"] = external_evidence_metadata
        if report_ids is not UNSET:
            field_dict["reportIds"] = report_ids
        if policy_ids is not UNSET:
            field_dict["policyIds"] = policy_ids
        if requirement_ids is not UNSET:
            field_dict["requirementIds"] = requirement_ids
        if owners is not UNSET:
            field_dict["owners"] = owners
        if test_ids is not UNSET:
            field_dict["testIds"] = test_ids
        if external_evidence is not UNSET:
            field_dict["externalEvidence"] = external_evidence
        if base_64_files is not UNSET:
            field_dict["base64Files"] = base_64_files

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        question = d.pop("question", UNSET)

        code = d.pop("code", UNSET)

        activity = d.pop("activity", UNSET)

        external_evidence_metadata = d.pop("externalEvidenceMetadata", UNSET)

        report_ids = cast(list[float], d.pop("reportIds", UNSET))

        policy_ids = cast(list[float], d.pop("policyIds", UNSET))

        requirement_ids = cast(list[float], d.pop("requirementIds", UNSET))

        owners = cast(list[float], d.pop("owners", UNSET))

        test_ids = cast(list[float], d.pop("testIds", UNSET))

        external_evidence = []
        _external_evidence = d.pop("externalEvidence", UNSET)
        for external_evidence_item_data in _external_evidence or []:
            external_evidence_item = File(payload=BytesIO(external_evidence_item_data))

            external_evidence.append(external_evidence_item)

        base_64_files = d.pop("base64Files", UNSET)

        create_control_request_public_dto = cls(
            name=name,
            description=description,
            question=question,
            code=code,
            activity=activity,
            external_evidence_metadata=external_evidence_metadata,
            report_ids=report_ids,
            policy_ids=policy_ids,
            requirement_ids=requirement_ids,
            owners=owners,
            test_ids=test_ids,
            external_evidence=external_evidence,
            base_64_files=base_64_files,
        )

        create_control_request_public_dto.additional_properties = d
        return create_control_request_public_dto

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
