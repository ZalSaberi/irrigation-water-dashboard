from pathlib import Path

from aqualog.data import AnalysisResultRepository, SQLiteDatabase, WaterSampleRepository, WaterSourceRepository
from aqualog.services import AnalysisService, ImportService


FIXTURE = Path("data/fixtures/rfp/rfp_input_20_sources.csv")


def test_full_rfp_fixture_imports_and_analyzes_300_rows(tmp_path: Path):
    assert FIXTURE.exists(), f"Missing fixture: {FIXTURE}"

    db = SQLiteDatabase(tmp_path / "rfp.sqlite3")
    db.initialize()
    report = ImportService(AnalysisService(db)).import_and_analyze(FIXTURE)

    assert report.total_rows == 300
    assert report.imported_rows == 300
    assert report.successful_rows == 300
    assert report.failed_rows == 0
    assert WaterSourceRepository(db).count() == 20
    assert WaterSampleRepository(db).count() == 300
    assert AnalysisResultRepository(db).count() == 300
