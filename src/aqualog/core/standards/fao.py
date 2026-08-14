from __future__ import annotations

from dataclasses import dataclass

from aqualog.domain.enums import RestrictionLevel
from aqualog.domain.models import InfiltrationAssessment, ParameterAssessment


FAO_SOURCE = "FAO Irrigation and Drainage Paper 29 Rev. 1 (Ayers & Westcot, 1985)"


@dataclass(frozen=True, slots=True)
class InfiltrationBand:
    sar_min: float
    sar_max: float
    no_restriction_above_ec: float
    severe_below_ec: float


INFILTRATION_BANDS = (
    InfiltrationBand(0.0, 3.0, 0.7, 0.2),
    InfiltrationBand(3.0, 6.0, 1.2, 0.3),
    InfiltrationBand(6.0, 12.0, 1.9, 0.5),
    InfiltrationBand(12.0, 20.0, 2.9, 1.3),
    InfiltrationBand(20.0, 40.0000001, 5.0, 2.9),
)


def _assessment(
    *, parameter: str, value: float, unit: str, level: RestrictionLevel, code: str,
    title_fa: str, title_en: str, note_fa: str = "", note_en: str = "",
) -> ParameterAssessment:
    return ParameterAssessment(
        parameter=parameter,
        value=value,
        unit=unit,
        level=level,
        code=code,
        title_fa=title_fa,
        title_en=title_en,
        standard=FAO_SOURCE,
        note_fa=note_fa,
        note_en=note_en,
    )


def assess_ec(ec_ds_m: float) -> ParameterAssessment:
    if ec_ds_m < 0.7:
        return _assessment(parameter="EC", value=ec_ds_m, unit="dS/m", level=RestrictionLevel.NONE,
                           code="None", title_fa="بدون محدودیت شوری", title_en="No salinity restriction")
    if ec_ds_m <= 3.0:
        return _assessment(parameter="EC", value=ec_ds_m, unit="dS/m", level=RestrictionLevel.SLIGHT_MODERATE,
                           code="Slight-Moderate", title_fa="محدودیت شوری خفیف تا متوسط", title_en="Slight to moderate salinity restriction")
    return _assessment(parameter="EC", value=ec_ds_m, unit="dS/m", level=RestrictionLevel.SEVERE,
                       code="Severe", title_fa="محدودیت شدید شوری", title_en="Severe salinity restriction")


def assess_tds(tds_mg_l: float) -> ParameterAssessment:
    if tds_mg_l < 450.0:
        return _assessment(parameter="TDS", value=tds_mg_l, unit="mg/L", level=RestrictionLevel.NONE,
                           code="None", title_fa="بدون محدودیت شوری", title_en="No salinity restriction")
    if tds_mg_l <= 2000.0:
        return _assessment(parameter="TDS", value=tds_mg_l, unit="mg/L", level=RestrictionLevel.SLIGHT_MODERATE,
                           code="Slight-Moderate", title_fa="محدودیت شوری خفیف تا متوسط", title_en="Slight to moderate salinity restriction")
    return _assessment(parameter="TDS", value=tds_mg_l, unit="mg/L", level=RestrictionLevel.SEVERE,
                       code="Severe", title_fa="محدودیت شدید شوری", title_en="Severe salinity restriction")


def assess_sar_surface_toxicity(sar: float) -> ParameterAssessment:
    if sar < 3.0:
        return _assessment(parameter="SAR", value=sar, unit="-", level=RestrictionLevel.NONE,
                           code="None", title_fa="بدون محدودیت سمیت سدیم", title_en="No sodium-toxicity restriction")
    if sar <= 9.0:
        return _assessment(parameter="SAR", value=sar, unit="-", level=RestrictionLevel.SLIGHT_MODERATE,
                           code="Slight-Moderate", title_fa="محدودیت سمیت سدیم خفیف تا متوسط", title_en="Slight to moderate sodium-toxicity restriction")
    return _assessment(parameter="SAR", value=sar, unit="-", level=RestrictionLevel.SEVERE,
                       code="Severe", title_fa="محدودیت شدید سمیت سدیم", title_en="Severe sodium-toxicity restriction")


def assess_ph(ph: float) -> ParameterAssessment:
    if 6.5 <= ph <= 8.4:
        return _assessment(parameter="pH", value=ph, unit="-", level=RestrictionLevel.NONE,
                           code="Normal", title_fa="محدوده معمول", title_en="Normal range")
    return _assessment(
        parameter="pH", value=ph, unit="-", level=RestrictionLevel.REVIEW,
        code="Review", title_fa="نیازمند بررسی", title_en="Review recommended",
        note_fa="pH خارج از محدوده معمول ۶٫۵ تا ۸٫۴ است؛ این مورد به‌تنهایی حکم نامناسب بودن آب نیست.",
        note_en="pH is outside the usual 6.5–8.4 range; this alone is not a definitive unsuitability classification.",
    )


def assess_infiltration(*, ec_ds_m: float, sar: float) -> InfiltrationAssessment:
    if sar > 40.0:
        return InfiltrationAssessment(
            ec_ds_m=ec_ds_m, sar=sar, level=RestrictionLevel.REVIEW,
            code="Outside-FAO-table", title_fa="خارج از جدول FAO", title_en="Outside FAO table",
            standard=FAO_SOURCE,
            note_fa="SAR بالاتر از ۴۰ خارج از محدوده جدول نفوذپذیری استفاده‌شده در این نسخه است و باید تخصصی بررسی شود.",
            note_en="SAR above 40 is outside the infiltration table implemented in this version and requires expert review.",
        )

    band = next((b for b in INFILTRATION_BANDS if b.sar_min <= sar < b.sar_max), None)
    if band is None:
        raise ValueError("SAR must be non-negative.")

    if ec_ds_m > band.no_restriction_above_ec:
        level, code = RestrictionLevel.NONE, "None"
        fa, en = "بدون محدودیت نفوذپذیری", "No infiltration restriction"
    elif ec_ds_m >= band.severe_below_ec:
        level, code = RestrictionLevel.SLIGHT_MODERATE, "Slight-Moderate"
        fa, en = "محدودیت نفوذپذیری خفیف تا متوسط", "Slight to moderate infiltration restriction"
    else:
        level, code = RestrictionLevel.SEVERE, "Severe"
        fa, en = "محدودیت شدید نفوذپذیری", "Severe infiltration restriction"

    return InfiltrationAssessment(
        ec_ds_m=ec_ds_m, sar=sar, level=level, code=code,
        title_fa=fa, title_en=en, standard=FAO_SOURCE,
    )
