from __future__ import annotations

from aqualog.domain.enums import QCStatus, RestrictionLevel
from aqualog.domain.models import (
    AnalysisResult,
    IonProfile,
    ScientificDiagnostics,
    WaterSample,
)

from .assessment import build_overall_assessment
from .formulas import (
    calculate_ionic_balance,
    calculate_sar,
    calculate_sodium_percentage,
    calculate_tds_ec_factor,
    calculate_total_hardness,
)
from .standards.fao import (
    assess_ec,
    assess_infiltration,
    assess_ph,
    assess_sar_surface_toxicity,
    assess_tds,
)
from .units import normalize_sample
from .validation import validate_sample


def _optional_float(value: object) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _all(values: list[float | None]) -> bool:
    return all(v is not None for v in values)


class IrrigationAnalysisEngine:
    VERSION = "1.0.0"
    STANDARD_PROFILE = "FAO-29-REV1-MVP"

    def analyze(self, sample: WaterSample) -> AnalysisResult:
        validate_sample(sample)
        normalized = normalize_sample(sample)

        ph_result = assess_ph(normalized.ph)
        ec_result = assess_ec(normalized.ec_ds_m)
        tds_result = assess_tds(normalized.tds_mg_l)
        sar_result = assess_sar_surface_toxicity(normalized.sar)
        infiltration_result = assess_infiltration(
            ec_ds_m=normalized.ec_ds_m,
            sar=normalized.sar,
        )
        overall = build_overall_assessment(
            ph=ph_result,
            ec=ec_result,
            tds=tds_result,
            sar=sar_result,
        )

        scientific = self._scientific_diagnostics(normalized)
        warnings = self._warnings(
            ph=ph_result,
            ec=ec_result,
            tds=tds_result,
            sar=sar_result,
            infiltration=infiltration_result,
            scientific=scientific,
        )

        return AnalysisResult(
            sample=normalized,
            ph=ph_result,
            ec=ec_result,
            tds=tds_result,
            sar=sar_result,
            infiltration=infiltration_result,
            overall=overall,
            scientific=scientific,
            warnings=warnings,
        )

    def _scientific_diagnostics(self, sample) -> ScientificDiagnostics:
        ions: IonProfile | None = sample.ions
        calculated_sar = None
        sodium_percent = None
        total_hardness = None
        ionic_balance = None
        ionic_qc = QCStatus.NOT_AVAILABLE

        if ions is not None:
            ca = _optional_float(ions.ca_meq_l)
            mg = _optional_float(ions.mg_meq_l)
            na = _optional_float(ions.na_meq_l)
            k = _optional_float(ions.k_meq_l)
            co3 = _optional_float(ions.co3_meq_l)
            hco3 = _optional_float(ions.hco3_meq_l)
            cl = _optional_float(ions.cl_meq_l)
            so4 = _optional_float(ions.so4_meq_l)
            no3 = _optional_float(ions.no3_meq_l)

            if _all([na, ca, mg]):
                calculated_sar = calculate_sar(na_meq_l=na, ca_meq_l=ca, mg_meq_l=mg)
            if _all([na, k, ca, mg]):
                sodium_percent = calculate_sodium_percentage(
                    na_meq_l=na, k_meq_l=k, ca_meq_l=ca, mg_meq_l=mg
                )
            if _all([ca, mg]):
                total_hardness = calculate_total_hardness(ca_meq_l=ca, mg_meq_l=mg)
            if _all([ca, mg, na, k, co3, hco3, cl, so4, no3]):
                ionic_balance = calculate_ionic_balance(
                    ca_meq_l=ca, mg_meq_l=mg, na_meq_l=na, k_meq_l=k,
                    co3_meq_l=co3, hco3_meq_l=hco3, cl_meq_l=cl,
                    so4_meq_l=so4, no3_meq_l=no3,
                )
                ionic_qc = QCStatus.PASS if abs(ionic_balance) <= 10.0 else QCStatus.REVIEW

        ec_us_cm = sample.ec_ds_m * 1000.0
        tds_ec_factor = None
        tds_ec_qc = QCStatus.NOT_AVAILABLE
        if ec_us_cm > 0:
            tds_ec_factor = calculate_tds_ec_factor(
                tds_mg_l=sample.tds_mg_l,
                ec_us_cm=ec_us_cm,
            )
            tds_ec_qc = QCStatus.PASS if 0.55 <= tds_ec_factor <= 0.75 else QCStatus.REVIEW

        return ScientificDiagnostics(
            calculated_sar=calculated_sar,
            sodium_percent=sodium_percent,
            total_hardness_mg_l=total_hardness,
            ionic_balance_percent=ionic_balance,
            ionic_balance_qc=ionic_qc,
            tds_ec_factor=tds_ec_factor,
            tds_ec_qc=tds_ec_qc,
        )

    @staticmethod
    def _warnings(*, ph, ec, tds, sar, infiltration, scientific) -> tuple[str, ...]:
        warnings: list[str] = []
        for item in (ph, ec, tds, sar):
            if item.level in {RestrictionLevel.SLIGHT_MODERATE, RestrictionLevel.SEVERE, RestrictionLevel.REVIEW}:
                warnings.append(f"{item.parameter}: {item.title_fa}")
        if infiltration.level is not RestrictionLevel.NONE:
            warnings.append(f"نفوذپذیری خاک: {infiltration.title_fa}")
        if scientific.ionic_balance_qc is QCStatus.REVIEW:
            warnings.append("کنترل توازن یونی نیازمند بررسی است.")
        if scientific.tds_ec_qc is QCStatus.REVIEW:
            warnings.append("نسبت TDS/EC خارج از بازه معمول کنترل کیفیت است.")
        return tuple(warnings)
