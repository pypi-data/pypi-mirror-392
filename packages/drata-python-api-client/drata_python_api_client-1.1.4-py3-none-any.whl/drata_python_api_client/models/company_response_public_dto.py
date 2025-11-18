import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.company_response_public_dto_entitlements_item import CompanyResponsePublicDtoEntitlementsItem
    from ..models.connection_response_public_dto import ConnectionResponsePublicDto
    from ..models.drata_support_access_response_public_dto import DrataSupportAccessResponsePublicDto
    from ..models.framework_response_public_dto import FrameworkResponsePublicDto
    from ..models.security_report_response_public_dto import SecurityReportResponsePublicDto
    from ..models.workspace_response_public_dto import WorkspaceResponsePublicDto


T = TypeVar("T", bound="CompanyResponsePublicDto")


@_attrs_define
class CompanyResponsePublicDto:
    """
    Attributes:
        account_id (str): The account ID for the company Example: aaaaaaaa-bbbb-0000-cccc-dddddddddddd.
        domain (str): Company's domain Example: drata.com.
        name (str): Company's common name Example: Drata.
        legal_name (str): Company's full legal name Example: Drata Inc..
        year (float): Year the company was founded Example: 2014.
        description (str): The description of the company Example: We make tools.
        phone_number (str): Company's phone number Example: 800-555-5555.
        address (str): The address of the company Example: 742 Evergreen Terrace, Springfield, OH 45501.
        privacy_url (str): Company's privacy URL Example: https://drata.com/privacy.
        terms_url (str): Company's terms of use URL Example: https://drata.com/terms.
        support_url (str): Company's support/help URL Example: https://help.drata.com.
        jobs_url (str): The URL where your open jobs are publicly posted online Example: https://jobs.drata.com.
        security_email (str): Company's security/compliance email Example: security@drata.com.
        logo_url (str): User avatar URL Example: https://cdn-prod.imgpilot.com/logo.png.
        security_training (Union[None, str]): Security Awareness Training option Example: DRATA_PROVIDED.
        hipaa_training (Union[None, str]): HIPAA Training option Example: DRATA_PROVIDED.
        background_check (Union[None, str]): The type of background check option Example: CERTN.
        security_report (SecurityReportResponsePublicDto):
        workspaces (list['WorkspaceResponsePublicDto']): Company workspaces Example: [].
        admin_onboarded_at (Union[None, datetime.datetime]): Company completed onboarded date timestamp Example:
            2025-07-01T16:45:55.246Z.
        renewal_period_start_date (Union[None, datetime.datetime]): Company entered annual renewal time date timestamp
            Example: 2025-07-01T16:45:55.246Z.
        connections (list['ConnectionResponsePublicDto']):
        created_at (datetime.datetime): Account created date timestamp Example: 2025-07-01T16:45:55.246Z.
        updated_at (datetime.datetime): Account updated date timestamp Example: 2025-07-01T16:45:55.246Z.
        frameworks (list['FrameworkResponsePublicDto']): Enabled frameworks for this account Example:
            FrameworkResponsePublicDto[].
        agent_enabled (bool): The agent status (ON/OFF)
        manual_upload_enabled (bool): Manual evidence upload status (ON/OFF)
        drata_support_access (Union['DrataSupportAccessResponsePublicDto', None]): Data to determine if Drata Support
            has access to the account
        entitlements (list['CompanyResponsePublicDtoEntitlementsItem']): The tenants admin accounts Example: [{'name':
            'Trust Center', 'description': 'The Trust Center Pages feature', 'type': 'TRUST_CENTER'}].
        language (str): Account language Example: ENGLISH_US.
        security_training_link (Union[Unset, str]): Link to custom security training Example: https://security-training-
            service.com.
        hipaa_training_link (Union[Unset, str]): Link to custom HIPAA Training Example: https://hipaa-training-
            service.com.
    """

    account_id: str
    domain: str
    name: str
    legal_name: str
    year: float
    description: str
    phone_number: str
    address: str
    privacy_url: str
    terms_url: str
    support_url: str
    jobs_url: str
    security_email: str
    logo_url: str
    security_training: Union[None, str]
    hipaa_training: Union[None, str]
    background_check: Union[None, str]
    security_report: "SecurityReportResponsePublicDto"
    workspaces: list["WorkspaceResponsePublicDto"]
    admin_onboarded_at: Union[None, datetime.datetime]
    renewal_period_start_date: Union[None, datetime.datetime]
    connections: list["ConnectionResponsePublicDto"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    frameworks: list["FrameworkResponsePublicDto"]
    agent_enabled: bool
    manual_upload_enabled: bool
    drata_support_access: Union["DrataSupportAccessResponsePublicDto", None]
    entitlements: list["CompanyResponsePublicDtoEntitlementsItem"]
    language: str
    security_training_link: Union[Unset, str] = UNSET
    hipaa_training_link: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.drata_support_access_response_public_dto import DrataSupportAccessResponsePublicDto

        account_id = self.account_id

        domain = self.domain

        name = self.name

        legal_name = self.legal_name

        year = self.year

        description = self.description

        phone_number = self.phone_number

        address = self.address

        privacy_url = self.privacy_url

        terms_url = self.terms_url

        support_url = self.support_url

        jobs_url = self.jobs_url

        security_email = self.security_email

        logo_url = self.logo_url

        security_training: Union[None, str]
        security_training = self.security_training

        hipaa_training: Union[None, str]
        hipaa_training = self.hipaa_training

        background_check: Union[None, str]
        background_check = self.background_check

        security_report = self.security_report.to_dict()

        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        admin_onboarded_at: Union[None, str]
        if isinstance(self.admin_onboarded_at, datetime.datetime):
            admin_onboarded_at = self.admin_onboarded_at.isoformat()
        else:
            admin_onboarded_at = self.admin_onboarded_at

        renewal_period_start_date: Union[None, str]
        if isinstance(self.renewal_period_start_date, datetime.datetime):
            renewal_period_start_date = self.renewal_period_start_date.isoformat()
        else:
            renewal_period_start_date = self.renewal_period_start_date

        connections = []
        for connections_item_data in self.connections:
            connections_item = connections_item_data.to_dict()
            connections.append(connections_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        frameworks = []
        for frameworks_item_data in self.frameworks:
            frameworks_item = frameworks_item_data.to_dict()
            frameworks.append(frameworks_item)

        agent_enabled = self.agent_enabled

        manual_upload_enabled = self.manual_upload_enabled

        drata_support_access: Union[None, dict[str, Any]]
        if isinstance(self.drata_support_access, DrataSupportAccessResponsePublicDto):
            drata_support_access = self.drata_support_access.to_dict()
        else:
            drata_support_access = self.drata_support_access

        entitlements = []
        for entitlements_item_data in self.entitlements:
            entitlements_item = entitlements_item_data.to_dict()
            entitlements.append(entitlements_item)

        language = self.language

        security_training_link = self.security_training_link

        hipaa_training_link = self.hipaa_training_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accountId": account_id,
                "domain": domain,
                "name": name,
                "legalName": legal_name,
                "year": year,
                "description": description,
                "phoneNumber": phone_number,
                "address": address,
                "privacyUrl": privacy_url,
                "termsUrl": terms_url,
                "supportUrl": support_url,
                "jobsUrl": jobs_url,
                "securityEmail": security_email,
                "logoUrl": logo_url,
                "securityTraining": security_training,
                "hipaaTraining": hipaa_training,
                "backgroundCheck": background_check,
                "securityReport": security_report,
                "workspaces": workspaces,
                "adminOnboardedAt": admin_onboarded_at,
                "renewalPeriodStartDate": renewal_period_start_date,
                "connections": connections,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "frameworks": frameworks,
                "agentEnabled": agent_enabled,
                "manualUploadEnabled": manual_upload_enabled,
                "drataSupportAccess": drata_support_access,
                "entitlements": entitlements,
                "language": language,
            }
        )
        if security_training_link is not UNSET:
            field_dict["securityTrainingLink"] = security_training_link
        if hipaa_training_link is not UNSET:
            field_dict["hipaaTrainingLink"] = hipaa_training_link

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.company_response_public_dto_entitlements_item import CompanyResponsePublicDtoEntitlementsItem
        from ..models.connection_response_public_dto import ConnectionResponsePublicDto
        from ..models.drata_support_access_response_public_dto import DrataSupportAccessResponsePublicDto
        from ..models.framework_response_public_dto import FrameworkResponsePublicDto
        from ..models.security_report_response_public_dto import SecurityReportResponsePublicDto
        from ..models.workspace_response_public_dto import WorkspaceResponsePublicDto

        d = dict(src_dict)
        account_id = d.pop("accountId")

        domain = d.pop("domain")

        name = d.pop("name")

        legal_name = d.pop("legalName")

        year = d.pop("year")

        description = d.pop("description")

        phone_number = d.pop("phoneNumber")

        address = d.pop("address")

        privacy_url = d.pop("privacyUrl")

        terms_url = d.pop("termsUrl")

        support_url = d.pop("supportUrl")

        jobs_url = d.pop("jobsUrl")

        security_email = d.pop("securityEmail")

        logo_url = d.pop("logoUrl")

        def _parse_security_training(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        security_training = _parse_security_training(d.pop("securityTraining"))

        def _parse_hipaa_training(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        hipaa_training = _parse_hipaa_training(d.pop("hipaaTraining"))

        def _parse_background_check(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        background_check = _parse_background_check(d.pop("backgroundCheck"))

        security_report = SecurityReportResponsePublicDto.from_dict(d.pop("securityReport"))

        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = WorkspaceResponsePublicDto.from_dict(workspaces_item_data)

            workspaces.append(workspaces_item)

        def _parse_admin_onboarded_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                admin_onboarded_at_type_0 = isoparse(data)

                return admin_onboarded_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        admin_onboarded_at = _parse_admin_onboarded_at(d.pop("adminOnboardedAt"))

        def _parse_renewal_period_start_date(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                renewal_period_start_date_type_0 = isoparse(data)

                return renewal_period_start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        renewal_period_start_date = _parse_renewal_period_start_date(d.pop("renewalPeriodStartDate"))

        connections = []
        _connections = d.pop("connections")
        for connections_item_data in _connections:
            connections_item = ConnectionResponsePublicDto.from_dict(connections_item_data)

            connections.append(connections_item)

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        frameworks = []
        _frameworks = d.pop("frameworks")
        for frameworks_item_data in _frameworks:
            frameworks_item = FrameworkResponsePublicDto.from_dict(frameworks_item_data)

            frameworks.append(frameworks_item)

        agent_enabled = d.pop("agentEnabled")

        manual_upload_enabled = d.pop("manualUploadEnabled")

        def _parse_drata_support_access(data: object) -> Union["DrataSupportAccessResponsePublicDto", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                drata_support_access_type_1 = DrataSupportAccessResponsePublicDto.from_dict(data)

                return drata_support_access_type_1
            except:  # noqa: E722
                pass
            return cast(Union["DrataSupportAccessResponsePublicDto", None], data)

        drata_support_access = _parse_drata_support_access(d.pop("drataSupportAccess"))

        entitlements = []
        _entitlements = d.pop("entitlements")
        for entitlements_item_data in _entitlements:
            entitlements_item = CompanyResponsePublicDtoEntitlementsItem.from_dict(entitlements_item_data)

            entitlements.append(entitlements_item)

        language = d.pop("language")

        security_training_link = d.pop("securityTrainingLink", UNSET)

        hipaa_training_link = d.pop("hipaaTrainingLink", UNSET)

        company_response_public_dto = cls(
            account_id=account_id,
            domain=domain,
            name=name,
            legal_name=legal_name,
            year=year,
            description=description,
            phone_number=phone_number,
            address=address,
            privacy_url=privacy_url,
            terms_url=terms_url,
            support_url=support_url,
            jobs_url=jobs_url,
            security_email=security_email,
            logo_url=logo_url,
            security_training=security_training,
            hipaa_training=hipaa_training,
            background_check=background_check,
            security_report=security_report,
            workspaces=workspaces,
            admin_onboarded_at=admin_onboarded_at,
            renewal_period_start_date=renewal_period_start_date,
            connections=connections,
            created_at=created_at,
            updated_at=updated_at,
            frameworks=frameworks,
            agent_enabled=agent_enabled,
            manual_upload_enabled=manual_upload_enabled,
            drata_support_access=drata_support_access,
            entitlements=entitlements,
            language=language,
            security_training_link=security_training_link,
            hipaa_training_link=hipaa_training_link,
        )

        company_response_public_dto.additional_properties = d
        return company_response_public_dto

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
