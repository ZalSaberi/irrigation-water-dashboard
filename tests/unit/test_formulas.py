import math

from aqualog.core.formulas import (
    calculate_sar,
    calculate_sodium_percentage,
    calculate_total_hardness,
)


def test_sar_formula():
    result = calculate_sar(na_meq_l=5.0, ca_meq_l=4.0, mg_meq_l=2.0)
    assert math.isclose(result, 5.0 / math.sqrt(3.0), rel_tol=1e-12)


def test_sodium_percentage_formula():
    result = calculate_sodium_percentage(na_meq_l=5, k_meq_l=1, ca_meq_l=3, mg_meq_l=1)
    assert math.isclose(result, 60.0)


def test_total_hardness_formula():
    assert calculate_total_hardness(ca_meq_l=3, mg_meq_l=2) == 250.0
