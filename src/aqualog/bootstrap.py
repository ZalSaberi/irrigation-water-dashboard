from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from aqualog.data.database import SQLiteDatabase
from aqualog.services import (
    AnalysisService,
    ArchiveQueryService,
    DashboardQueryService,
    ImportService,
    InitialDataService,
)


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    database: SQLiteDatabase
    analysis: AnalysisService
    importer: ImportService
    dashboard: DashboardQueryService
    archive: ArchiveQueryService


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_database_path() -> Path:
    override = os.getenv("GROVITY_IRRIGATION_DB")
    if override:
        return Path(override).expanduser()
    return project_root() / "data" / "database" / "aqualog.sqlite3"


def default_seed_data_path() -> Path:
    override = os.getenv("GROVITY_IRRIGATION_SEED_DATA")
    if override:
        return Path(override).expanduser()
    return project_root() / "data" / "fixtures" / "rfp" / "rfp_input_20_sources.csv"


def _auto_seed_enabled() -> bool:
    value = os.getenv("GROVITY_IRRIGATION_AUTO_SEED", "1").strip().lower()
    return value not in {"0", "false", "no", "off"}


def build_services(database_path: str | Path | None = None) -> ApplicationServices:
    use_default_database = database_path is None
    db = SQLiteDatabase(database_path or default_database_path())
    db.initialize()

    analysis = AnalysisService(db)
    importer = ImportService(analysis)

    if use_default_database and _auto_seed_enabled():
        InitialDataService(db, importer).ensure_seeded(default_seed_data_path())

    return ApplicationServices(
        database=db,
        analysis=analysis,
        importer=importer,
        dashboard=DashboardQueryService(db),
        archive=ArchiveQueryService(db),
    )
