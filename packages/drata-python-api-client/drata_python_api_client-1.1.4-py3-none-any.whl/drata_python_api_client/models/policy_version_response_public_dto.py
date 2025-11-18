import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.policy_version_response_public_dto_status import PolicyVersionResponsePublicDtoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grace_period_sla_response_public_dto import GracePeriodSLAResponsePublicDto
    from ..models.p3_matrix_sla_response_public_dto import P3MatrixSLAResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto
    from ..models.week_time_frame_sla_response_public_dto import WeekTimeFrameSLAResponsePublicDto


T = TypeVar("T", bound="PolicyVersionResponsePublicDto")


@_attrs_define
class PolicyVersionResponsePublicDto:
    """
    Attributes:
        id (float): Policy version ID Example: 1.
        version (float): The policy version Example: 1.
        minor_version (float): The policy minor version Example: 1.
        current (bool): Is this the current policy (last uploaded/created) Example: True.
        type_ (str): The policy version type Example: UPLOADED.
        file_url (Union[None, str]): The secure URL to the policy version Example:
            http://localhost:5000/download/policies/1.
        doc_viewer (str): The type of document viewer to use Example: NATIVE.
        description (Union[None, str]): The policy version description Example: This policy defines how you do XYZ.
        html (Union[None, str]): The policy version description html Example: <html><body>Text</body></html>.
        renewal_date (str): Policy renewal date Example: 2025-07-01T16:45:55.246Z.
        created_at (datetime.datetime): Date and time when the policy version was created Example:
            2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Date and time when the policy version was updated Example:
            2025-07-01T16:45:55.246Z.
        owner (Union['UserResponsePublicDto', None]): The user that is assigned as the owner of this policy
        changes_explanation (Union[None, str]): The description of the changes done in the update Example: - This is
            what changes in the new version. - And this is another change..
        status (PolicyVersionResponsePublicDtoStatus): The policy version status. Example: DRAFT.
        week_time_frame_sl_as (Union[Unset, list['WeekTimeFrameSLAResponsePublicDto']]): The set of week timeframe SLA
            values for this policy version Example: WeekTimeFrameSLAResponsePublicDto[].
        p_3_matrix_sl_as (Union[Unset, list['P3MatrixSLAResponsePublicDto']]): The set of P3 Matrix SLA values for this
            policy Example: P3MatrixSLAsResponsePublicDto[].
        grace_period_sl_as (Union[Unset, list['GracePeriodSLAResponsePublicDto']]): The set of grace period SLA values
            for this policy version Example: GracePeriodSLAResponsePublicDto[].
        approved_at (Union[None, Unset, datetime.datetime]): Date and time when the policy version was approved Example:
            2025-07-01T16:45:55.246Z.
        published_at (Union[None, Unset, datetime.datetime]): Date and time when the policy version was published
            Example: 2025-07-01T16:45:55.246Z.
        html_last_updated (Union[None, Unset, datetime.datetime]): Date and time when the policy version html was
            updated Example: 2025-07-01T16:45:55.246Z.
    """

    id: float
    version: float
    minor_version: float
    current: bool
    type_: str
    file_url: Union[None, str]
    doc_viewer: str
    description: Union[None, str]
    html: Union[None, str]
    renewal_date: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: Union["UserResponsePublicDto", None]
    changes_explanation: Union[None, str]
    status: PolicyVersionResponsePublicDtoStatus
    week_time_frame_sl_as: Union[Unset, list["WeekTimeFrameSLAResponsePublicDto"]] = UNSET
    p_3_matrix_sl_as: Union[Unset, list["P3MatrixSLAResponsePublicDto"]] = UNSET
    grace_period_sl_as: Union[Unset, list["GracePeriodSLAResponsePublicDto"]] = UNSET
    approved_at: Union[None, Unset, datetime.datetime] = UNSET
    published_at: Union[None, Unset, datetime.datetime] = UNSET
    html_last_updated: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_response_public_dto import UserResponsePublicDto

        id = self.id

        version = self.version

        minor_version = self.minor_version

        current = self.current

        type_ = self.type_

        file_url: Union[None, str]
        file_url = self.file_url

        doc_viewer = self.doc_viewer

        description: Union[None, str]
        description = self.description

        html: Union[None, str]
        html = self.html

        renewal_date = self.renewal_date

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        owner: Union[None, dict[str, Any]]
        if isinstance(self.owner, UserResponsePublicDto):
            owner = self.owner.to_dict()
        else:
            owner = self.owner

        changes_explanation: Union[None, str]
        changes_explanation = self.changes_explanation

        status = self.status.value

        week_time_frame_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.week_time_frame_sl_as, Unset):
            week_time_frame_sl_as = []
            for week_time_frame_sl_as_item_data in self.week_time_frame_sl_as:
                week_time_frame_sl_as_item = week_time_frame_sl_as_item_data.to_dict()
                week_time_frame_sl_as.append(week_time_frame_sl_as_item)

        p_3_matrix_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.p_3_matrix_sl_as, Unset):
            p_3_matrix_sl_as = []
            for p_3_matrix_sl_as_item_data in self.p_3_matrix_sl_as:
                p_3_matrix_sl_as_item = p_3_matrix_sl_as_item_data.to_dict()
                p_3_matrix_sl_as.append(p_3_matrix_sl_as_item)

        grace_period_sl_as: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.grace_period_sl_as, Unset):
            grace_period_sl_as = []
            for grace_period_sl_as_item_data in self.grace_period_sl_as:
                grace_period_sl_as_item = grace_period_sl_as_item_data.to_dict()
                grace_period_sl_as.append(grace_period_sl_as_item)

        approved_at: Union[None, Unset, str]
        if isinstance(self.approved_at, Unset):
            approved_at = UNSET
        elif isinstance(self.approved_at, datetime.datetime):
            approved_at = self.approved_at.isoformat()
        else:
            approved_at = self.approved_at

        published_at: Union[None, Unset, str]
        if isinstance(self.published_at, Unset):
            published_at = UNSET
        elif isinstance(self.published_at, datetime.datetime):
            published_at = self.published_at.isoformat()
        else:
            published_at = self.published_at

        html_last_updated: Union[None, Unset, str]
        if isinstance(self.html_last_updated, Unset):
            html_last_updated = UNSET
        elif isinstance(self.html_last_updated, datetime.datetime):
            html_last_updated = self.html_last_updated.isoformat()
        else:
            html_last_updated = self.html_last_updated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "version": version,
                "minorVersion": minor_version,
                "current": current,
                "type": type_,
                "fileUrl": file_url,
                "docViewer": doc_viewer,
                "description": description,
                "html": html,
                "renewalDate": renewal_date,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "owner": owner,
                "changesExplanation": changes_explanation,
                "status": status,
            }
        )
        if week_time_frame_sl_as is not UNSET:
            field_dict["weekTimeFrameSLAs"] = week_time_frame_sl_as
        if p_3_matrix_sl_as is not UNSET:
            field_dict["p3MatrixSLAs"] = p_3_matrix_sl_as
        if grace_period_sl_as is not UNSET:
            field_dict["gracePeriodSLAs"] = grace_period_sl_as
        if approved_at is not UNSET:
            field_dict["approvedAt"] = approved_at
        if published_at is not UNSET:
            field_dict["publishedAt"] = published_at
        if html_last_updated is not UNSET:
            field_dict["htmlLastUpdated"] = html_last_updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.grace_period_sla_response_public_dto import GracePeriodSLAResponsePublicDto
        from ..models.p3_matrix_sla_response_public_dto import P3MatrixSLAResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto
        from ..models.week_time_frame_sla_response_public_dto import WeekTimeFrameSLAResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        version = d.pop("version")

        minor_version = d.pop("minorVersion")

        current = d.pop("current")

        type_ = d.pop("type")

        def _parse_file_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        file_url = _parse_file_url(d.pop("fileUrl"))

        doc_viewer = d.pop("docViewer")

        def _parse_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        description = _parse_description(d.pop("description"))

        def _parse_html(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        html = _parse_html(d.pop("html"))

        renewal_date = d.pop("renewalDate")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_owner(data: object) -> Union["UserResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                owner_type_1 = UserResponsePublicDto.from_dict(data)

                return owner_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserResponsePublicDto", None], data)

        owner = _parse_owner(d.pop("owner"))

        def _parse_changes_explanation(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        changes_explanation = _parse_changes_explanation(d.pop("changesExplanation"))

        status = PolicyVersionResponsePublicDtoStatus(d.pop("status"))

        week_time_frame_sl_as = []
        _week_time_frame_sl_as = d.pop("weekTimeFrameSLAs", UNSET)
        for week_time_frame_sl_as_item_data in _week_time_frame_sl_as or []:
            week_time_frame_sl_as_item = WeekTimeFrameSLAResponsePublicDto.from_dict(week_time_frame_sl_as_item_data)

            week_time_frame_sl_as.append(week_time_frame_sl_as_item)

        p_3_matrix_sl_as = []
        _p_3_matrix_sl_as = d.pop("p3MatrixSLAs", UNSET)
        for p_3_matrix_sl_as_item_data in _p_3_matrix_sl_as or []:
            p_3_matrix_sl_as_item = P3MatrixSLAResponsePublicDto.from_dict(p_3_matrix_sl_as_item_data)

            p_3_matrix_sl_as.append(p_3_matrix_sl_as_item)

        grace_period_sl_as = []
        _grace_period_sl_as = d.pop("gracePeriodSLAs", UNSET)
        for grace_period_sl_as_item_data in _grace_period_sl_as or []:
            grace_period_sl_as_item = GracePeriodSLAResponsePublicDto.from_dict(grace_period_sl_as_item_data)

            grace_period_sl_as.append(grace_period_sl_as_item)

        def _parse_approved_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                approved_at_type_0 = isoparse(data)

                return approved_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        approved_at = _parse_approved_at(d.pop("approvedAt", UNSET))

        def _parse_published_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                published_at_type_0 = isoparse(data)

                return published_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        published_at = _parse_published_at(d.pop("publishedAt", UNSET))

        def _parse_html_last_updated(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                html_last_updated_type_0 = isoparse(data)

                return html_last_updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        html_last_updated = _parse_html_last_updated(d.pop("htmlLastUpdated", UNSET))

        policy_version_response_public_dto = cls(
            id=id,
            version=version,
            minor_version=minor_version,
            current=current,
            type_=type_,
            file_url=file_url,
            doc_viewer=doc_viewer,
            description=description,
            html=html,
            renewal_date=renewal_date,
            created_at=created_at,
            updated_at=updated_at,
            owner=owner,
            changes_explanation=changes_explanation,
            status=status,
            week_time_frame_sl_as=week_time_frame_sl_as,
            p_3_matrix_sl_as=p_3_matrix_sl_as,
            grace_period_sl_as=grace_period_sl_as,
            approved_at=approved_at,
            published_at=published_at,
            html_last_updated=html_last_updated,
        )

        policy_version_response_public_dto.additional_properties = d
        return policy_version_response_public_dto

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
