from pathlib import Path

from aqualog.data import AnalysisResultRepository, SQLiteDatabase, WaterSampleRepository, WaterSourceRepository
from aqualog.services import AnalysisService, ImportService


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "fixtures" / "rfp" / "rfp_input_20_sources.csv"
DB = ROOT / "data" / "database" / "aqualog.sqlite3"


def main() -> None:
    db = SQLiteDatabase(DB)
    db.initialize()
    report = ImportService(AnalysisService(db)).import_and_analyze(DATA)

    print(f"Input rows:      {report.total_rows}")
    print(f"Imported rows:   {report.imported_rows}")
    print(f"Analyzed rows:   {report.successful_rows}")
    print(f"Failed rows:     {report.failed_rows}")
    print(f"Sources in DB:   {WaterSourceRepository(db).count()}")
    print(f"Samples in DB:   {WaterSampleRepository(db).count()}")
    print(f"Results in DB:   {AnalysisResultRepository(db).count()}")
    print(f"Database:        {DB}")


if __name__ == "__main__":
    main()
