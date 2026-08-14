from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aqualog.data import SQLiteDatabase, WaterSampleRepository

from .import_service import ImportService


@dataclass(frozen=True, slots=True)
class SeedResult:
    """Describe the outcome of preparing the bundled starter dataset."""

    status: str
    source_path: Path
    imported_rows: int = 0
    analyzed_rows: int = 0

    @property
    def seeded(self) -> bool:
        return self.status == "seeded"


class SeedDataError(RuntimeError):
    """Raised when the bundled starter dataset cannot be imported completely."""


class InitialDataService:
    """Populate an empty application database with the bundled 300-sample dataset."""

    def __init__(self, database: SQLiteDatabase, import_service: ImportService):
        self.database = database
        self.import_service = import_service
        self.samples = WaterSampleRepository(database)

    def ensure_seeded(self, source_path: str | Path) -> SeedResult:
        seed_path = Path(source_path)

        if self.samples.count() > 0:
            return SeedResult(status="already-populated", source_path=seed_path)

        if not seed_path.is_file():
            return SeedResult(status="missing", source_path=seed_path)

        report = self.import_service.import_and_analyze(
            seed_path,
            persist=True,
            continue_on_error=True,
        )

        if report.failed_rows:
            raise SeedDataError(
                "Bundled starter data could not be imported completely: "
                f"{report.failed_rows} row(s) failed."
            )

        return SeedResult(
            status="seeded",
            source_path=seed_path,
            imported_rows=report.imported_rows,
            analyzed_rows=report.successful_rows,
        )
