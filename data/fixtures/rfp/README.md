# AquaLog — RFP-aligned irrigation water data pack

This pack is aligned to RFP 1640 for a simple irrigation-water-quality dashboard.

## RFP core inputs
The application import form should require:
- pH
- EC
- TDS
- SAR

Metadata such as sample id, source id/type and date are included because they are needed for comparison and trend charts.

## Prepared real dataset
- 20 real river monitoring sources
- 20 different Iranian hydrological sub-basins
- 15 chronological observations per source
- 300 real observations total
- source: uploaded Iranian river chemistry dataset (1964–2020)

This is intentionally much smaller than the full source workbook while still covering low, moderate and severe salinity situations and long time trends.

## Primary scientific profile for the MVP
FAO Water Quality for Agriculture (Ayers & Westcot) is selected as the primary rule set because it directly supports the four mandatory RFP inputs.

Core rules:
- EC salinity: <0.7 dS/m none; 0.7–3.0 slight/moderate; >3.0 severe
- TDS salinity: <450 mg/L none; 450–2000 slight/moderate; >2000 severe
- SAR surface-irrigation sodium toxicity: <3 none; 3–9 slight/moderate; >9 severe
- pH normal range: 6.5–8.4
- Infiltration risk: joint EC–SAR FAO matrix

Official FAO source:
https://www.fao.org/4/T0234e/T0234E01.htm
https://www.fao.org/4/T0234e/T0234E06.htm

## Dashboard color logic
RFP asks for green / yellow / red.
The pack uses an explicit application aggregation rule for the four mandatory RFP inputs:
- Green: EC/TDS/SAR primary classes have no restriction and pH is normal
- Yellow: at least one EC/TDS/SAR primary class has slight/moderate restriction or pH needs review, with no severe result
- Red: at least one EC/TDS/SAR primary class has severe restriction

The FAO EC–SAR infiltration matrix is displayed separately as a soil-infiltration diagnostic/warning. It is deliberately not collapsed into the single main card color, because FAO treats salinity, infiltration and toxicity as different problem areas.

Important: the overall color is an MVP dashboard aggregation rule, NOT a published FAO water-quality index.

## Wilcox support
The RFP says “such as Wilcox or FAO”. FAO is primary. Na% and raw ions are preserved in the scientific support file so a Wilcox sodium-percentage view can be added without changing the dataset.

## Files
- rfp_input_20_sources.csv — clean import data for the app
- rfp_reference_answers.csv — expected classifications/colors for regression tests
- scientific_support_raw_ions.csv — raw chemistry and independent formula checks
- selected_sources.csv — the 20 selected sources
- standards_rfp.csv — versionable rule table
- formula_catalog_rfp.csv — formulas and unit conversions
- validation_boundary_cases.csv — valid, boundary, missing, wrong-unit and invalid-value tests
- data_dictionary.csv — import schema and validation rules
- rfp_traceability.csv — RFP requirement -> data/test artifact
- input_template.csv — user import template

## Recommended implementation workflow
1. Import `rfp_input_20_sources.csv`.
2. Compute classifications in the application.
3. Compare the output row-by-row with `rfp_reference_answers.csv`.
4. Run validation tests using `validation_boundary_cases.csv`.
5. Use `scientific_support_raw_ions.csv` to unit-test SAR and Na% formulas.
