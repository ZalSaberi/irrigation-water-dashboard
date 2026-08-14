from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .enums import ECUnit, OverallStatus, QCStatus, RestrictionLevel, TDSUnit


NumericInput = float | int | str | None


@dataclass(frozen=True, slots=True)
class IonProfile:
    ca_meq_l: NumericInput = None
    mg_meq_l: NumericInput = None
    na_meq_l: NumericInput = None
    k_meq_l: NumericInput = None
    co3_meq_l: NumericInput = None
    hco3_meq_l: NumericInput = None
    cl_meq_l: NumericInput = None
    so4_meq_l: NumericInput = None
    no3_meq_l: NumericInput = None


@dataclass(frozen=True, slots=True)
class WaterSample:
    sample_id: str
    ph: NumericInput
    ec: NumericInput
    tds: NumericInput
    sar: NumericInput
    ec_unit: ECUnit | str = ECUnit.US_CM
    tds_unit: TDSUnit | str = TDSUnit.MG_L
    source_id: str | None = None
    source_name: str | None = None
    source_type: str | None = None
    sub_basin: str | None = None
    river: str | None = None
    sample_date: date | str | None = None
    ions: IonProfile | None = None


@dataclass(frozen=True, slots=True)
class NormalizedWaterSample:
    sample_id: str
    ph: float
    ec_ds_m: float
    tds_mg_l: float
    sar: float
    source_id: str | None = None
    source_name: str | None = None
    source_type: str | None = None
    sub_basin: str | None = None
    river: str | None = None
    sample_date: date | str | None = None
    ions: IonProfile | None = None


@dataclass(frozen=True, slots=True)
class ParameterAssessment:
    parameter: str
    value: float
    unit: str
    level: RestrictionLevel
    code: str
    title_fa: str
    title_en: str
    standard: str
    note_fa: str = ""
    note_en: str = ""


@dataclass(frozen=True, slots=True)
class InfiltrationAssessment:
    ec_ds_m: float
    sar: float
    level: RestrictionLevel
    code: str
    title_fa: str
    title_en: str
    standard: str
    note_fa: str = ""
    note_en: str = ""


@dataclass(frozen=True, slots=True)
class OverallAssessment:
    status: OverallStatus
    status_en: str
    status_fa: str
    color_key: str
    note_fa: str
    note_en: str


@dataclass(frozen=True, slots=True)
class ScientificDiagnostics:
    calculated_sar: float | None = None
    sodium_percent: float | None = None
    total_hardness_mg_l: float | None = None
    ionic_balance_percent: float | None = None
    ionic_balance_qc: QCStatus = QCStatus.NOT_AVAILABLE
    tds_ec_factor: float | None = None
    tds_ec_qc: QCStatus = QCStatus.NOT_AVAILABLE


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    sample: NormalizedWaterSample
    ph: ParameterAssessment
    ec: ParameterAssessment
    tds: ParameterAssessment
    sar: ParameterAssessment
    infiltration: InfiltrationAssessment
    overall: OverallAssessment
    scientific: ScientificDiagnostics
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample.sample_id,
            "ph": self.ph.code,
            "ec": self.ec.code,
            "tds": self.tds.code,
            "sar": self.sar.code,
            "infiltration": self.infiltration.code,
            "overall_status": self.overall.status_en,
            "overall_color": self.overall.color_key,
        }
