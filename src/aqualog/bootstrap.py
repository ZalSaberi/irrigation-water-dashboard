from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from aqualog.data.database import SQLiteDatabase
from aqualog.services import AnalysisService, ArchiveQueryService, DashboardQueryService, ImportService

@dataclass(frozen=True, slots=True)
class ApplicationServices:
    database: SQLiteDatabase
    analysis: AnalysisService
    importer: ImportService
    dashboard: DashboardQueryService
    archive: ArchiveQueryService

def default_database_path() -> Path:
    override = os.getenv('GROVITY_IRRIGATION_DB')
    if override:
        return Path(override).expanduser()
    return Path.cwd() / 'data' / 'database' / 'aqualog.sqlite3'

def build_services(database_path: str | Path | None=None) -> ApplicationServices:
    db = SQLiteDatabase(database_path or default_database_path())
    db.initialize()
    analysis = AnalysisService(db)
    return ApplicationServices(database=db, analysis=analysis, importer=ImportService(analysis), dashboard=DashboardQueryService(db), archive=ArchiveQueryService(db))
