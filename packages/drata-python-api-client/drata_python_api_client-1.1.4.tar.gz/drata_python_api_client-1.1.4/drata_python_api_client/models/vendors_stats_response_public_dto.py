from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vendor_business_unit_stats_response_public_dto import VendorBusinessUnitStatsResponsePublicDto
    from ..models.vendor_has_pii_stats_response_public_dto import VendorHasPiiStatsResponsePublicDto
    from ..models.vendor_impact_level_stats_response_public_dto import VendorImpactLevelStatsResponsePublicDto
    from ..models.vendor_is_critical_stats_response_public_dto import VendorIsCriticalStatsResponsePublicDto
    from ..models.vendor_is_sub_processor_stats_response_public_dto import VendorIsSubProcessorStatsResponsePublicDto
    from ..models.vendor_password_policy_response_public_dto import VendorPasswordPolicyResponsePublicDto
    from ..models.vendor_reminder_stats_response_public_dto import VendorReminderStatsResponsePublicDto
    from ..models.vendor_status_stats_response_public_dto import VendorStatusStatsResponsePublicDto
    from ..models.vendor_type_stats_response_public_dto import VendorTypeStatsResponsePublicDto
    from ..models.vendors_risk_stats_response_public_dto import VendorsRiskStatsResponsePublicDto


T = TypeVar("T", bound="VendorsStatsResponsePublicDto")


@_attrs_define
class VendorsStatsResponsePublicDto:
    """
    Attributes:
        reminder (Union[None, list['VendorReminderStatsResponsePublicDto']]): A list with the stats of reminders for
            Active Vendors Example: [{'key': 'RENEWAL_DUE', 'amount': 1}, {'key': 'RENEWAL_DUE_SOON', 'amount': 1}].
        has_pii (Union[None, list['VendorHasPiiStatsResponsePublicDto']]): A list with the count of Active Vendors
            grouped by has PII value Example: [{'key': 'true', 'amount': 1}, {'key': 'false', 'amount': 1}].
        business_units (Union[None, list['VendorBusinessUnitStatsResponsePublicDto']]): A list with the count of Active
            Vendors grouped by Business Unit Example: [{'key': 'ENGINEERING', 'amount': 118}, {'key': 'PRODUCT', 'amount':
            2}].
        password_policy (Union[None, list['VendorPasswordPolicyResponsePublicDto']]): A list with the count of Active
            Vendors grouped by password policy Example: [{'key': 'USERNAME_PASSWORD', 'amount': 118}, {'key': 'SSO',
            'amount': 2}, {'key': 'NONE', 'amount': 2}, {'key': 'LDAP', 'amount': 2}].
        status (Union[None, list['VendorStatusStatsResponsePublicDto']]): A list with the stats of vendors status
            Example: [{'key': 'ACTIVE', 'amount': 118}, {'key': 'UNDER_REVIEW', 'amount': 1}].
        is_critical (Union[None, list['VendorIsCriticalStatsResponsePublicDto']]): A list with the stats of vendors is
            critical Example: [{'key': 'Yes', 'amount': 10}, {'key': 'No', 'amount': 20}].
        is_sub_processor (Union[None, list['VendorIsSubProcessorStatsResponsePublicDto']]): A list with the count of
            Active Vendors grouped by is sub-processor value Example: [{'key': 'true', 'amount': 10}, {'key': 'false',
            'amount': 20}].
        type_ (Union[None, list['VendorTypeStatsResponsePublicDto']]): A list with the count of Active Vendors grouped
            by type Example: [{'key': 'CONTRACTOR', 'amount': 1}, {'key': 'NONE', 'amount': 2}, {'key': 'OTHER', 'amount':
            3}, {'key': 'PARTNER', 'amount': 4}, {'key': 'SUPPLIER', 'amount': 4}, {'key': 'VENDOR', 'amount': 5}].
        risk (Union[None, list['VendorsRiskStatsResponsePublicDto']]): A list with the stats of vendors risk Example:
            [{'key': 'HIGH', 'amount': 118}, {'key': 'MODERATE', 'amount': 2}, {'key': 'LOW', 'amount': 2}, {'key': 'NONE',
            'amount': 2}].
        impact_level (Union[None, list['VendorImpactLevelStatsResponsePublicDto']]): A list with the stats of vendors
            impact level Example: [{'key': 'CRITICAL', 'amount': 7}, {'key': 'MAJOR', 'amount': 12}, {'key': 'MODERATE',
            'amount': 1}, {'key': 'MINOR', 'amount': 5}, {'key': 'INSIGNIFICANT', 'amount': 21}, {'key': 'UNSCORED',
            'amount': 0}].
    """

    reminder: Union[None, list["VendorReminderStatsResponsePublicDto"]]
    has_pii: Union[None, list["VendorHasPiiStatsResponsePublicDto"]]
    business_units: Union[None, list["VendorBusinessUnitStatsResponsePublicDto"]]
    password_policy: Union[None, list["VendorPasswordPolicyResponsePublicDto"]]
    status: Union[None, list["VendorStatusStatsResponsePublicDto"]]
    is_critical: Union[None, list["VendorIsCriticalStatsResponsePublicDto"]]
    is_sub_processor: Union[None, list["VendorIsSubProcessorStatsResponsePublicDto"]]
    type_: Union[None, list["VendorTypeStatsResponsePublicDto"]]
    risk: Union[None, list["VendorsRiskStatsResponsePublicDto"]]
    impact_level: Union[None, list["VendorImpactLevelStatsResponsePublicDto"]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reminder: Union[None, list[dict[str, Any]]]
        if isinstance(self.reminder, list):
            reminder = []
            for reminder_type_0_item_data in self.reminder:
                reminder_type_0_item = reminder_type_0_item_data.to_dict()
                reminder.append(reminder_type_0_item)

        else:
            reminder = self.reminder

        has_pii: Union[None, list[dict[str, Any]]]
        if isinstance(self.has_pii, list):
            has_pii = []
            for has_pii_type_0_item_data in self.has_pii:
                has_pii_type_0_item = has_pii_type_0_item_data.to_dict()
                has_pii.append(has_pii_type_0_item)

        else:
            has_pii = self.has_pii

        business_units: Union[None, list[dict[str, Any]]]
        if isinstance(self.business_units, list):
            business_units = []
            for business_units_type_0_item_data in self.business_units:
                business_units_type_0_item = business_units_type_0_item_data.to_dict()
                business_units.append(business_units_type_0_item)

        else:
            business_units = self.business_units

        password_policy: Union[None, list[dict[str, Any]]]
        if isinstance(self.password_policy, list):
            password_policy = []
            for password_policy_type_0_item_data in self.password_policy:
                password_policy_type_0_item = password_policy_type_0_item_data.to_dict()
                password_policy.append(password_policy_type_0_item)

        else:
            password_policy = self.password_policy

        status: Union[None, list[dict[str, Any]]]
        if isinstance(self.status, list):
            status = []
            for status_type_0_item_data in self.status:
                status_type_0_item = status_type_0_item_data.to_dict()
                status.append(status_type_0_item)

        else:
            status = self.status

        is_critical: Union[None, list[dict[str, Any]]]
        if isinstance(self.is_critical, list):
            is_critical = []
            for is_critical_type_0_item_data in self.is_critical:
                is_critical_type_0_item = is_critical_type_0_item_data.to_dict()
                is_critical.append(is_critical_type_0_item)

        else:
            is_critical = self.is_critical

        is_sub_processor: Union[None, list[dict[str, Any]]]
        if isinstance(self.is_sub_processor, list):
            is_sub_processor = []
            for is_sub_processor_type_0_item_data in self.is_sub_processor:
                is_sub_processor_type_0_item = is_sub_processor_type_0_item_data.to_dict()
                is_sub_processor.append(is_sub_processor_type_0_item)

        else:
            is_sub_processor = self.is_sub_processor

        type_: Union[None, list[dict[str, Any]]]
        if isinstance(self.type_, list):
            type_ = []
            for type_type_0_item_data in self.type_:
                type_type_0_item = type_type_0_item_data.to_dict()
                type_.append(type_type_0_item)

        else:
            type_ = self.type_

        risk: Union[None, list[dict[str, Any]]]
        if isinstance(self.risk, list):
            risk = []
            for risk_type_0_item_data in self.risk:
                risk_type_0_item = risk_type_0_item_data.to_dict()
                risk.append(risk_type_0_item)

        else:
            risk = self.risk

        impact_level: Union[None, list[dict[str, Any]]]
        if isinstance(self.impact_level, list):
            impact_level = []
            for impact_level_type_0_item_data in self.impact_level:
                impact_level_type_0_item = impact_level_type_0_item_data.to_dict()
                impact_level.append(impact_level_type_0_item)

        else:
            impact_level = self.impact_level

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reminder": reminder,
                "hasPii": has_pii,
                "businessUnits": business_units,
                "passwordPolicy": password_policy,
                "status": status,
                "isCritical": is_critical,
                "isSubProcessor": is_sub_processor,
                "type": type_,
                "risk": risk,
                "impactLevel": impact_level,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vendor_business_unit_stats_response_public_dto import VendorBusinessUnitStatsResponsePublicDto
        from ..models.vendor_has_pii_stats_response_public_dto import VendorHasPiiStatsResponsePublicDto
        from ..models.vendor_impact_level_stats_response_public_dto import VendorImpactLevelStatsResponsePublicDto
        from ..models.vendor_is_critical_stats_response_public_dto import VendorIsCriticalStatsResponsePublicDto
        from ..models.vendor_is_sub_processor_stats_response_public_dto import (
            VendorIsSubProcessorStatsResponsePublicDto,
        )
        from ..models.vendor_password_policy_response_public_dto import VendorPasswordPolicyResponsePublicDto
        from ..models.vendor_reminder_stats_response_public_dto import VendorReminderStatsResponsePublicDto
        from ..models.vendor_status_stats_response_public_dto import VendorStatusStatsResponsePublicDto
        from ..models.vendor_type_stats_response_public_dto import VendorTypeStatsResponsePublicDto
        from ..models.vendors_risk_stats_response_public_dto import VendorsRiskStatsResponsePublicDto

        d = dict(src_dict)

        def _parse_reminder(data: object) -> Union[None, list["VendorReminderStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                reminder_type_0 = []
                _reminder_type_0 = data
                for reminder_type_0_item_data in _reminder_type_0:
                    reminder_type_0_item = VendorReminderStatsResponsePublicDto.from_dict(reminder_type_0_item_data)

                    reminder_type_0.append(reminder_type_0_item)

                return reminder_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorReminderStatsResponsePublicDto"]], data)

        reminder = _parse_reminder(d.pop("reminder"))

        def _parse_has_pii(data: object) -> Union[None, list["VendorHasPiiStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                has_pii_type_0 = []
                _has_pii_type_0 = data
                for has_pii_type_0_item_data in _has_pii_type_0:
                    has_pii_type_0_item = VendorHasPiiStatsResponsePublicDto.from_dict(has_pii_type_0_item_data)

                    has_pii_type_0.append(has_pii_type_0_item)

                return has_pii_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorHasPiiStatsResponsePublicDto"]], data)

        has_pii = _parse_has_pii(d.pop("hasPii"))

        def _parse_business_units(data: object) -> Union[None, list["VendorBusinessUnitStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                business_units_type_0 = []
                _business_units_type_0 = data
                for business_units_type_0_item_data in _business_units_type_0:
                    business_units_type_0_item = VendorBusinessUnitStatsResponsePublicDto.from_dict(
                        business_units_type_0_item_data
                    )

                    business_units_type_0.append(business_units_type_0_item)

                return business_units_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorBusinessUnitStatsResponsePublicDto"]], data)

        business_units = _parse_business_units(d.pop("businessUnits"))

        def _parse_password_policy(data: object) -> Union[None, list["VendorPasswordPolicyResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                password_policy_type_0 = []
                _password_policy_type_0 = data
                for password_policy_type_0_item_data in _password_policy_type_0:
                    password_policy_type_0_item = VendorPasswordPolicyResponsePublicDto.from_dict(
                        password_policy_type_0_item_data
                    )

                    password_policy_type_0.append(password_policy_type_0_item)

                return password_policy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorPasswordPolicyResponsePublicDto"]], data)

        password_policy = _parse_password_policy(d.pop("passwordPolicy"))

        def _parse_status(data: object) -> Union[None, list["VendorStatusStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                status_type_0 = []
                _status_type_0 = data
                for status_type_0_item_data in _status_type_0:
                    status_type_0_item = VendorStatusStatsResponsePublicDto.from_dict(status_type_0_item_data)

                    status_type_0.append(status_type_0_item)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorStatusStatsResponsePublicDto"]], data)

        status = _parse_status(d.pop("status"))

        def _parse_is_critical(data: object) -> Union[None, list["VendorIsCriticalStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                is_critical_type_0 = []
                _is_critical_type_0 = data
                for is_critical_type_0_item_data in _is_critical_type_0:
                    is_critical_type_0_item = VendorIsCriticalStatsResponsePublicDto.from_dict(
                        is_critical_type_0_item_data
                    )

                    is_critical_type_0.append(is_critical_type_0_item)

                return is_critical_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorIsCriticalStatsResponsePublicDto"]], data)

        is_critical = _parse_is_critical(d.pop("isCritical"))

        def _parse_is_sub_processor(data: object) -> Union[None, list["VendorIsSubProcessorStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                is_sub_processor_type_0 = []
                _is_sub_processor_type_0 = data
                for is_sub_processor_type_0_item_data in _is_sub_processor_type_0:
                    is_sub_processor_type_0_item = VendorIsSubProcessorStatsResponsePublicDto.from_dict(
                        is_sub_processor_type_0_item_data
                    )

                    is_sub_processor_type_0.append(is_sub_processor_type_0_item)

                return is_sub_processor_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorIsSubProcessorStatsResponsePublicDto"]], data)

        is_sub_processor = _parse_is_sub_processor(d.pop("isSubProcessor"))

        def _parse_type_(data: object) -> Union[None, list["VendorTypeStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                type_type_0 = []
                _type_type_0 = data
                for type_type_0_item_data in _type_type_0:
                    type_type_0_item = VendorTypeStatsResponsePublicDto.from_dict(type_type_0_item_data)

                    type_type_0.append(type_type_0_item)

                return type_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorTypeStatsResponsePublicDto"]], data)

        type_ = _parse_type_(d.pop("type"))

        def _parse_risk(data: object) -> Union[None, list["VendorsRiskStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                risk_type_0 = []
                _risk_type_0 = data
                for risk_type_0_item_data in _risk_type_0:
                    risk_type_0_item = VendorsRiskStatsResponsePublicDto.from_dict(risk_type_0_item_data)

                    risk_type_0.append(risk_type_0_item)

                return risk_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorsRiskStatsResponsePublicDto"]], data)

        risk = _parse_risk(d.pop("risk"))

        def _parse_impact_level(data: object) -> Union[None, list["VendorImpactLevelStatsResponsePublicDto"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                impact_level_type_0 = []
                _impact_level_type_0 = data
                for impact_level_type_0_item_data in _impact_level_type_0:
                    impact_level_type_0_item = VendorImpactLevelStatsResponsePublicDto.from_dict(
                        impact_level_type_0_item_data
                    )

                    impact_level_type_0.append(impact_level_type_0_item)

                return impact_level_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["VendorImpactLevelStatsResponsePublicDto"]], data)

        impact_level = _parse_impact_level(d.pop("impactLevel"))

        vendors_stats_response_public_dto = cls(
            reminder=reminder,
            has_pii=has_pii,
            business_units=business_units,
            password_policy=password_policy,
            status=status,
            is_critical=is_critical,
            is_sub_processor=is_sub_processor,
            type_=type_,
            risk=risk,
            impact_level=impact_level,
        )

        vendors_stats_response_public_dto.additional_properties = d
        return vendors_stats_response_public_dto

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
