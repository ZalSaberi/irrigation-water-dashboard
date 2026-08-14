from __future__ import annotations

from pathlib import Path

from aqualog.data import AnalysisResultRepository, SQLiteDatabase, WaterSampleRepository, WaterSourceRepository
from aqualog.services import AnalysisService, ImportService, InitialDataService


ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "data" / "fixtures" / "rfp" / "rfp_input_20_sources.csv"


def test_initial_seed_populates_empty_database_once(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "seed.sqlite3")
    database.initialize()
    service = InitialDataService(database, ImportService(AnalysisService(database)))

    first = service.ensure_seeded(SEED)

    assert first.seeded is True
    assert first.imported_rows == 300
    assert first.analyzed_rows == 300
    assert WaterSourceRepository(database).count() == 20
    assert WaterSampleRepository(database).count() == 300
    assert AnalysisResultRepository(database).count() == 300

    second = service.ensure_seeded(SEED)

    assert second.status == "already-populated"
    assert WaterSourceRepository(database).count() == 20
    assert WaterSampleRepository(database).count() == 300
    assert AnalysisResultRepository(database).count() == 300
