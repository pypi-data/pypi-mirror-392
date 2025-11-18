from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vendor_request_public_dto_category import VendorRequestPublicDtoCategory
from ..models.vendor_request_public_dto_data_accessed_or_processed_list_type_0_item import (
    VendorRequestPublicDtoDataAccessedOrProcessedListType0Item,
)
from ..models.vendor_request_public_dto_environment_access import VendorRequestPublicDtoEnvironmentAccess
from ..models.vendor_request_public_dto_impact_level import VendorRequestPublicDtoImpactLevel
from ..models.vendor_request_public_dto_operational_impact import VendorRequestPublicDtoOperationalImpact
from ..models.vendor_request_public_dto_password_policy import VendorRequestPublicDtoPasswordPolicy
from ..models.vendor_request_public_dto_renewal_schedule_type import VendorRequestPublicDtoRenewalScheduleType
from ..models.vendor_request_public_dto_risk import VendorRequestPublicDtoRisk
from ..models.vendor_request_public_dto_status import VendorRequestPublicDtoStatus
from ..models.vendor_request_public_dto_type import VendorRequestPublicDtoType
from ..types import UNSET, Unset

T = TypeVar("T", bound="VendorRequestPublicDto")


@_attrs_define
class VendorRequestPublicDto:
    """
    Attributes:
        name (str): The name of the vendor Example: Acme.
        is_sub_processor (bool): Indicates whether this vendor is considered a sub-processor
        is_sub_processor_active (bool): Indicates whether this subprocessor is active
        has_pii (bool): Indicates whether this vendor stores any type of Personally Identifiable Information (PII)
            Example: True.
        password_requires_min_length (bool): Indicates whether there is a minimum length requirement for password
            Example: True.
        password_requires_number (bool): Indicates whether a password requires numbers Example: True.
        password_requires_symbol (bool): Indicates whether a password requires non-alpha-numeric characters Example:
            True.
        password_mfa_enabled (bool): Indicates whether multi-factor authentication is enabled for this vendor Example:
            True.
        category (Union[Unset, VendorRequestPublicDtoCategory]): The type of vendor Example: ENGINEERING.
        risk (Union[Unset, VendorRequestPublicDtoRisk]): The level of risk associated with customer data Example:
            MODERATE.
        status (Union[Unset, VendorRequestPublicDtoStatus]): The status of vendor Example: UNDER_REVIEW.
        critical (Union[None, Unset, bool]): Does this vendor is considered as critical
        user_id (Union[None, Unset, float]): The user ID of the person responsible for vendor compliance Example: 1.
        url (Union[None, Unset, str]): Vendor URL Example: https://acme.com.
        privacy_url (Union[Unset, str]): Vendor Privacy Policy URL Example: https://acme.com/privacy.
        terms_url (Union[Unset, str]): Vendor Terms of Use URL Example: https://acme.com/terms.
        services_provided (Union[None, Unset, str]): Description of the services provided by the vendor Example: Perform
            security scans once a month.
        data_stored (Union[None, Unset, str]): Description of the type of data the vendor stores Example: resulting
            reports of security scans.
        location (Union[Unset, str]): Location where the vendor services are provided Example: San Diego.
        password_policy (Union[Unset, VendorRequestPublicDtoPasswordPolicy]): The vendor password policy Example:
            USERNAME_PASSWORD.
        password_min_length (Union[None, Unset, float]): Minimum character length required for a password Example: 8.
        contact_at_vendor (Union[None, Unset, str]): Name of the corresponding account manager for this vendor Example:
            John Doe.
        contacts_email (Union[None, Unset, str]): Email of the corresponding account manager for this vendor Example:
            jdoe@company.com.
        notes (Union[Unset, str]): Additional notes for vendor Example: Meeting once a month to adjust contract.
        renewal_date (Union[None, Unset, str]): Vendor renewal date Example: 2025-07-01T16:45:55.246Z.
        renewal_schedule_type (Union[Unset, VendorRequestPublicDtoRenewalScheduleType]): Vendor renewal schedule type
            Example: ONE_YEAR.
        confirmed (Union[None, Unset, bool]): Is all vendor data confirmed? Example: True.
        type_ (Union[Unset, VendorRequestPublicDtoType]): Vendor type identifier Example: VENDOR.
        account_id (Union[Unset, str]): Account Id Example: 36.
        operational_impact (Union[Unset, VendorRequestPublicDtoOperationalImpact]): Vendor level of operational impact
            Example: IMPORTANT.
        environment_access (Union[Unset, VendorRequestPublicDtoEnvironmentAccess]): Vendor environment access privileges
            Example: READ_ONLY.
        impact_level (Union[Unset, VendorRequestPublicDtoImpactLevel]): Vendor overall impact level Example:
            INSIGNIFICANT.
        data_accessed_or_processed_list (Union[None, Unset,
            list[VendorRequestPublicDtoDataAccessedOrProcessedListType0Item]]): List of data accessed or processed enum type
            Example: ['FINANCIAL', 'GENERAL'].
        integrations (Union[Unset, list[float]]): List of vendor IDs Example: [1, 2, 3].
        cost (Union[None, Unset, str]): Annual Contract Value for the vendor in Cents unit Example: 1088.
        exclude_ids (Union[None, Unset, list[float]]): Excluded vendor ids. Example: [1, 2].
    """

    name: str
    is_sub_processor: bool
    is_sub_processor_active: bool
    has_pii: bool
    password_requires_min_length: bool
    password_requires_number: bool
    password_requires_symbol: bool
    password_mfa_enabled: bool
    category: Union[Unset, VendorRequestPublicDtoCategory] = UNSET
    risk: Union[Unset, VendorRequestPublicDtoRisk] = UNSET
    status: Union[Unset, VendorRequestPublicDtoStatus] = UNSET
    critical: Union[None, Unset, bool] = UNSET
    user_id: Union[None, Unset, float] = UNSET
    url: Union[None, Unset, str] = UNSET
    privacy_url: Union[Unset, str] = UNSET
    terms_url: Union[Unset, str] = UNSET
    services_provided: Union[None, Unset, str] = UNSET
    data_stored: Union[None, Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    password_policy: Union[Unset, VendorRequestPublicDtoPasswordPolicy] = UNSET
    password_min_length: Union[None, Unset, float] = UNSET
    contact_at_vendor: Union[None, Unset, str] = UNSET
    contacts_email: Union[None, Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    renewal_date: Union[None, Unset, str] = UNSET
    renewal_schedule_type: Union[Unset, VendorRequestPublicDtoRenewalScheduleType] = UNSET
    confirmed: Union[None, Unset, bool] = UNSET
    type_: Union[Unset, VendorRequestPublicDtoType] = UNSET
    account_id: Union[Unset, str] = UNSET
    operational_impact: Union[Unset, VendorRequestPublicDtoOperationalImpact] = UNSET
    environment_access: Union[Unset, VendorRequestPublicDtoEnvironmentAccess] = UNSET
    impact_level: Union[Unset, VendorRequestPublicDtoImpactLevel] = UNSET
    data_accessed_or_processed_list: Union[
        None, Unset, list[VendorRequestPublicDtoDataAccessedOrProcessedListType0Item]
    ] = UNSET
    integrations: Union[Unset, list[float]] = UNSET
    cost: Union[None, Unset, str] = UNSET
    exclude_ids: Union[None, Unset, list[float]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        is_sub_processor = self.is_sub_processor

        is_sub_processor_active = self.is_sub_processor_active

        has_pii = self.has_pii

        password_requires_min_length = self.password_requires_min_length

        password_requires_number = self.password_requires_number

        password_requires_symbol = self.password_requires_symbol

        password_mfa_enabled = self.password_mfa_enabled

        category: Union[Unset, str] = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        risk: Union[Unset, str] = UNSET
        if not isinstance(self.risk, Unset):
            risk = self.risk.value

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        critical: Union[None, Unset, bool]
        if isinstance(self.critical, Unset):
            critical = UNSET
        else:
            critical = self.critical

        user_id: Union[None, Unset, float]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        url: Union[None, Unset, str]
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        privacy_url = self.privacy_url

        terms_url = self.terms_url

        services_provided: Union[None, Unset, str]
        if isinstance(self.services_provided, Unset):
            services_provided = UNSET
        else:
            services_provided = self.services_provided

        data_stored: Union[None, Unset, str]
        if isinstance(self.data_stored, Unset):
            data_stored = UNSET
        else:
            data_stored = self.data_stored

        location = self.location

        password_policy: Union[Unset, str] = UNSET
        if not isinstance(self.password_policy, Unset):
            password_policy = self.password_policy.value

        password_min_length: Union[None, Unset, float]
        if isinstance(self.password_min_length, Unset):
            password_min_length = UNSET
        else:
            password_min_length = self.password_min_length

        contact_at_vendor: Union[None, Unset, str]
        if isinstance(self.contact_at_vendor, Unset):
            contact_at_vendor = UNSET
        else:
            contact_at_vendor = self.contact_at_vendor

        contacts_email: Union[None, Unset, str]
        if isinstance(self.contacts_email, Unset):
            contacts_email = UNSET
        else:
            contacts_email = self.contacts_email

        notes = self.notes

        renewal_date: Union[None, Unset, str]
        if isinstance(self.renewal_date, Unset):
            renewal_date = UNSET
        else:
            renewal_date = self.renewal_date

        renewal_schedule_type: Union[Unset, str] = UNSET
        if not isinstance(self.renewal_schedule_type, Unset):
            renewal_schedule_type = self.renewal_schedule_type.value

        confirmed: Union[None, Unset, bool]
        if isinstance(self.confirmed, Unset):
            confirmed = UNSET
        else:
            confirmed = self.confirmed

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        account_id = self.account_id

        operational_impact: Union[Unset, str] = UNSET
        if not isinstance(self.operational_impact, Unset):
            operational_impact = self.operational_impact.value

        environment_access: Union[Unset, str] = UNSET
        if not isinstance(self.environment_access, Unset):
            environment_access = self.environment_access.value

        impact_level: Union[Unset, str] = UNSET
        if not isinstance(self.impact_level, Unset):
            impact_level = self.impact_level.value

        data_accessed_or_processed_list: Union[None, Unset, list[str]]
        if isinstance(self.data_accessed_or_processed_list, Unset):
            data_accessed_or_processed_list = UNSET
        elif isinstance(self.data_accessed_or_processed_list, list):
            data_accessed_or_processed_list = []
            for data_accessed_or_processed_list_type_0_item_data in self.data_accessed_or_processed_list:
                data_accessed_or_processed_list_type_0_item = data_accessed_or_processed_list_type_0_item_data.value
                data_accessed_or_processed_list.append(data_accessed_or_processed_list_type_0_item)

        else:
            data_accessed_or_processed_list = self.data_accessed_or_processed_list

        integrations: Union[Unset, list[float]] = UNSET
        if not isinstance(self.integrations, Unset):
            integrations = self.integrations

        cost: Union[None, Unset, str]
        if isinstance(self.cost, Unset):
            cost = UNSET
        else:
            cost = self.cost

        exclude_ids: Union[None, Unset, list[float]]
        if isinstance(self.exclude_ids, Unset):
            exclude_ids = UNSET
        elif isinstance(self.exclude_ids, list):
            exclude_ids = self.exclude_ids

        else:
            exclude_ids = self.exclude_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "isSubProcessor": is_sub_processor,
                "isSubProcessorActive": is_sub_processor_active,
                "hasPii": has_pii,
                "passwordRequiresMinLength": password_requires_min_length,
                "passwordRequiresNumber": password_requires_number,
                "passwordRequiresSymbol": password_requires_symbol,
                "passwordMfaEnabled": password_mfa_enabled,
            }
        )
        if category is not UNSET:
            field_dict["category"] = category
        if risk is not UNSET:
            field_dict["risk"] = risk
        if status is not UNSET:
            field_dict["status"] = status
        if critical is not UNSET:
            field_dict["critical"] = critical
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if url is not UNSET:
            field_dict["url"] = url
        if privacy_url is not UNSET:
            field_dict["privacyUrl"] = privacy_url
        if terms_url is not UNSET:
            field_dict["termsUrl"] = terms_url
        if services_provided is not UNSET:
            field_dict["servicesProvided"] = services_provided
        if data_stored is not UNSET:
            field_dict["dataStored"] = data_stored
        if location is not UNSET:
            field_dict["location"] = location
        if password_policy is not UNSET:
            field_dict["passwordPolicy"] = password_policy
        if password_min_length is not UNSET:
            field_dict["passwordMinLength"] = password_min_length
        if contact_at_vendor is not UNSET:
            field_dict["contactAtVendor"] = contact_at_vendor
        if contacts_email is not UNSET:
            field_dict["contactsEmail"] = contacts_email
        if notes is not UNSET:
            field_dict["notes"] = notes
        if renewal_date is not UNSET:
            field_dict["renewalDate"] = renewal_date
        if renewal_schedule_type is not UNSET:
            field_dict["renewalScheduleType"] = renewal_schedule_type
        if confirmed is not UNSET:
            field_dict["confirmed"] = confirmed
        if type_ is not UNSET:
            field_dict["type"] = type_
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if operational_impact is not UNSET:
            field_dict["operationalImpact"] = operational_impact
        if environment_access is not UNSET:
            field_dict["environmentAccess"] = environment_access
        if impact_level is not UNSET:
            field_dict["impactLevel"] = impact_level
        if data_accessed_or_processed_list is not UNSET:
            field_dict["dataAccessedOrProcessedList"] = data_accessed_or_processed_list
        if integrations is not UNSET:
            field_dict["integrations"] = integrations
        if cost is not UNSET:
            field_dict["cost"] = cost
        if exclude_ids is not UNSET:
            field_dict["excludeIds"] = exclude_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        is_sub_processor = d.pop("isSubProcessor")

        is_sub_processor_active = d.pop("isSubProcessorActive")

        has_pii = d.pop("hasPii")

        password_requires_min_length = d.pop("passwordRequiresMinLength")

        password_requires_number = d.pop("passwordRequiresNumber")

        password_requires_symbol = d.pop("passwordRequiresSymbol")

        password_mfa_enabled = d.pop("passwordMfaEnabled")

        _category = d.pop("category", UNSET)
        category: Union[Unset, VendorRequestPublicDtoCategory]
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = VendorRequestPublicDtoCategory(_category)

        _risk = d.pop("risk", UNSET)
        risk: Union[Unset, VendorRequestPublicDtoRisk]
        if isinstance(_risk, Unset):
            risk = UNSET
        else:
            risk = VendorRequestPublicDtoRisk(_risk)

        _status = d.pop("status", UNSET)
        status: Union[Unset, VendorRequestPublicDtoStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = VendorRequestPublicDtoStatus(_status)

        def _parse_critical(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        critical = _parse_critical(d.pop("critical", UNSET))

        def _parse_user_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        user_id = _parse_user_id(d.pop("userId", UNSET))

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        privacy_url = d.pop("privacyUrl", UNSET)

        terms_url = d.pop("termsUrl", UNSET)

        def _parse_services_provided(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        services_provided = _parse_services_provided(d.pop("servicesProvided", UNSET))

        def _parse_data_stored(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        data_stored = _parse_data_stored(d.pop("dataStored", UNSET))

        location = d.pop("location", UNSET)

        _password_policy = d.pop("passwordPolicy", UNSET)
        password_policy: Union[Unset, VendorRequestPublicDtoPasswordPolicy]
        if isinstance(_password_policy, Unset):
            password_policy = UNSET
        else:
            password_policy = VendorRequestPublicDtoPasswordPolicy(_password_policy)

        def _parse_password_min_length(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        password_min_length = _parse_password_min_length(d.pop("passwordMinLength", UNSET))

        def _parse_contact_at_vendor(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        contact_at_vendor = _parse_contact_at_vendor(d.pop("contactAtVendor", UNSET))

        def _parse_contacts_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        contacts_email = _parse_contacts_email(d.pop("contactsEmail", UNSET))

        notes = d.pop("notes", UNSET)

        def _parse_renewal_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        renewal_date = _parse_renewal_date(d.pop("renewalDate", UNSET))

        _renewal_schedule_type = d.pop("renewalScheduleType", UNSET)
        renewal_schedule_type: Union[Unset, VendorRequestPublicDtoRenewalScheduleType]
        if isinstance(_renewal_schedule_type, Unset):
            renewal_schedule_type = UNSET
        else:
            renewal_schedule_type = VendorRequestPublicDtoRenewalScheduleType(_renewal_schedule_type)

        def _parse_confirmed(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        confirmed = _parse_confirmed(d.pop("confirmed", UNSET))

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, VendorRequestPublicDtoType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = VendorRequestPublicDtoType(_type_)

        account_id = d.pop("accountId", UNSET)

        _operational_impact = d.pop("operationalImpact", UNSET)
        operational_impact: Union[Unset, VendorRequestPublicDtoOperationalImpact]
        if isinstance(_operational_impact, Unset):
            operational_impact = UNSET
        else:
            operational_impact = VendorRequestPublicDtoOperationalImpact(_operational_impact)

        _environment_access = d.pop("environmentAccess", UNSET)
        environment_access: Union[Unset, VendorRequestPublicDtoEnvironmentAccess]
        if isinstance(_environment_access, Unset):
            environment_access = UNSET
        else:
            environment_access = VendorRequestPublicDtoEnvironmentAccess(_environment_access)

        _impact_level = d.pop("impactLevel", UNSET)
        impact_level: Union[Unset, VendorRequestPublicDtoImpactLevel]
        if isinstance(_impact_level, Unset):
            impact_level = UNSET
        else:
            impact_level = VendorRequestPublicDtoImpactLevel(_impact_level)

        def _parse_data_accessed_or_processed_list(
            data: object,
        ) -> Union[None, Unset, list[VendorRequestPublicDtoDataAccessedOrProcessedListType0Item]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_accessed_or_processed_list_type_0 = []
                _data_accessed_or_processed_list_type_0 = data
                for data_accessed_or_processed_list_type_0_item_data in _data_accessed_or_processed_list_type_0:
                    data_accessed_or_processed_list_type_0_item = (
                        VendorRequestPublicDtoDataAccessedOrProcessedListType0Item(
                            data_accessed_or_processed_list_type_0_item_data
                        )
                    )

                    data_accessed_or_processed_list_type_0.append(data_accessed_or_processed_list_type_0_item)

                return data_accessed_or_processed_list_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[VendorRequestPublicDtoDataAccessedOrProcessedListType0Item]], data)

        data_accessed_or_processed_list = _parse_data_accessed_or_processed_list(
            d.pop("dataAccessedOrProcessedList", UNSET)
        )

        integrations = cast(list[float], d.pop("integrations", UNSET))

        def _parse_cost(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cost = _parse_cost(d.pop("cost", UNSET))

        def _parse_exclude_ids(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                exclude_ids_type_0 = cast(list[float], data)

                return exclude_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        exclude_ids = _parse_exclude_ids(d.pop("excludeIds", UNSET))

        vendor_request_public_dto = cls(
            name=name,
            is_sub_processor=is_sub_processor,
            is_sub_processor_active=is_sub_processor_active,
            has_pii=has_pii,
            password_requires_min_length=password_requires_min_length,
            password_requires_number=password_requires_number,
            password_requires_symbol=password_requires_symbol,
            password_mfa_enabled=password_mfa_enabled,
            category=category,
            risk=risk,
            status=status,
            critical=critical,
            user_id=user_id,
            url=url,
            privacy_url=privacy_url,
            terms_url=terms_url,
            services_provided=services_provided,
            data_stored=data_stored,
            location=location,
            password_policy=password_policy,
            password_min_length=password_min_length,
            contact_at_vendor=contact_at_vendor,
            contacts_email=contacts_email,
            notes=notes,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            confirmed=confirmed,
            type_=type_,
            account_id=account_id,
            operational_impact=operational_impact,
            environment_access=environment_access,
            impact_level=impact_level,
            data_accessed_or_processed_list=data_accessed_or_processed_list,
            integrations=integrations,
            cost=cost,
            exclude_ids=exclude_ids,
        )

        vendor_request_public_dto.additional_properties = d
        return vendor_request_public_dto

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
