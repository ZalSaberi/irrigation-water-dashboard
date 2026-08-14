from __future__ import annotations

from aqualog.domain.enums import OverallStatus, RestrictionLevel
from aqualog.domain.models import OverallAssessment, ParameterAssessment


def build_overall_assessment(
    *,
    ph: ParameterAssessment,
    ec: ParameterAssessment,
    tds: ParameterAssessment,
    sar: ParameterAssessment,
) -> OverallAssessment:
    # RFP application summary rule. The FAO EC-SAR infiltration diagnostic is
    # intentionally kept separate instead of being collapsed into this card.
    levels = (ph.level, ec.level, tds.level, sar.level)

    if RestrictionLevel.SEVERE in levels:
        return OverallAssessment(
            status=OverallStatus.UNSUITABLE,
            status_en="Severe restriction",
            status_fa="نامناسب / محدودیت شدید",
            color_key="red",
            note_fa="حداقل یکی از شاخص‌های اصلی دارای محدودیت شدید است.",
            note_en="At least one primary indicator has a severe restriction.",
        )

    if RestrictionLevel.SLIGHT_MODERATE in levels or RestrictionLevel.REVIEW in levels:
        return OverallAssessment(
            status=OverallStatus.CAUTION,
            status_en="Caution",
            status_fa="نیازمند احتیاط",
            color_key="yellow",
            note_fa="حداقل یکی از شاخص‌های اصلی نیازمند احتیاط یا بررسی است.",
            note_en="At least one primary indicator requires caution or review.",
        )

    return OverallAssessment(
        status=OverallStatus.SUITABLE,
        status_en="Suitable",
        status_fa="مناسب",
        color_key="green",
        note_fa="در شاخص‌های اصلی بررسی‌شده محدودیت قابل توجهی مشاهده نشد.",
        note_en="No significant restriction was identified in the primary indicators.",
    )
