# RFP Reference Data

This directory contains the compact scientific dataset used to develop and regression-test **Grovity Irrigation Water**.

## Coverage

- 20 real river-monitoring sources
- 20 Iranian hydrological sub-basins
- 15 chronological observations per selected source
- 300 observations in the application fixture
- source records spanning 1964–2020

The subset is intentionally small enough for fast development while retaining low, moderate, and severe salinity conditions, temporal variation, and threshold-adjacent cases.

## Primary Inputs

The application workflow uses:

- pH
- EC
- TDS
- SAR

Metadata such as source ID and sample date is included for filtering, comparison, and trend charts.

## Scientific Profile

The current MVP uses FAO-oriented rules for the primary assessment:

| Indicator | No restriction / normal | Slight–moderate / review | Severe |
|---|---:|---:|---:|
| EC | `< 0.7 dS/m` | `0.7–3.0 dS/m` | `> 3.0 dS/m` |
| TDS | `< 450 mg/L` | `450–2000 mg/L` | `> 2000 mg/L` |
| SAR | `< 3` | `3–9` | `> 9` |
| pH | `6.5–8.4` | outside the normal range | — |

The EC–SAR infiltration matrix is evaluated separately from the overall application status.

## Files

| File | Purpose |
|---|---|
| `rfp_input_20_sources.csv` | Clean application input fixture |
| `rfp_reference_answers.csv` | Expected classifications and dashboard status |
| `scientific_support_raw_ions.csv` | Raw ionic chemistry for independent formula checks |
| `selected_sources.csv` | Metadata for the 20 selected sources |
| `standards_rfp.csv` | Versionable classification rules |
| `formula_catalog_rfp.csv` | Formula and unit-conversion catalog |
| `validation_boundary_cases.csv` | Boundary, missing-value, unit, and invalid-input cases |
| `data_dictionary.csv` | Import schema and field validation notes |
| `rfp_traceability.csv` | RFP requirement-to-data traceability |
| `input_template.csv` | User-facing import template |

## Regression Workflow

1. Import `rfp_input_20_sources.csv`.
2. Analyze each sample with the application engine.
3. Compare results against `rfp_reference_answers.csv`.
4. Run boundary validation with `validation_boundary_cases.csv`.
5. Verify scientific formulas against `scientific_support_raw_ions.csv`.
