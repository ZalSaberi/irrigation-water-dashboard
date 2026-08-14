from pathlib import Path

from aqualog.data import (
    AnalysisResultRepository,
    SQLiteDatabase,
    TabularWaterSampleImporter,
    WaterSampleRepository,
    WaterSourceRepository,
)
from aqualog.domain.models import WaterSample
from aqualog.services import AnalysisService, ImportService


def test_sqlite_roundtrip_and_analysis_persistence(tmp_path: Path):
    db = SQLiteDatabase(tmp_path / "app.sqlite3")
    db.initialize()
    service = AnalysisService(db)

    sample = WaterSample(
        sample_id="DB-001",
        source_id="SRC-001",
        source_name="Test well",
        source_type="Well",
        sample_date="2026-08-14",
        ph=7.2,
        ec=650,
        ec_unit="µS/cm",
        tds=420,
        sar=2.5,
    )
    result = service.analyze(sample)

    assert result.overall.color_key == "green"
    assert WaterSourceRepository(db).count() == 1
    assert WaterSampleRepository(db).count() == 1
    assert AnalysisResultRepository(db).count() == 1

    restored = WaterSampleRepository(db).get("DB-001")
    assert restored is not None
    assert float(restored.ec) == 650
    assert restored.source_name == "Test well"

    stored_result = AnalysisResultRepository(db).get_latest("DB-001")
    assert stored_result is not None
    assert stored_result.overall_color == "green"


def test_csv_import_to_database_pipeline(tmp_path: Path):
    csv_path = tmp_path / "input.csv"
    csv_path.write_text(
        "sample_id,source_id,source_type,sample_date,pH,EC_value,EC_unit,TDS_value,TDS_unit,SAR\n"
        "S1,W1,Well,2026-01-01,7.2,650,µS/cm,420,mg/L,2.5\n"
        "S2,W1,Well,2026-02-01,7.5,1500,µS/cm,900,mg/L,5\n",
        encoding="utf-8-sig",
    )

    db = SQLiteDatabase(tmp_path / "pipeline.sqlite3")
    db.initialize()
    report = ImportService(AnalysisService(db)).import_and_analyze(csv_path)

    assert report.total_rows == 2
    assert report.successful_rows == 2
    assert report.failed_rows == 0
    assert WaterSampleRepository(db).count() == 2
    assert AnalysisResultRepository(db).count() == 2


def test_xlsx_import(tmp_path: Path):
    import pandas as pd

    xlsx_path = tmp_path / "input.xlsx"
    pd.DataFrame([
        {
            "sample_id": "X1",
            "source_id": "R1",
            "pH": 7.1,
            "EC_value": 0.65,
            "EC_unit": "dS/m",
            "TDS_value": 400,
            "TDS_unit": "mg/L",
            "SAR": 2,
        }
    ]).to_excel(xlsx_path, index=False, engine="openpyxl")

    imported = TabularWaterSampleImporter().load(xlsx_path)
    assert imported.valid_rows == 1
    assert imported.failed_rows == 0
    assert imported.samples[0].sample_id == "X1"
    assert imported.samples[0].ec_unit == "dS/m"
