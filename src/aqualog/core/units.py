from __future__ import annotations

from aqualog.domain.enums import ECUnit, TDSUnit
from aqualog.domain.models import NormalizedWaterSample, WaterSample


_EC_ALIASES = {
    "µs/cm": ECUnit.US_CM,
    "μs/cm": ECUnit.US_CM,
    "us/cm": ECUnit.US_CM,
    "uscm": ECUnit.US_CM,
    "µscm": ECUnit.US_CM,
    "ds/m": ECUnit.DS_M,
    "dsm": ECUnit.DS_M,
}

_TDS_ALIASES = {
    "mg/l": TDSUnit.MG_L,
    "mgl": TDSUnit.MG_L,
}


def _clean_unit(value: object) -> str:
    return str(value).strip().lower().replace(" ", "")


def parse_ec_unit(value: ECUnit | str) -> ECUnit:
    if isinstance(value, ECUnit):
        return value
    cleaned = _clean_unit(value)
    try:
        return _EC_ALIASES[cleaned]
    except KeyError as exc:
        raise ValueError(f"Unsupported EC unit: {value!r}") from exc


def parse_tds_unit(value: TDSUnit | str) -> TDSUnit:
    if isinstance(value, TDSUnit):
        return value
    cleaned = _clean_unit(value)
    try:
        return _TDS_ALIASES[cleaned]
    except KeyError as exc:
        raise ValueError(f"Unsupported TDS unit: {value!r}") from exc


def ec_to_ds_m(value: float, unit: ECUnit | str) -> float:
    parsed = parse_ec_unit(unit)
    if parsed is ECUnit.US_CM:
        return value / 1000.0
    return value


def tds_to_mg_l(value: float, unit: TDSUnit | str) -> float:
    parse_tds_unit(unit)
    return value


def normalize_sample(sample: WaterSample) -> NormalizedWaterSample:
    return NormalizedWaterSample(
        sample_id=sample.sample_id.strip(),
        ph=float(sample.ph),
        ec_ds_m=ec_to_ds_m(float(sample.ec), sample.ec_unit),
        tds_mg_l=tds_to_mg_l(float(sample.tds), sample.tds_unit),
        sar=float(sample.sar),
        source_id=sample.source_id,
        source_name=sample.source_name,
        source_type=sample.source_type,
        sub_basin=sample.sub_basin,
        river=sample.river,
        sample_date=sample.sample_date,
        ions=sample.ions,
    )
