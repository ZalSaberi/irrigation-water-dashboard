from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from collections.abc import Iterator


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS water_sources (
    source_id TEXT PRIMARY KEY,
    source_name TEXT,
    source_type TEXT,
    sub_basin TEXT,
    river TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS samples (
    sample_id TEXT PRIMARY KEY,
    source_id TEXT,
    sample_date TEXT,
    ph REAL NOT NULL,
    ec_value REAL NOT NULL,
    ec_unit TEXT NOT NULL,
    tds_value REAL NOT NULL,
    tds_unit TEXT NOT NULL,
    sar REAL NOT NULL,
    ions_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES water_sources(source_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    standard_profile TEXT NOT NULL,
    analyzed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ph_code TEXT NOT NULL,
    ph_level TEXT NOT NULL,
    ec_code TEXT NOT NULL,
    ec_level TEXT NOT NULL,
    tds_code TEXT NOT NULL,
    tds_level TEXT NOT NULL,
    sar_code TEXT NOT NULL,
    sar_level TEXT NOT NULL,
    infiltration_code TEXT NOT NULL,
    infiltration_level TEXT NOT NULL,

    overall_status TEXT NOT NULL,
    overall_color TEXT NOT NULL,
    warnings_json TEXT NOT NULL,
    scientific_json TEXT NOT NULL,

    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE(sample_id, engine_version, standard_profile)
);

CREATE INDEX IF NOT EXISTS idx_samples_source_date
    ON samples(source_id, sample_date);
CREATE INDEX IF NOT EXISTS idx_analysis_sample
    ON analysis_results(sample_id, analyzed_at);
"""


class SQLiteDatabase:
    """Small SQLite wrapper used by repositories and services.

    Connections are intentionally short-lived. This keeps the layer safe for a
    future PyQt application where reads and writes may happen from workers.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(SCHEMA_SQL)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
