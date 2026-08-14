<div align="center">
  <img src="src/aqualog/resources/images/grovity_logo.png" alt="Grovity logo" width="150" />

  # Grovity Irrigation Water

  **A Persian desktop dashboard for irrigation-water quality monitoring and analysis.**

  <sub>By Grovity Software Team</sub>

  <br /><br />

  ![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
  ![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52?logo=qt&logoColor=white)
  ![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
  ![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)
  ![RTL](https://img.shields.io/badge/Interface-Persian%20RTL-2DD4BF)
</div>

---

## Overview

**Grovity Irrigation Water** is a desktop application for recording, validating, analyzing, and reviewing irrigation-water quality data. The current analysis workflow focuses on the four primary inputs defined for the project:

- **pH**
- **Electrical Conductivity (EC)**
- **Total Dissolved Solids (TDS)**
- **Sodium Adsorption Ratio (SAR)**

The application combines a tested scientific analysis engine with a local SQLite database and a Persian right-to-left PyQt6 interface.

> [!IMPORTANT]
> The overall green / amber / red status is an **application-level summary** built from the primary indicators. The FAO EC–SAR infiltration assessment is preserved as a separate diagnostic and is not presented as an official FAO composite index.

---

## Highlights

<table>
<tr>
<td width="50%" valign="top">

### Scientific analysis

- FAO-oriented EC, TDS, SAR, and pH assessment
- Joint EC–SAR infiltration diagnostic
- Optional Wilcox sodium-percentage support
- SAR, Na%, total hardness, ionic-balance, and TDS/EC calculations
- Explicit unit normalization before analysis

</td>
<td width="50%" valign="top">

### Desktop workflow

- Persian RTL interface with the **Shabnam** typeface
- Dashboard KPIs, trends, and status distribution
- Sample analysis and persistence
- CSV / Excel import with row-level validation
- Searchable sample archive
- Local SQLite storage

</td>
</tr>
</table>

---

## Application Architecture

```mermaid
flowchart LR
    A[CSV / Excel / Manual Entry] --> B[Import & Validation]
    B --> C[WaterSample]
    C --> D[Analysis Engine]
    D --> E[FAO / Wilcox / QA]
    E --> F[AnalysisResult]
    F --> G[(SQLite)]
    G --> H[Query Services]
    H --> I[PyQt6 Dashboard]
```

The UI does not execute scientific calculations or raw SQL directly. Responsibilities are separated into domain, core analysis, persistence, application services, and presentation layers.

For a more detailed module map, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Project Structure

```text
irrigation-water-dashboard/
├── data/
│   ├── database/              # Local runtime database (ignored by Git)
│   └── fixtures/rfp/          # Regression and validation fixtures
├── docs/
│   ├── ARCHITECTURE.md
│   └── legacy/                # Preserved AquaLog reference material
├── scripts/
│   ├── run_gui.py
│   └── smoke_data_layer.py
├── src/aqualog/
│   ├── core/                  # Scientific rules, formulas, validation
│   ├── data/                  # SQLite and import infrastructure
│   ├── domain/                # Domain models and enums
│   ├── resources/             # Fonts and image assets
│   ├── services/              # Application/query services
│   └── ui/                    # PyQt6 presentation layer
├── tests/
│   ├── integration/
│   ├── regression/
│   └── unit/
├── pyproject.toml
├── requirements-core.txt
├── requirements-export.txt
└── requirements-gui.txt
```

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

### 2. Configure pip for a slower connection (optional)

```bash
python -m pip config set global.timeout 60
python -m pip config set global.retries 10
```

### 3. Install dependencies

```bash
python -m pip install -r requirements-core.txt --timeout 60 --retries 10 --prefer-binary
python -m pip install -r requirements-gui.txt --timeout 60 --retries 10 --prefer-binary
python -m pip install -e . --no-deps
```

Optional export dependencies:

```bash
python -m pip install -r requirements-export.txt --timeout 60 --retries 10 --prefer-binary
```

### 4. Run the test suite

```bash
python -m pytest -q
```

### 5. Seed the local database with the bundled RFP fixture

```bash
python scripts/smoke_data_layer.py
```

### 6. Launch the application

```bash
python -m aqualog
```

or:

```bash
python scripts/run_gui.py
```

---

## Scientific Rules in the Current MVP

| Indicator | No restriction / normal | Caution | Severe / review |
|---|---:|---:|---:|
| **EC** | `< 0.7 dS/m` | `0.7–3.0 dS/m` | `> 3.0 dS/m` |
| **TDS** | `< 450 mg/L` | `450–2000 mg/L` | `> 2000 mg/L` |
| **SAR** | `< 3` | `3–9` | `> 9` |
| **pH** | `6.5–8.4` | outside normal range → review | — |

The engine also evaluates the FAO EC–SAR infiltration matrix separately. Scientific fixtures, formula references, and expected outputs are stored under [`data/fixtures/rfp`](data/fixtures/rfp/).

---

## Data Import

Supported tabular formats:

- `.csv`
- `.xlsx`
- `.xlsm`

Required fields:

```text
sample_id
pH
EC_value
TDS_value
SAR
```

Recommended metadata includes source ID, source name/type, sample date, EC unit, and TDS unit. A ready-to-use template is available at:

[`data/fixtures/rfp/input_template.csv`](data/fixtures/rfp/input_template.csv)

---

## UI Direction

The interface follows a dark scientific-dashboard design language:

- **Dark navy surfaces** for calm visual hierarchy
- **Teal accent** for active controls and primary interactions
- **Green / amber / rose** status colors
- **Shabnam** for Persian typography
- True **RTL page structure**, while scientific values, IDs, URLs, and units remain LTR where appropriate

The UI intentionally avoids heavy animations, glowing effects, and decorative motion so it remains responsive on ordinary hardware.

---

## Testing

The repository includes:

- unit tests for scientific formulas and FAO rules
- regression tests against the prepared reference dataset
- integration tests for import, persistence, analysis, and query services
- UI stylesheet checks

Run everything with:

```bash
python -m pytest
```

---

## Development Team

<table>
<tr>
<td valign="top">

### Sara Saberi
**Lead Developer**

- GitHub: [@ZalSaberi](https://github.com/ZalSaberi)
- Email: `Zal.saberi.s@gmail.com`
- LinkedIn: [saberisara](https://linkedin.com/in/saberisara)

</td>
<td valign="top">

### Maryam Shahidi
**Research & Documentation Intern**

Research support, documentation assistance, and project-study contributions.

</td>
</tr>
</table>

---

## Repository Notes

- Runtime SQLite databases are intentionally excluded from version control.
- Temporary delivery ZIPs, local backups, build output, caches, and generated `*.egg-info` folders are ignored.
- The original AquaLog material used during architectural review is preserved under [`docs/legacy/aqualog`](docs/legacy/aqualog/) and is not part of the active application code.
- Active source-code comments and docstrings are written in concise professional English; Persian is reserved for user-facing application copy.

---

<div align="center">
  <strong>Grovity Irrigation Water</strong><br />
  <sub>By Grovity Software Team</sub>
</div>
