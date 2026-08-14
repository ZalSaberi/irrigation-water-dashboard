from aqualog.core.standards.fao import (
    assess_ec,
    assess_infiltration,
    assess_ph,
    assess_sar_surface_toxicity,
    assess_tds,
)


def test_ec_boundaries():
    assert assess_ec(0.6999).code == "None"
    assert assess_ec(0.7).code == "Slight-Moderate"
    assert assess_ec(3.0).code == "Slight-Moderate"
    assert assess_ec(3.0001).code == "Severe"


def test_tds_boundaries():
    assert assess_tds(449.9).code == "None"
    assert assess_tds(450).code == "Slight-Moderate"
    assert assess_tds(2000).code == "Slight-Moderate"
    assert assess_tds(2000.1).code == "Severe"


def test_sar_toxicity_boundaries():
    assert assess_sar_surface_toxicity(2.99).code == "None"
    assert assess_sar_surface_toxicity(3).code == "Slight-Moderate"
    assert assess_sar_surface_toxicity(9).code == "Slight-Moderate"
    assert assess_sar_surface_toxicity(9.01).code == "Severe"


def test_ph_boundaries():
    assert assess_ph(6.5).code == "Normal"
    assert assess_ph(8.4).code == "Normal"
    assert assess_ph(6.49).code == "Review"
    assert assess_ph(8.41).code == "Review"


def test_infiltration_matrix_examples():
    assert assess_infiltration(ec_ds_m=0.2, sar=2).code == "Slight-Moderate"
    assert assess_infiltration(ec_ds_m=0.199, sar=2).code == "Severe"
    assert assess_infiltration(ec_ds_m=0.701, sar=2).code == "None"
    assert assess_infiltration(ec_ds_m=0.299, sar=4).code == "Severe"
    assert assess_infiltration(ec_ds_m=2.0, sar=8).code == "None"
    assert assess_infiltration(ec_ds_m=6.0, sar=41).code == "Outside-FAO-table"
