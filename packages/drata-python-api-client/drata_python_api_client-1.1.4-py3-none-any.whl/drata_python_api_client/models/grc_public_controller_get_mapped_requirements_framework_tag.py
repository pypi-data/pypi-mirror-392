from enum import Enum


class GRCPublicControllerGetMappedRequirementsFrameworkTag(str, Enum):
    CCM = "CCM"
    CCPA = "CCPA"
    CMMC = "CMMC"
    COBIT = "COBIT"
    CUSTOM = "CUSTOM"
    CYBER_ESSENTIALS = "CYBER_ESSENTIALS"
    DORA = "DORA"
    DRATA_ESSENTIALS = "DRATA_ESSENTIALS"
    FEDRAMP = "FEDRAMP"
    FFIEC = "FFIEC"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    ISO27001 = "ISO27001"
    ISO270012022 = "ISO270012022"
    ISO270172015 = "ISO270172015"
    ISO270182019 = "ISO270182019"
    ISO27701 = "ISO27701"
    ISO420012023 = "ISO420012023"
    MSSSPA = "MSSSPA"
    NIS2 = "NIS2"
    NIST800171 = "NIST800171"
    NIST800171R3 = "NIST800171R3"
    NIST80053 = "NIST80053"
    NISTAI = "NISTAI"
    NISTCSF = "NISTCSF"
    NISTCSF2 = "NISTCSF2"
    NONE = "NONE"
    PCI = "PCI"
    PCI4 = "PCI4"
    SCF = "SCF"
    SOC_2 = "SOC_2"
    SOX_ITGC = "SOX_ITGC"

    def __str__(self) -> str:
        return str(self.value)
