import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.vendor_response_public_dto_trust_center_provider import VendorResponsePublicDtoTrustCenterProvider
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto
    from ..models.user_response_public_dto import UserResponsePublicDto
    from ..models.vendor_document_response_public_dto import VendorDocumentResponsePublicDto
    from ..models.vendor_integration_response_public_dto import VendorIntegrationResponsePublicDto
    from ..models.vendor_response_public_dto_last_questionnaire_type_0 import (
        VendorResponsePublicDtoLastQuestionnaireType0,
    )
    from ..models.vendor_review_response_public_dto import VendorReviewResponsePublicDto
    from ..models.vendor_security_review_response_public_dto import VendorSecurityReviewResponsePublicDto


T = TypeVar("T", bound="VendorResponsePublicDto")


@_attrs_define
class VendorResponsePublicDto:
    """
    Attributes:
        id (float): Vendor ID Example: 1.
        name (str): The name of a vendor Example: Acme.
        category (Union[None, str]): The business domain of the vendor Example: ENGINEERING.
        risk (str): The vendor risk type Example: MODERATE.
        type_ (Union[None, str]): The vendor sub-type (Vendor, Contractor, Supplier, etc) Example: CONTRACTOR.
        critical (Union[None, bool]): Does the vendor is considered critical or not
        location (Union[None, str]): Vendor location Example: USA.
        url (Union[None, str]): Vendor URL Example: https://acme.com.
        privacy_url (Union[None, str]): Vendor Privacy Policy URL Example: https://acme.com.
        terms_url (Union[None, str]): Vendor Terms of Use URL Example: https://acme.com.
        trust_center_url (Union[None, str]): Vendor Trust Center URL Example: https://trust.drata.com.
        trust_center_provider (VendorResponsePublicDtoTrustCenterProvider): The providing service for this Trust Center
            Example: DRATA.
        services_provided (Union[None, str]): Describe vendor services Example: Perform security scans once a month.
        data_stored (Union[None, str]): What type of data the vendor stores Example: Resulting reports of security
            scans.
        has_pii (bool): Does this vendor store any type of PII Example: True.
        password_policy (Union[None, str]): The vendor password policy Example: USERNAME_PASSWORD.
        password_requires_min_length (bool): Is there a minimum length for user passwords Example: True.
        password_min_length (Union[None, float]): Minimum character length for a password Example: 8.
        password_requires_number (bool): Does a password require numbers Example: True.
        password_requires_symbol (bool): Does a password require non-alpha-numeric characters Example: True.
        password_mfa_enabled (bool): Is multi-factor authentication enabled for this vendor Example: True.
        contact_at_vendor (Union[None, str]): The name of the corresponding account manager for this vendor Example:
            John Doe.
        contacts_email (Union[None, str]): The email of the corresponding account manager for this vendor Example:
            jdoe@company.com.
        notes (Union[None, str]): Additional notes for vendor Example: Meeting once a month to adjust contract.
        logo_url (Union[None, str]): Vendor logo URL Example: https://cdn-prod.imgpilot.com/logo.png.
        created_at (datetime.datetime): Vendor created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Vendor updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        user (Union['UserResponsePublicDto', None]): The user that is responsible for the compliance of this vendor
        documents (list['VendorDocumentResponsePublicDto']): A list of vendor documents
        last_questionnaire (Union['VendorResponsePublicDtoLastQuestionnaireType0', None]): The last questionnaire
            associated with the vendor
        is_sub_processor (bool): Is this vendor a sub-processor?
        is_sub_processor_active (bool): Is this vendor an active Sub-processor?
        archived_at (Union[None, datetime.datetime]): Timestamp when the status of the vendor changed Example:
            2025-07-01T16:45:55.246Z.
        status (Union[None, str]): The vendor status Example: ACTIVE.
        renewal_date (Union[None, str]): Vendor renewal date Example: 2020-07-06.
        renewal_schedule_type (Union[None, str]): Vendor renewal schedule type Example: ONE_YEAR.
        renewal_date_status (Union[None, str]): Vendor renewal status based on the proximity to the renewal due date
            Example: COMPLETED.
        confirmed_at (Union[None, datetime.datetime]): Timestamp when the vendor details were confirmed Example:
            2025-07-01T16:45:55.246Z.
        reviews (list['VendorReviewResponsePublicDto']): Vendor Reviews
        shared_account_id (Union[None, str]): Shared account id Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        is_drata_user (Union[None, bool]): Is the vendor an user of drata
        events (Union[None, float]): The number of event notifications pending for the vendor Example: 4.
        integrations (Union[None, list['VendorIntegrationResponsePublicDto']]): Vendor integrations list
        cost (Union[None, str]): Annual Contract Value for the vendor in Cents unit Example: 1088.
        operational_impact (Union[None, str]): Vendor level of operational impact Example: CRITICAL.
        environment_access (Union[None, str]): Vendor environment access privileges Example: READ_ONLY.
        impact_level (Union[None, str]): Vendor overall impact level Example: INSIGNIFICANT.
        data_accessed_or_processed_list (Union[None, list[str]]): List of data accessed or processed
        risk_count (Union[None, float]): The number of associated risks
        vendor_relationship_contact (Union['UserCardCompactResponsePublicDto', None]): The vendor relationship contact
            Example: {'id': 1, 'email': 'adam@drata.com', 'firstName': 'Adam', 'lastName': 'Attack', 'createdAt':
            '2025-01-08T21:18:10.846Z', 'updatedAt': '2025-01-10T23:46:09.000Z'}.
        latest_security_reviews (Union[None, Unset, list['VendorSecurityReviewResponsePublicDto']]): Latest Security
            Reviews
    """

    id: float
    name: str
    category: Union[None, str]
    risk: str
    type_: Union[None, str]
    critical: Union[None, bool]
    location: Union[None, str]
    url: Union[None, str]
    privacy_url: Union[None, str]
    terms_url: Union[None, str]
    trust_center_url: Union[None, str]
    trust_center_provider: VendorResponsePublicDtoTrustCenterProvider
    services_provided: Union[None, str]
    data_stored: Union[None, str]
    has_pii: bool
    password_policy: Union[None, str]
    password_requires_min_length: bool
    password_min_length: Union[None, float]
    password_requires_number: bool
    password_requires_symbol: bool
    password_mfa_enabled: bool
    contact_at_vendor: Union[None, str]
    contacts_email: Union[None, str]
    notes: Union[None, str]
    logo_url: Union[None, str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user: Union["UserResponsePublicDto", None]
    documents: list["VendorDocumentResponsePublicDto"]
    last_questionnaire: Union["VendorResponsePublicDtoLastQuestionnaireType0", None]
    is_sub_processor: bool
    is_sub_processor_active: bool
    archived_at: Union[None, datetime.datetime]
    status: Union[None, str]
    renewal_date: Union[None, str]
    renewal_schedule_type: Union[None, str]
    renewal_date_status: Union[None, str]
    confirmed_at: Union[None, datetime.datetime]
    reviews: list["VendorReviewResponsePublicDto"]
    shared_account_id: Union[None, str]
    is_drata_user: Union[None, bool]
    events: Union[None, float]
    integrations: Union[None, list["VendorIntegrationResponsePublicDto"]]
    cost: Union[None, str]
    operational_impact: Union[None, str]
    environment_access: Union[None, str]
    impact_level: Union[None, str]
    data_accessed_or_processed_list: Union[None, list[str]]
    risk_count: Union[None, float]
    vendor_relationship_contact: Union["UserCardCompactResponsePublicDto", None]
    latest_security_reviews: Union[None, Unset, list["VendorSecurityReviewResponsePublicDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto
        from ..models.vendor_response_public_dto_last_questionnaire_type_0 import (
            VendorResponsePublicDtoLastQuestionnaireType0,
        )

        id = self.id

        name = self.name

        category: Union[None, str]
        category = self.category

        risk = self.risk

        type_: Union[None, str]
        type_ = self.type_

        critical: Union[None, bool]
        critical = self.critical

        location: Union[None, str]
        location = self.location

        url: Union[None, str]
        url = self.url

        privacy_url: Union[None, str]
        privacy_url = self.privacy_url

        terms_url: Union[None, str]
        terms_url = self.terms_url

        trust_center_url: Union[None, str]
        trust_center_url = self.trust_center_url

        trust_center_provider = self.trust_center_provider.value

        services_provided: Union[None, str]
        services_provided = self.services_provided

        data_stored: Union[None, str]
        data_stored = self.data_stored

        has_pii = self.has_pii

        password_policy: Union[None, str]
        password_policy = self.password_policy

        password_requires_min_length = self.password_requires_min_length

        password_min_length: Union[None, float]
        password_min_length = self.password_min_length

        password_requires_number = self.password_requires_number

        password_requires_symbol = self.password_requires_symbol

        password_mfa_enabled = self.password_mfa_enabled

        contact_at_vendor: Union[None, str]
        contact_at_vendor = self.contact_at_vendor

        contacts_email: Union[None, str]
        contacts_email = self.contacts_email

        notes: Union[None, str]
        notes = self.notes

        logo_url: Union[None, str]
        logo_url = self.logo_url

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        user: Union[None, dict[str, Any]]
        if isinstance(self.user, UserResponsePublicDto):
            user = self.user.to_dict()
        else:
            user = self.user

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        last_questionnaire: Union[None, dict[str, Any]]
        if isinstance(self.last_questionnaire, VendorResponsePublicDtoLastQuestionnaireType0):
            last_questionnaire = self.last_questionnaire.to_dict()
        else:
            last_questionnaire = self.last_questionnaire

        is_sub_processor = self.is_sub_processor

        is_sub_processor_active = self.is_sub_processor_active

        archived_at: Union[None, str]
        if isinstance(self.archived_at, datetime.datetime):
            archived_at = self.archived_at.isoformat()
        else:
            archived_at = self.archived_at

        status: Union[None, str]
        status = self.status

        renewal_date: Union[None, str]
        renewal_date = self.renewal_date

        renewal_schedule_type: Union[None, str]
        renewal_schedule_type = self.renewal_schedule_type

        renewal_date_status: Union[None, str]
        renewal_date_status = self.renewal_date_status

        confirmed_at: Union[None, str]
        if isinstance(self.confirmed_at, datetime.datetime):
            confirmed_at = self.confirmed_at.isoformat()
        else:
            confirmed_at = self.confirmed_at

        reviews = []
        for reviews_item_data in self.reviews:
            reviews_item = reviews_item_data.to_dict()
            reviews.append(reviews_item)

        shared_account_id: Union[None, str]
        shared_account_id = self.shared_account_id

        is_drata_user: Union[None, bool]
        is_drata_user = self.is_drata_user

        events: Union[None, float]
        events = self.events

        integrations: Union[None, list[dict[str, Any]]]
        if isinstance(self.integrations, list):
            integrations = []
            for integrations_type_0_item_data in self.integrations:
                integrations_type_0_item = integrations_type_0_item_data.to_dict()
                integrations.append(integrations_type_0_item)

        else:
            integrations = self.integrations

        cost: Union[None, str]
        cost = self.cost

        operational_impact: Union[None, str]
        operational_impact = self.operational_impact

        environment_access: Union[None, str]
        environment_access = self.environment_access

        impact_level: Union[None, str]
        impact_level = self.impact_level

        data_accessed_or_processed_list: Union[None, list[str]]
        if isinstance(self.data_accessed_or_processed_list, list):
            data_accessed_or_processed_list = self.data_accessed_or_processed_list

        else:
            data_accessed_or_processed_list = self.data_accessed_or_processed_list

        risk_count: Union[None, float]
        risk_count = self.risk_count

        vendor_relationship_contact: Union[None, dict[str, Any]]
        if isinstance(self.vendor_relationship_contact, UserCardCompactResponsePublicDto):
            vendor_relationship_contact = self.vendor_relationship_contact.to_dict()
        else:
            vendor_relationship_contact = self.vendor_relationship_contact

        latest_security_reviews: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.latest_security_reviews, Unset):
            latest_security_reviews = UNSET
        elif isinstance(self.latest_security_reviews, list):
            latest_security_reviews = []
            for latest_security_reviews_type_0_item_data in self.latest_security_reviews:
                latest_security_reviews_type_0_item = latest_security_reviews_type_0_item_data.to_dict()
                latest_security_reviews.append(latest_security_reviews_type_0_item)

        else:
            latest_security_reviews = self.latest_security_reviews

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "category": category,
                "risk": risk,
                "type": type_,
                "critical": critical,
                "location": location,
                "url": url,
                "privacyUrl": privacy_url,
                "termsUrl": terms_url,
                "trustCenterUrl": trust_center_url,
                "trustCenterProvider": trust_center_provider,
                "servicesProvided": services_provided,
                "dataStored": data_stored,
                "hasPii": has_pii,
                "passwordPolicy": password_policy,
                "passwordRequiresMinLength": password_requires_min_length,
                "passwordMinLength": password_min_length,
                "passwordRequiresNumber": password_requires_number,
                "passwordRequiresSymbol": password_requires_symbol,
                "passwordMfaEnabled": password_mfa_enabled,
                "contactAtVendor": contact_at_vendor,
                "contactsEmail": contacts_email,
                "notes": notes,
                "logoUrl": logo_url,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "user": user,
                "documents": documents,
                "lastQuestionnaire": last_questionnaire,
                "isSubProcessor": is_sub_processor,
                "isSubProcessorActive": is_sub_processor_active,
                "archivedAt": archived_at,
                "status": status,
                "renewalDate": renewal_date,
                "renewalScheduleType": renewal_schedule_type,
                "renewalDateStatus": renewal_date_status,
                "confirmedAt": confirmed_at,
                "reviews": reviews,
                "sharedAccountId": shared_account_id,
                "isDrataUser": is_drata_user,
                "events": events,
                "integrations": integrations,
                "cost": cost,
                "operationalImpact": operational_impact,
                "environmentAccess": environment_access,
                "impactLevel": impact_level,
                "dataAccessedOrProcessedList": data_accessed_or_processed_list,
                "riskCount": risk_count,
                "vendorRelationshipContact": vendor_relationship_contact,
            }
        )
        if latest_security_reviews is not UNSET:
            field_dict["latestSecurityReviews"] = latest_security_reviews

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_card_compact_response_public_dto import UserCardCompactResponsePublicDto
        from ..models.user_response_public_dto import UserResponsePublicDto
        from ..models.vendor_document_response_public_dto import VendorDocumentResponsePublicDto
        from ..models.vendor_integration_response_public_dto import VendorIntegrationResponsePublicDto
        from ..models.vendor_response_public_dto_last_questionnaire_type_0 import (
            VendorResponsePublicDtoLastQuestionnaireType0,
        )
        from ..models.vendor_review_response_public_dto import VendorReviewResponsePublicDto
        from ..models.vendor_security_review_response_public_dto import VendorSecurityReviewResponsePublicDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_category(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        category = _parse_category(d.pop("category"))

        risk = d.pop("risk")

        def _parse_type_(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        type_ = _parse_type_(d.pop("type"))

        def _parse_critical(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        critical = _parse_critical(d.pop("critical"))

        def _parse_location(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        location = _parse_location(d.pop("location"))

        def _parse_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        url = _parse_url(d.pop("url"))

        def _parse_privacy_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        privacy_url = _parse_privacy_url(d.pop("privacyUrl"))

        def _parse_terms_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        terms_url = _parse_terms_url(d.pop("termsUrl"))

        def _parse_trust_center_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        trust_center_url = _parse_trust_center_url(d.pop("trustCenterUrl"))

        trust_center_provider = VendorResponsePublicDtoTrustCenterProvider(d.pop("trustCenterProvider"))

        def _parse_services_provided(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        services_provided = _parse_services_provided(d.pop("servicesProvided"))

        def _parse_data_stored(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        data_stored = _parse_data_stored(d.pop("dataStored"))

        has_pii = d.pop("hasPii")

        def _parse_password_policy(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        password_policy = _parse_password_policy(d.pop("passwordPolicy"))

        password_requires_min_length = d.pop("passwordRequiresMinLength")

        def _parse_password_min_length(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        password_min_length = _parse_password_min_length(d.pop("passwordMinLength"))

        password_requires_number = d.pop("passwordRequiresNumber")

        password_requires_symbol = d.pop("passwordRequiresSymbol")

        password_mfa_enabled = d.pop("passwordMfaEnabled")

        def _parse_contact_at_vendor(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        contact_at_vendor = _parse_contact_at_vendor(d.pop("contactAtVendor"))

        def _parse_contacts_email(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        contacts_email = _parse_contacts_email(d.pop("contactsEmail"))

        def _parse_notes(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        notes = _parse_notes(d.pop("notes"))

        def _parse_logo_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        logo_url = _parse_logo_url(d.pop("logoUrl"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

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

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = VendorDocumentResponsePublicDto.from_dict(documents_item_data)

            documents.append(documents_item)

        def _parse_last_questionnaire(data: object) -> Union["VendorResponsePublicDtoLastQuestionnaireType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_questionnaire_type_0 = VendorResponsePublicDtoLastQuestionnaireType0.from_dict(data)

                return last_questionnaire_type_0
            except:  # noqa: E722
                pass
            return cast(Union["VendorResponsePublicDtoLastQuestionnaireType0", None], data)

        last_questionnaire = _parse_last_questionnaire(d.pop("lastQuestionnaire"))

        is_sub_processor = d.pop("isSubProcessor")

        is_sub_processor_active = d.pop("isSubProcessorActive")

        def _parse_archived_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                archived_at_type_0 = isoparse(data)

                return archived_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        archived_at = _parse_archived_at(d.pop("archivedAt"))

        def _parse_status(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        status = _parse_status(d.pop("status"))

        def _parse_renewal_date(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        renewal_date = _parse_renewal_date(d.pop("renewalDate"))

        def _parse_renewal_schedule_type(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        renewal_schedule_type = _parse_renewal_schedule_type(d.pop("renewalScheduleType"))

        def _parse_renewal_date_status(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        renewal_date_status = _parse_renewal_date_status(d.pop("renewalDateStatus"))

        def _parse_confirmed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                confirmed_at_type_0 = isoparse(data)

                return confirmed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        confirmed_at = _parse_confirmed_at(d.pop("confirmedAt"))

        reviews = []
        _reviews = d.pop("reviews")
        for reviews_item_data in _reviews:
            reviews_item = VendorReviewResponsePublicDto.from_dict(reviews_item_data)

            reviews.append(reviews_item)

        def _parse_shared_account_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        shared_account_id = _parse_shared_account_id(d.pop("sharedAccountId"))

        def _parse_is_drata_user(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        is_drata_user = _parse_is_drata_user(d.pop("isDrataUser"))

        def _parse_events(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        events = _parse_events(d.pop("events"))

        def _parse_integrations(data: object) -> Union[None, list["VendorIntegrationResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                integrations_type_0 = []
                _integrations_type_0 = data
                for integrations_type_0_item_data in _integrations_type_0:
                    integrations_type_0_item = VendorIntegrationResponsePublicDto.from_dict(
                        integrations_type_0_item_data
                    )

                    integrations_type_0.append(integrations_type_0_item)

                return integrations_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorIntegrationResponsePublicDto"]], data)

        integrations = _parse_integrations(d.pop("integrations"))

        def _parse_cost(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        cost = _parse_cost(d.pop("cost"))

        def _parse_operational_impact(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        operational_impact = _parse_operational_impact(d.pop("operationalImpact"))

        def _parse_environment_access(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        environment_access = _parse_environment_access(d.pop("environmentAccess"))

        def _parse_impact_level(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        impact_level = _parse_impact_level(d.pop("impactLevel"))

        def _parse_data_accessed_or_processed_list(data: object) -> Union[None, list[str]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_accessed_or_processed_list_type_0 = cast(list[str], data)

                return data_accessed_or_processed_list_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[str]], data)

        data_accessed_or_processed_list = _parse_data_accessed_or_processed_list(d.pop("dataAccessedOrProcessedList"))

        def _parse_risk_count(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        risk_count = _parse_risk_count(d.pop("riskCount"))

        def _parse_vendor_relationship_contact(data: object) -> Union["UserCardCompactResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                vendor_relationship_contact_type_1 = UserCardCompactResponsePublicDto.from_dict(data)

                return vendor_relationship_contact_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserCardCompactResponsePublicDto", None], data)

        vendor_relationship_contact = _parse_vendor_relationship_contact(d.pop("vendorRelationshipContact"))

        def _parse_latest_security_reviews(
            data: object,
        ) -> Union[None, Unset, list["VendorSecurityReviewResponsePublicDto"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                latest_security_reviews_type_0 = []
                _latest_security_reviews_type_0 = data
                for latest_security_reviews_type_0_item_data in _latest_security_reviews_type_0:
                    latest_security_reviews_type_0_item = VendorSecurityReviewResponsePublicDto.from_dict(
                        latest_security_reviews_type_0_item_data
                    )

                    latest_security_reviews_type_0.append(latest_security_reviews_type_0_item)

                return latest_security_reviews_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["VendorSecurityReviewResponsePublicDto"]], data)

        latest_security_reviews = _parse_latest_security_reviews(d.pop("latestSecurityReviews", UNSET))

        vendor_response_public_dto = cls(
            id=id,
            name=name,
            category=category,
            risk=risk,
            type_=type_,
            critical=critical,
            location=location,
            url=url,
            privacy_url=privacy_url,
            terms_url=terms_url,
            trust_center_url=trust_center_url,
            trust_center_provider=trust_center_provider,
            services_provided=services_provided,
            data_stored=data_stored,
            has_pii=has_pii,
            password_policy=password_policy,
            password_requires_min_length=password_requires_min_length,
            password_min_length=password_min_length,
            password_requires_number=password_requires_number,
            password_requires_symbol=password_requires_symbol,
            password_mfa_enabled=password_mfa_enabled,
            contact_at_vendor=contact_at_vendor,
            contacts_email=contacts_email,
            notes=notes,
            logo_url=logo_url,
            created_at=created_at,
            updated_at=updated_at,
            user=user,
            documents=documents,
            last_questionnaire=last_questionnaire,
            is_sub_processor=is_sub_processor,
            is_sub_processor_active=is_sub_processor_active,
            archived_at=archived_at,
            status=status,
            renewal_date=renewal_date,
            renewal_schedule_type=renewal_schedule_type,
            renewal_date_status=renewal_date_status,
            confirmed_at=confirmed_at,
            reviews=reviews,
            shared_account_id=shared_account_id,
            is_drata_user=is_drata_user,
            events=events,
            integrations=integrations,
            cost=cost,
            operational_impact=operational_impact,
            environment_access=environment_access,
            impact_level=impact_level,
            data_accessed_or_processed_list=data_accessed_or_processed_list,
            risk_count=risk_count,
            vendor_relationship_contact=vendor_relationship_contact,
            latest_security_reviews=latest_security_reviews,
        )

        vendor_response_public_dto.additional_properties = d
        return vendor_response_public_dto

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
