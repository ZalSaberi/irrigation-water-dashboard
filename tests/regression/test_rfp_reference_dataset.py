from __future__ import annotations

import csv
from pathlib import Path

import pytest

from aqualog.core.engine import IrrigationAnalysisEngine
from aqualog.domain.errors import WaterSampleValidationError
from aqualog.domain.models import WaterSample


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "data" / "fixtures" / "rfp"
engine = IrrigationAnalysisEngine()


def _rows(name: str):
    with (FIXTURES / name).open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def _value(value: str):
    return None if value == "" else value


def test_all_300_real_samples_match_reference_answers():
    inputs = {row["sample_id"]: row for row in _rows("rfp_input_20_sources.csv")}
    refs = {row["sample_id"]: row for row in _rows("rfp_reference_answers.csv")}
    assert len(inputs) == 300
    assert set(inputs) == set(refs)

    for sample_id, row in inputs.items():
        result = engine.analyze(WaterSample(
            sample_id=sample_id,
            source_id=row["source_id"],
            source_type=row["source_type"],
            sub_basin=row["sub_basin"],
            river=row["river"],
            sample_date=row["sample_date"],
            ph=row["pH"],
            ec=row["EC_value"],
            ec_unit=row["EC_unit"],
            tds=row["TDS_value"],
            tds_unit=row["TDS_unit"],
            sar=row["SAR"],
        ))
        ref = refs[sample_id]
        assert result.ec.code == ref["FAO_salinity_EC_restriction"], sample_id
        assert result.tds.code == ref["FAO_salinity_TDS_restriction"], sample_id
        assert result.sar.code == ref["FAO_SAR_surface_toxicity"], sample_id
        assert result.infiltration.code == ref["FAO_EC_SAR_infiltration_restriction"], sample_id
        assert result.ph.code == ref["FAO_pH_status"], sample_id
        assert result.overall.status_en == ref["dashboard_overall_status_en"], sample_id
        assert result.overall.status_fa == ref["dashboard_overall_status_fa"], sample_id
        assert result.overall.color_key == ref["dashboard_color"], sample_id


def test_validation_and_boundary_fixture():
    for row in _rows("validation_boundary_cases.csv"):
        sample = WaterSample(
            sample_id=row["case_id"],
            ph=_value(row["pH"]),
            ec=_value(row["EC_value"]),
            ec_unit=row["EC_unit"],
            tds=_value(row["TDS_value"]),
            tds_unit=row["TDS_unit"],
            sar=_value(row["SAR"]),
        )
        expected = row["expected_validation"]
        if expected.startswith("Invalid"):
            with pytest.raises(WaterSampleValidationError):
                engine.analyze(sample)
        else:
            result = engine.analyze(sample)
            if row["expected_color"] in {"green", "yellow", "red"}:
                assert result.overall.color_key == row["expected_color"], row["case_id"]
