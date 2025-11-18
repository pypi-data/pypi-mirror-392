from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_response_public_dto_metadata_dto_type_0 import EventResponsePublicDtoMetadataDtoType0
    from ..models.event_response_public_dto_metadata_request_type_0 import EventResponsePublicDtoMetadataRequestType0
    from ..models.event_response_public_dto_metadata_response_type_0 import EventResponsePublicDtoMetadataResponseType0
    from ..models.event_response_public_dto_metadata_source_data_type_0 import (
        EventResponsePublicDtoMetadataSourceDataType0,
    )
    from ..models.event_response_public_dto_metadata_target_entities_item_type_0 import (
        EventResponsePublicDtoMetadataTargetEntitiesItemType0,
    )
    from ..models.event_response_public_dto_metadata_target_entity_type_0 import (
        EventResponsePublicDtoMetadataTargetEntityType0,
    )


T = TypeVar("T", bound="EventResponsePublicDtoMetadata")


@_attrs_define
class EventResponsePublicDtoMetadata:
    """The event metadata in JSON

    Example:
        EventMetadataType

    Attributes:
        dto (Union['EventResponsePublicDtoMetadataDtoType0', None, Unset]):
        target_entity (Union['EventResponsePublicDtoMetadataTargetEntityType0', None, Unset]):
        target_entities (Union[Unset, list[Union['EventResponsePublicDtoMetadataTargetEntitiesItemType0', None]]]):
        file_key (Union[None, Unset, str]):
        source_data (Union['EventResponsePublicDtoMetadataSourceDataType0', None, Unset]):
        task_type (Union[None, Unset, float]):
        request (Union['EventResponsePublicDtoMetadataRequestType0', None, Unset]):
        response (Union['EventResponsePublicDtoMetadataResponseType0', None, Unset]):
    """

    dto: Union["EventResponsePublicDtoMetadataDtoType0", None, Unset] = UNSET
    target_entity: Union["EventResponsePublicDtoMetadataTargetEntityType0", None, Unset] = UNSET
    target_entities: Union[Unset, list[Union["EventResponsePublicDtoMetadataTargetEntitiesItemType0", None]]] = UNSET
    file_key: Union[None, Unset, str] = UNSET
    source_data: Union["EventResponsePublicDtoMetadataSourceDataType0", None, Unset] = UNSET
    task_type: Union[None, Unset, float] = UNSET
    request: Union["EventResponsePublicDtoMetadataRequestType0", None, Unset] = UNSET
    response: Union["EventResponsePublicDtoMetadataResponseType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.event_response_public_dto_metadata_dto_type_0 import EventResponsePublicDtoMetadataDtoType0
        from ..models.event_response_public_dto_metadata_request_type_0 import (
            EventResponsePublicDtoMetadataRequestType0,
        )
        from ..models.event_response_public_dto_metadata_response_type_0 import (
            EventResponsePublicDtoMetadataResponseType0,
        )
        from ..models.event_response_public_dto_metadata_source_data_type_0 import (
            EventResponsePublicDtoMetadataSourceDataType0,
        )
        from ..models.event_response_public_dto_metadata_target_entities_item_type_0 import (
            EventResponsePublicDtoMetadataTargetEntitiesItemType0,
        )
        from ..models.event_response_public_dto_metadata_target_entity_type_0 import (
            EventResponsePublicDtoMetadataTargetEntityType0,
        )

        dto: Union[None, Unset, dict[str, Any]]
        if isinstance(self.dto, Unset):
            dto = UNSET
        elif isinstance(self.dto, EventResponsePublicDtoMetadataDtoType0):
            dto = self.dto.to_dict()
        else:
            dto = self.dto

        target_entity: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_entity, Unset):
            target_entity = UNSET
        elif isinstance(self.target_entity, EventResponsePublicDtoMetadataTargetEntityType0):
            target_entity = self.target_entity.to_dict()
        else:
            target_entity = self.target_entity

        target_entities: Union[Unset, list[Union[None, dict[str, Any]]]] = UNSET
        if not isinstance(self.target_entities, Unset):
            target_entities = []
            for target_entities_item_data in self.target_entities:
                target_entities_item: Union[None, dict[str, Any]]
                if isinstance(target_entities_item_data, EventResponsePublicDtoMetadataTargetEntitiesItemType0):
                    target_entities_item = target_entities_item_data.to_dict()
                else:
                    target_entities_item = target_entities_item_data
                target_entities.append(target_entities_item)

        file_key: Union[None, Unset, str]
        if isinstance(self.file_key, Unset):
            file_key = UNSET
        else:
            file_key = self.file_key

        source_data: Union[None, Unset, dict[str, Any]]
        if isinstance(self.source_data, Unset):
            source_data = UNSET
        elif isinstance(self.source_data, EventResponsePublicDtoMetadataSourceDataType0):
            source_data = self.source_data.to_dict()
        else:
            source_data = self.source_data

        task_type: Union[None, Unset, float]
        if isinstance(self.task_type, Unset):
            task_type = UNSET
        else:
            task_type = self.task_type

        request: Union[None, Unset, dict[str, Any]]
        if isinstance(self.request, Unset):
            request = UNSET
        elif isinstance(self.request, EventResponsePublicDtoMetadataRequestType0):
            request = self.request.to_dict()
        else:
            request = self.request

        response: Union[None, Unset, dict[str, Any]]
        if isinstance(self.response, Unset):
            response = UNSET
        elif isinstance(self.response, EventResponsePublicDtoMetadataResponseType0):
            response = self.response.to_dict()
        else:
            response = self.response

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dto is not UNSET:
            field_dict["dto"] = dto
        if target_entity is not UNSET:
            field_dict["targetEntity"] = target_entity
        if target_entities is not UNSET:
            field_dict["targetEntities"] = target_entities
        if file_key is not UNSET:
            field_dict["fileKey"] = file_key
        if source_data is not UNSET:
            field_dict["sourceData"] = source_data
        if task_type is not UNSET:
            field_dict["taskType"] = task_type
        if request is not UNSET:
            field_dict["request"] = request
        if response is not UNSET:
            field_dict["response"] = response

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_response_public_dto_metadata_dto_type_0 import EventResponsePublicDtoMetadataDtoType0
        from ..models.event_response_public_dto_metadata_request_type_0 import (
            EventResponsePublicDtoMetadataRequestType0,
        )
        from ..models.event_response_public_dto_metadata_response_type_0 import (
            EventResponsePublicDtoMetadataResponseType0,
        )
        from ..models.event_response_public_dto_metadata_source_data_type_0 import (
            EventResponsePublicDtoMetadataSourceDataType0,
        )
        from ..models.event_response_public_dto_metadata_target_entities_item_type_0 import (
            EventResponsePublicDtoMetadataTargetEntitiesItemType0,
        )
        from ..models.event_response_public_dto_metadata_target_entity_type_0 import (
            EventResponsePublicDtoMetadataTargetEntityType0,
        )

        d = dict(src_dict)

        def _parse_dto(data: object) -> Union["EventResponsePublicDtoMetadataDtoType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                dto_type_0 = EventResponsePublicDtoMetadataDtoType0.from_dict(data)

                return dto_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoMetadataDtoType0", None, Unset], data)

        dto = _parse_dto(d.pop("dto", UNSET))

        def _parse_target_entity(data: object) -> Union["EventResponsePublicDtoMetadataTargetEntityType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_entity_type_0 = EventResponsePublicDtoMetadataTargetEntityType0.from_dict(data)

                return target_entity_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoMetadataTargetEntityType0", None, Unset], data)

        target_entity = _parse_target_entity(d.pop("targetEntity", UNSET))

        target_entities = []
        _target_entities = d.pop("targetEntities", UNSET)
        for target_entities_item_data in _target_entities or []:

            def _parse_target_entities_item(
                data: object,
            ) -> Union["EventResponsePublicDtoMetadataTargetEntitiesItemType0", None]:
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    target_entities_item_type_0 = EventResponsePublicDtoMetadataTargetEntitiesItemType0.from_dict(data)

                    return target_entities_item_type_0
                except:  # noqa: E722
                    pass
                return cast(Union["EventResponsePublicDtoMetadataTargetEntitiesItemType0", None], data)

            target_entities_item = _parse_target_entities_item(target_entities_item_data)

            target_entities.append(target_entities_item)

        def _parse_file_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_key = _parse_file_key(d.pop("fileKey", UNSET))

        def _parse_source_data(data: object) -> Union["EventResponsePublicDtoMetadataSourceDataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_data_type_0 = EventResponsePublicDtoMetadataSourceDataType0.from_dict(data)

                return source_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoMetadataSourceDataType0", None, Unset], data)

        source_data = _parse_source_data(d.pop("sourceData", UNSET))

        def _parse_task_type(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        task_type = _parse_task_type(d.pop("taskType", UNSET))

        def _parse_request(data: object) -> Union["EventResponsePublicDtoMetadataRequestType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_type_0 = EventResponsePublicDtoMetadataRequestType0.from_dict(data)

                return request_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoMetadataRequestType0", None, Unset], data)

        request = _parse_request(d.pop("request", UNSET))

        def _parse_response(data: object) -> Union["EventResponsePublicDtoMetadataResponseType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_type_0 = EventResponsePublicDtoMetadataResponseType0.from_dict(data)

                return response_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EventResponsePublicDtoMetadataResponseType0", None, Unset], data)

        response = _parse_response(d.pop("response", UNSET))

        event_response_public_dto_metadata = cls(
            dto=dto,
            target_entity=target_entity,
            target_entities=target_entities,
            file_key=file_key,
            source_data=source_data,
            task_type=task_type,
            request=request,
            response=response,
        )

        event_response_public_dto_metadata.additional_properties = d
        return event_response_public_dto_metadata

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
