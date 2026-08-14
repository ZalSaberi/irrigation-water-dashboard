from __future__ import annotations

import math

from aqualog.domain.errors import ValidationIssue, WaterSampleValidationError
from aqualog.domain.models import WaterSample
from .units import parse_ec_unit, parse_tds_unit


def _number(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def validate_sample(sample: WaterSample) -> None:
    issues: list[ValidationIssue] = []

    if not isinstance(sample.sample_id, str) or not sample.sample_id.strip():
        issues.append(ValidationIssue(
            "sample_id", "REQUIRED",
            "شناسه نمونه الزامی است.",
            "Sample ID is required.",
        ))

    values = {
        "ph": _number(sample.ph),
        "ec": _number(sample.ec),
        "tds": _number(sample.tds),
        "sar": _number(sample.sar),
    }

    labels_fa = {"ph": "pH", "ec": "EC", "tds": "TDS", "sar": "SAR"}
    for field, value in values.items():
        original = getattr(sample, field)
        if original is None or (isinstance(original, str) and not original.strip()):
            issues.append(ValidationIssue(
                field, "REQUIRED",
                f"مقدار {labels_fa[field]} الزامی است.",
                f"{field.upper()} is required.",
            ))
        elif value is None:
            issues.append(ValidationIssue(
                field, "NOT_NUMERIC",
                f"مقدار {labels_fa[field]} باید عددی و متناهی باشد.",
                f"{field.upper()} must be a finite number.",
            ))

    ph = values["ph"]
    if ph is not None and not 0.0 <= ph <= 14.0:
        issues.append(ValidationIssue(
            "ph", "OUT_OF_RANGE",
            "مقدار pH باید بین ۰ و ۱۴ باشد.",
            "pH must be between 0 and 14.",
        ))

    for field in ("ec", "tds", "sar"):
        value = values[field]
        if value is not None and value < 0:
            issues.append(ValidationIssue(
                field, "NEGATIVE",
                f"مقدار {labels_fa[field]} نمی‌تواند منفی باشد.",
                f"{field.upper()} cannot be negative.",
            ))

    try:
        parse_ec_unit(sample.ec_unit)
    except ValueError:
        issues.append(ValidationIssue(
            "ec_unit", "UNSUPPORTED_UNIT",
            "واحد EC باید µS/cm یا dS/m باشد.",
            "EC unit must be µS/cm or dS/m.",
        ))

    try:
        parse_tds_unit(sample.tds_unit)
    except ValueError:
        issues.append(ValidationIssue(
            "tds_unit", "UNSUPPORTED_UNIT",
            "در نسخه فعلی واحد TDS باید mg/L باشد.",
            "TDS unit must be mg/L in the current version.",
        ))

    if issues:
        raise WaterSampleValidationError(issues)
