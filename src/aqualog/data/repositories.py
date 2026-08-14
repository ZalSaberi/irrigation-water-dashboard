from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
import json
import sqlite3
from typing import Any

from aqualog.domain.models import AnalysisResult, IonProfile, WaterSample

from .database import SQLiteDatabase


def _enum_value(value: object) -> str:
    return str(value.value) if isinstance(value, Enum) else str(value)


def _date_value(value: date | str | None) -> str | None:
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return None
    return str(value)


def _ions_json(ions: IonProfile | None) -> str | None:
    return None if ions is None else json.dumps(asdict(ions), ensure_ascii=False)


def _ions_from_json(value: str | None) -> IonProfile | None:
    if not value:
        return None
    return IonProfile(**json.loads(value))


@dataclass(frozen=True, slots=True)
class StoredAnalysis:
    sample_id: str
    engine_version: str
    standard_profile: str
    analyzed_at: str
    ph_code: str
    ec_code: str
    tds_code: str
    sar_code: str
    infiltration_code: str
    overall_status: str
    overall_color: str
    warnings: tuple[str, ...]
    scientific: dict[str, Any]


class _Repository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database


class WaterSourceRepository(_Repository):
    def upsert_from_sample(
        self, sample: WaterSample, *, connection: sqlite3.Connection | None = None
    ) -> None:
        if not sample.source_id:
            return
        query = """
        INSERT INTO water_sources(
            source_id, source_name, source_type, sub_basin, river
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            source_name = COALESCE(excluded.source_name, water_sources.source_name),
            source_type = COALESCE(excluded.source_type, water_sources.source_type),
            sub_basin = COALESCE(excluded.sub_basin, water_sources.sub_basin),
            river = COALESCE(excluded.river, water_sources.river),
            updated_at = CURRENT_TIMESTAMP
        """
        params = (
            sample.source_id,
            sample.source_name,
            sample.source_type,
            sample.sub_basin,
            sample.river,
        )
        if connection is not None:
            connection.execute(query, params)
            return
        with self.database.transaction() as conn:
            conn.execute(query, params)

    def count(self) -> int:
        with self.database.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM water_sources").fetchone()[0])


class WaterSampleRepository(_Repository):
    def upsert(
        self, sample: WaterSample, *, connection: sqlite3.Connection | None = None
    ) -> None:
        query = """
        INSERT INTO samples(
            sample_id, source_id, sample_date, ph, ec_value, ec_unit,
            tds_value, tds_unit, sar, ions_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(sample_id) DO UPDATE SET
            source_id = excluded.source_id,
            sample_date = excluded.sample_date,
            ph = excluded.ph,
            ec_value = excluded.ec_value,
            ec_unit = excluded.ec_unit,
            tds_value = excluded.tds_value,
            tds_unit = excluded.tds_unit,
            sar = excluded.sar,
            ions_json = excluded.ions_json,
            updated_at = CURRENT_TIMESTAMP
        """
        params = (
            sample.sample_id,
            sample.source_id,
            _date_value(sample.sample_date),
            float(sample.ph),
            float(sample.ec),
            _enum_value(sample.ec_unit),
            float(sample.tds),
            _enum_value(sample.tds_unit),
            float(sample.sar),
            _ions_json(sample.ions),
        )
        if connection is not None:
            connection.execute(query, params)
            return
        with self.database.transaction() as conn:
            conn.execute(query, params)

    def get(self, sample_id: str) -> WaterSample | None:
        with self.database.connect() as conn:
            row = conn.execute(
                """
                SELECT s.*, ws.source_name, ws.source_type, ws.sub_basin, ws.river
                FROM samples s
                LEFT JOIN water_sources ws ON ws.source_id = s.source_id
                WHERE s.sample_id = ?
                """,
                (sample_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def list_all(self, *, limit: int | None = None, offset: int = 0) -> list[WaterSample]:
        sql = """
        SELECT s.*, ws.source_name, ws.source_type, ws.sub_basin, ws.river
        FROM samples s
        LEFT JOIN water_sources ws ON ws.source_id = s.source_id
        ORDER BY COALESCE(s.sample_date, ''), s.sample_id
        """
        params: tuple[Any, ...] = ()
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params = (limit, offset)
        with self.database.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._from_row(row) for row in rows]

    def list_by_source(self, source_id: str) -> list[WaterSample]:
        with self.database.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*, ws.source_name, ws.source_type, ws.sub_basin, ws.river
                FROM samples s
                LEFT JOIN water_sources ws ON ws.source_id = s.source_id
                WHERE s.source_id = ?
                ORDER BY COALESCE(s.sample_date, ''), s.sample_id
                """,
                (source_id,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def count(self) -> int:
        with self.database.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0])

    def delete(self, sample_id: str) -> bool:
        with self.database.transaction() as conn:
            cursor = conn.execute("DELETE FROM samples WHERE sample_id = ?", (sample_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _from_row(row: sqlite3.Row) -> WaterSample:
        return WaterSample(
            sample_id=row["sample_id"],
            source_id=row["source_id"],
            source_name=row["source_name"],
            source_type=row["source_type"],
            sub_basin=row["sub_basin"],
            river=row["river"],
            sample_date=row["sample_date"],
            ph=row["ph"],
            ec=row["ec_value"],
            ec_unit=row["ec_unit"],
            tds=row["tds_value"],
            tds_unit=row["tds_unit"],
            sar=row["sar"],
            ions=_ions_from_json(row["ions_json"]),
        )


class AnalysisResultRepository(_Repository):
    def upsert(
        self,
        result: AnalysisResult,
        *,
        engine_version: str,
        standard_profile: str,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        scientific = asdict(result.scientific)
        for key, value in list(scientific.items()):
            if isinstance(value, Enum):
                scientific[key] = value.value

        query = """
        INSERT INTO analysis_results(
            sample_id, engine_version, standard_profile,
            ph_code, ph_level, ec_code, ec_level, tds_code, tds_level,
            sar_code, sar_level, infiltration_code, infiltration_level,
            overall_status, overall_color, warnings_json, scientific_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(sample_id, engine_version, standard_profile) DO UPDATE SET
            analyzed_at = CURRENT_TIMESTAMP,
            ph_code = excluded.ph_code,
            ph_level = excluded.ph_level,
            ec_code = excluded.ec_code,
            ec_level = excluded.ec_level,
            tds_code = excluded.tds_code,
            tds_level = excluded.tds_level,
            sar_code = excluded.sar_code,
            sar_level = excluded.sar_level,
            infiltration_code = excluded.infiltration_code,
            infiltration_level = excluded.infiltration_level,
            overall_status = excluded.overall_status,
            overall_color = excluded.overall_color,
            warnings_json = excluded.warnings_json,
            scientific_json = excluded.scientific_json
        """
        params = (
            result.sample.sample_id,
            engine_version,
            standard_profile,
            result.ph.code,
            result.ph.level.value,
            result.ec.code,
            result.ec.level.value,
            result.tds.code,
            result.tds.level.value,
            result.sar.code,
            result.sar.level.value,
            result.infiltration.code,
            result.infiltration.level.value,
            result.overall.status.value,
            result.overall.color_key,
            json.dumps(result.warnings, ensure_ascii=False),
            json.dumps(scientific, ensure_ascii=False),
        )
        if connection is not None:
            connection.execute(query, params)
            return
        with self.database.transaction() as conn:
            conn.execute(query, params)

    def get_latest(self, sample_id: str) -> StoredAnalysis | None:
        with self.database.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM analysis_results
                WHERE sample_id = ?
                ORDER BY analyzed_at DESC, id DESC
                LIMIT 1
                """,
                (sample_id,),
            ).fetchone()
        if row is None:
            return None
        return StoredAnalysis(
            sample_id=row["sample_id"],
            engine_version=row["engine_version"],
            standard_profile=row["standard_profile"],
            analyzed_at=row["analyzed_at"],
            ph_code=row["ph_code"],
            ec_code=row["ec_code"],
            tds_code=row["tds_code"],
            sar_code=row["sar_code"],
            infiltration_code=row["infiltration_code"],
            overall_status=row["overall_status"],
            overall_color=row["overall_color"],
            warnings=tuple(json.loads(row["warnings_json"])),
            scientific=json.loads(row["scientific_json"]),
        )

    def count(self) -> int:
        with self.database.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0])
