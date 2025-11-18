from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ControlTestResponsePublicDtoGraph")


@_attrs_define
class ControlTestResponsePublicDtoGraph:
    """Graph of control test. history

    Example:
        ControlTestInstanceHistoryType

    Attributes:
        labels (Union[Unset, list[str]]):
        passed (Union[Unset, list[float]]):
        failed (Union[Unset, list[float]]):
        errored (Union[Unset, list[float]]):
    """

    labels: Union[Unset, list[str]] = UNSET
    passed: Union[Unset, list[float]] = UNSET
    failed: Union[Unset, list[float]] = UNSET
    errored: Union[Unset, list[float]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        passed: Union[Unset, list[float]] = UNSET
        if not isinstance(self.passed, Unset):
            passed = self.passed

        failed: Union[Unset, list[float]] = UNSET
        if not isinstance(self.failed, Unset):
            failed = self.failed

        errored: Union[Unset, list[float]] = UNSET
        if not isinstance(self.errored, Unset):
            errored = self.errored

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if labels is not UNSET:
            field_dict["labels"] = labels
        if passed is not UNSET:
            field_dict["passed"] = passed
        if failed is not UNSET:
            field_dict["failed"] = failed
        if errored is not UNSET:
            field_dict["errored"] = errored

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        labels = cast(list[str], d.pop("labels", UNSET))

        passed = cast(list[float], d.pop("passed", UNSET))

        failed = cast(list[float], d.pop("failed", UNSET))

        errored = cast(list[float], d.pop("errored", UNSET))

        control_test_response_public_dto_graph = cls(
            labels=labels,
            passed=passed,
            failed=failed,
            errored=errored,
        )

        return control_test_response_public_dto_graph
