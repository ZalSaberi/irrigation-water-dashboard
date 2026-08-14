from __future__ import annotations

from enum import Enum


class RestrictionLevel(str, Enum):
    NONE = "none"
    SLIGHT_MODERATE = "slight_moderate"
    SEVERE = "severe"
    REVIEW = "review"


class OverallStatus(str, Enum):
    SUITABLE = "suitable"
    CAUTION = "caution"
    UNSUITABLE = "unsuitable"


class ECUnit(str, Enum):
    US_CM = "µS/cm"
    DS_M = "dS/m"


class TDSUnit(str, Enum):
    MG_L = "mg/L"


class WilcoxClass(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    PERMISSIBLE = "permissible"
    DOUBTFUL = "doubtful"
    UNSUITABLE = "unsuitable"


class QCStatus(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    NOT_AVAILABLE = "not_available"
