import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.public_api_key_response_public_dto_access_type import PublicApiKeyResponsePublicDtoAccessType
from ..models.public_api_key_response_public_dto_status import PublicApiKeyResponsePublicDtoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.public_api_key_response_public_dto_user import PublicApiKeyResponsePublicDtoUser


T = TypeVar("T", bound="PublicApiKeyResponsePublicDto")


@_attrs_define
class PublicApiKeyResponsePublicDto:
    """
    Attributes:
        id (str): Public Key Id Example: 1.
        public_api_key (str): The masked UUID Public key Example: ********************************762f.
        name (str): The Public key name Example: My Drata Key.
        status (PublicApiKeyResponsePublicDtoStatus): Status of the public key Example: ACTIVE.
        created_at (datetime.datetime): Key created date timestamp Example: 2025-07-01T16:45:55.246Z.
        expires_at (datetime.datetime): Key expires date timestamp Example: 2020-07-06.
        user (PublicApiKeyResponsePublicDtoUser): A user Info Example: {'firstName': 'FirstnameTest', 'lastName':
            'LastnameTest', 'email': 'Email@test.com', 'avatarUrl': 'https://cdn-prod.imgpilot.com/avatar.png'}.
        last_used_at (Union[Unset, datetime.datetime]): Key last used date timestamp Example: 2025-07-01T16:45:55.246Z.
        deleted_at (Union[Unset, datetime.datetime]): Key deleted date timestamp Example: 2025-07-01T16:45:55.246Z.
        permissions (Union[Unset, list[str]]): Public key permissions list Example: ['CONTROLS_GET'].
        allow_list_ip_addresses (Union[Unset, list[str]]): Public key allowed ip addresses list Example:
            ['142.251.35.14', '684D:1111:222:3333:4444:5555:6:77'].
        access_type (Union[Unset, PublicApiKeyResponsePublicDtoAccessType]): Access type Example: ALL_READ.
    """

    id: str
    public_api_key: str
    name: str
    status: PublicApiKeyResponsePublicDtoStatus
    created_at: datetime.datetime
    expires_at: datetime.datetime
    user: "PublicApiKeyResponsePublicDtoUser"
    last_used_at: Union[Unset, datetime.datetime] = UNSET
    deleted_at: Union[Unset, datetime.datetime] = UNSET
    permissions: Union[Unset, list[str]] = UNSET
    allow_list_ip_addresses: Union[Unset, list[str]] = UNSET
    access_type: Union[Unset, PublicApiKeyResponsePublicDtoAccessType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        public_api_key = self.public_api_key

        name = self.name

        status = self.status.value

        created_at = self.created_at.isoformat()

        expires_at = self.expires_at.isoformat()

        user = self.user.to_dict()

        last_used_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_used_at, Unset):
            last_used_at = self.last_used_at.isoformat()

        deleted_at: Union[Unset, str] = UNSET
        if not isinstance(self.deleted_at, Unset):
            deleted_at = self.deleted_at.isoformat()

        permissions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        allow_list_ip_addresses: Union[Unset, list[str]] = UNSET
        if not isinstance(self.allow_list_ip_addresses, Unset):
            allow_list_ip_addresses = self.allow_list_ip_addresses

        access_type: Union[Unset, str] = UNSET
        if not isinstance(self.access_type, Unset):
            access_type = self.access_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "publicApiKey": public_api_key,
                "name": name,
                "status": status,
                "createdAt": created_at,
                "expiresAt": expires_at,
                "user": user,
            }
        )
        if last_used_at is not UNSET:
            field_dict["lastUsedAt"] = last_used_at
        if deleted_at is not UNSET:
            field_dict["deletedAt"] = deleted_at
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if allow_list_ip_addresses is not UNSET:
            field_dict["allowListIPAddresses"] = allow_list_ip_addresses
        if access_type is not UNSET:
            field_dict["accessType"] = access_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.public_api_key_response_public_dto_user import PublicApiKeyResponsePublicDtoUser

        d = dict(src_dict)
        id = d.pop("id")

        public_api_key = d.pop("publicApiKey")

        name = d.pop("name")

        status = PublicApiKeyResponsePublicDtoStatus(d.pop("status"))

        created_at = isoparse(d.pop("createdAt"))

        expires_at = isoparse(d.pop("expiresAt"))

        user = PublicApiKeyResponsePublicDtoUser.from_dict(d.pop("user"))

        _last_used_at = d.pop("lastUsedAt", UNSET)
        last_used_at: Union[Unset, datetime.datetime]
        if isinstance(_last_used_at, Unset):
            last_used_at = UNSET
        else:
            last_used_at = isoparse(_last_used_at)

        _deleted_at = d.pop("deletedAt", UNSET)
        deleted_at: Union[Unset, datetime.datetime]
        if isinstance(_deleted_at, Unset):
            deleted_at = UNSET
        else:
            deleted_at = isoparse(_deleted_at)

        permissions = cast(list[str], d.pop("permissions", UNSET))

        allow_list_ip_addresses = cast(list[str], d.pop("allowListIPAddresses", UNSET))

        _access_type = d.pop("accessType", UNSET)
        access_type: Union[Unset, PublicApiKeyResponsePublicDtoAccessType]
        if isinstance(_access_type, Unset):
            access_type = UNSET
        else:
            access_type = PublicApiKeyResponsePublicDtoAccessType(_access_type)

        public_api_key_response_public_dto = cls(
            id=id,
            public_api_key=public_api_key,
            name=name,
            status=status,
            created_at=created_at,
            expires_at=expires_at,
            user=user,
            last_used_at=last_used_at,
            deleted_at=deleted_at,
            permissions=permissions,
            allow_list_ip_addresses=allow_list_ip_addresses,
            access_type=access_type,
        )

        public_api_key_response_public_dto.additional_properties = d
        return public_api_key_response_public_dto

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
