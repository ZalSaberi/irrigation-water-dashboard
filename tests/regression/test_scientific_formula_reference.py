from __future__ import annotations

import csv
import math
from pathlib import Path

from aqualog.core.formulas import calculate_sar


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "data" / "fixtures" / "rfp"


def test_calculated_sar_matches_prepared_scientific_reference():
    checked = 0
    with (FIXTURES / "scientific_support_raw_ions.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if not all(row[key] for key in ("Na_meq_L", "Ca_meq_L", "Mg_meq_L", "calc_SAR")):
                continue
            actual = calculate_sar(
                na_meq_l=float(row["Na_meq_L"]),
                ca_meq_l=float(row["Ca_meq_L"]),
                mg_meq_l=float(row["Mg_meq_L"]),
            )
            assert math.isclose(actual, float(row["calc_SAR"]), rel_tol=1e-10, abs_tol=1e-10)
            checked += 1
    assert checked > 0
