import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.event_response_public_dto_connection_type_0 import EventResponsePublicDtoConnectionType0
    from ..models.event_response_public_dto_issues_item import EventResponsePublicDtoIssuesItem
    from ..models.event_response_public_dto_metadata import EventResponsePublicDtoMetadata
    from ..models.user_response_public_dto import UserResponsePublicDto


T = TypeVar("T", bound="EventResponsePublicDto")


@_attrs_define
class EventResponsePublicDto:
    """
    Attributes:
        id (str): Event UUID Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        type_ (str): The type of event Example: COMPANY_DATA_UPDATED.
        category (str): The type of event Example: COMPANY.
        source (str): The source of the event (APP or AUTOPILOT) Example: APP.
        description (str): The description of the event Example: Wile E. Coyote updated the company info..
        metadata (EventResponsePublicDtoMetadata): The event metadata in JSON Example: EventMetadataType.
        status (Union[None, str]): The result of the test if the event type is an Autopilot test, otherwise null
            Example: PASSED.
        created_at (datetime.datetime): Report created date timestamp Example: 2025-07-01T16:45:55.246Z.
        user (Union['UserResponsePublicDto', None]): The user that uploaded the report
        connection (Union['EventResponsePublicDtoConnectionType0', None]): The associated connection if this event has
            one
        request_description (Union[None, str]): The human readable explanation of the workings of the associated AP test
            Example: Data was fetched from https://xyz.com/api/v1/data.
        issues (list['EventResponsePublicDtoIssuesItem']): The issues associated to this event, if any
    """

    id: str
    type_: str
    category: str
    source: str
    description: str
    metadata: "EventResponsePublicDtoMetadata"
    status: Union[None, str]
    created_at: datetime.datetime
    user: Union["UserResponsePublicDto", None]
    connection: Union["EventResponsePublicDtoConnectionType0", None]
    request_description: Union[None, str]
    issues: list["EventResponsePublicDtoIssuesItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.event_response_public_dto_connection_type_0 import EventResponsePublicDtoConnectionType0
        from ..models.user_response_public_dto import UserResponsePublicDto

        id = self.id

        type_ = self.type_

        category = self.category

        source = self.source

        description = self.description

        metadata = self.metadata.to_dict()

        status: Union[None, str]
        status = self.status

        created_at = self.created_at.isoformat()

        user: Union[None, dict[str, Any]]
        if isinstance(self.user, UserResponsePublicDto):
            user = self.user.to_dict()
        else:
            user = self.user

        connection: Union[None, dict[str, Any]]
        if isinstance(self.connection, EventResponsePublicDtoConnectionType0):
            connection = self.connection.to_dict()
        else:
            connection = self.connection

        request_description: Union[None, str]
        request_description = self.request_description

        issues = []
        for issues_item_data in self.issues:
            issues_item = issues_item_data.to_dict()
            issues.append(issues_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "category": category,
                "source": source,
                "description": description,
                "metadata": metadata,
                "status": status,
                "createdAt": created_at,
                "user": user,
                "connection": connection,
                "requestDescription": request_description,
                "issues": issues,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_response_public_dto_connection_type_0 import EventResponsePublicDtoConnectionType0
        from ..models.event_response_public_dto_issues_item import EventResponsePublicDtoIssuesItem
        from ..models.event_response_public_dto_metadata import EventResponsePublicDtoMetadata
        from ..models.user_response_public_dto import UserResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        category = d.pop("category")

        source = d.pop("source")

        description = d.pop("description")

        metadata = EventResponsePublicDtoMetadata.from_dict(d.pop("metadata"))

        def _parse_status(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        status = _parse_status(d.pop("status"))

        created_at = isoparse(d.pop("createdAt"))

        def _parse_user(data: object) -> Union["UserResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_type_1 = UserResponsePublicDto.from_dict(data)

                return user_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserResponsePublicDto", None], data)

        user = _parse_user(d.pop("user"))

        def _parse_connection(data: object) -> Union["EventResponsePublicDtoConnectionType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                connection_type_0 = EventResponsePublicDtoConnectionType0.from_dict(data)

                return connection_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoConnectionType0", None], data)

        connection = _parse_connection(d.pop("connection"))

        def _parse_request_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        request_description = _parse_request_description(d.pop("requestDescription"))

        issues = []
        _issues = d.pop("issues")
        for issues_item_data in _issues:
            issues_item = EventResponsePublicDtoIssuesItem.from_dict(issues_item_data)

            issues.append(issues_item)

        event_response_public_dto = cls(
            id=id,
            type_=type_,
            category=category,
            source=source,
            description=description,
            metadata=metadata,
            status=status,
            created_at=created_at,
            user=user,
            connection=connection,
            request_description=request_description,
            issues=issues,
        )

        event_response_public_dto.additional_properties = d
        return event_response_public_dto

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
