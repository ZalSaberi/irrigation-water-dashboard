import pytest

from aqualog.core.engine import IrrigationAnalysisEngine
from aqualog.domain.errors import WaterSampleValidationError
from aqualog.domain.models import WaterSample


engine = IrrigationAnalysisEngine()


def test_green_case():
    result = engine.analyze(WaterSample(
        sample_id="G1", ph=7.2, ec=600, ec_unit="µS/cm", tds=400, sar=2,
    ))
    assert result.overall.color_key == "green"
    assert result.ec.code == "None"


def test_yellow_case():
    result = engine.analyze(WaterSample(
        sample_id="Y1", ph=7.5, ec=1500, ec_unit="µS/cm", tds=900, sar=5,
    ))
    assert result.overall.color_key == "yellow"


def test_red_case():
    result = engine.analyze(WaterSample(
        sample_id="R1", ph=7.8, ec=4500, ec_unit="µS/cm", tds=2600, sar=12,
    ))
    assert result.overall.color_key == "red"


def test_ec_ds_m_unit_is_normalized():
    result = engine.analyze(WaterSample(
        sample_id="U1", ph=7.2, ec=0.65, ec_unit="dS/m", tds=400, sar=2,
    ))
    assert result.sample.ec_ds_m == pytest.approx(0.65)
    assert result.ec.code == "None"


def test_invalid_negative_ec_is_rejected():
    with pytest.raises(WaterSampleValidationError):
        engine.analyze(WaterSample(sample_id="BAD", ph=7, ec=-1, tds=400, sar=2))
