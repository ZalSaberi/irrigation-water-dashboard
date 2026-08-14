from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from aqualog.data.database import SQLiteDatabase
from aqualog.data.repositories import WaterSampleRepository
from aqualog.domain.models import WaterSample


@dataclass(frozen=True, slots=True)
class ArchiveFilters:
    search: str | None = None
    source_id: str | None = None
    status: str | None = None
    date_from: date | str | None = None
    date_to: date | str | None = None
    limit: int = 500
    offset: int = 0


@dataclass(frozen=True, slots=True)
class ArchiveSampleRow:
    sample_id: str
    source_id: str | None
    source_label: str
    source_type: str | None
    date: str | None
    ph: float
    ec_value: float
    ec_unit: str
    tds_value: float
    tds_unit: str
    sar: float
    overall_status: str
    overall_color: str


@dataclass(frozen=True, slots=True)
class ArchivePageData:
    rows: tuple[ArchiveSampleRow, ...]
    total_count: int


class ArchiveQueryService:
    LATEST_ANALYSIS_CTE = """
    WITH latest_analysis AS (
        SELECT * FROM (
            SELECT ar.*,
                   ROW_NUMBER() OVER (
                       PARTITION BY ar.sample_id
                       ORDER BY datetime(ar.analyzed_at) DESC, ar.id DESC
                   ) AS rn
            FROM analysis_results ar
        ) ranked
        WHERE rn = 1
    )
    """

    def __init__(self, database: SQLiteDatabase):
        self.database = database
        self.samples = WaterSampleRepository(database)

    @staticmethod
    def _date_text(value: date | str | None) -> str | None:
        if value is None:
            return None
        return value.isoformat() if isinstance(value, date) else str(value)[:10]

    @classmethod
    def _where(cls, f: ArchiveFilters) -> tuple[str, list[object]]:
        conditions: list[str] = []
        params: list[object] = []
        if f.search and f.search.strip():
            needle = f"%{f.search.strip()}%"
            conditions.append(
                "(s.sample_id LIKE ? OR s.source_id LIKE ? OR ws.source_name LIKE ? OR ws.river LIKE ?)"
            )
            params.extend([needle, needle, needle, needle])
        if f.source_id:
            conditions.append("s.source_id = ?")
            params.append(f.source_id)
        if f.status:
            conditions.append("la.overall_status = ?")
            params.append(f.status)
        if f.date_from:
            conditions.append("date(s.sample_date) >= date(?)")
            params.append(cls._date_text(f.date_from))
        if f.date_to:
            conditions.append("date(s.sample_date) <= date(?)")
            params.append(cls._date_text(f.date_to))
        return (" AND ".join(conditions) if conditions else "1=1"), params

    def list_sources(self) -> list[tuple[str, str]]:
        with self.database.connect() as conn:
            rows = conn.execute(
                """
                SELECT source_id, COALESCE(NULLIF(source_name,''), NULLIF(river,''), source_id) label
                FROM water_sources ORDER BY label COLLATE NOCASE
                """
            ).fetchall()
        return [(str(r["source_id"]), str(r["label"])) for r in rows]

    def list_samples(self, filters: ArchiveFilters | None = None) -> ArchivePageData:
        f = filters or ArchiveFilters()
        where, params = self._where(f)
        base = """
        FROM samples s
        LEFT JOIN water_sources ws ON ws.source_id = s.source_id
        LEFT JOIN latest_analysis la ON la.sample_id = s.sample_id
        """
        with self.database.connect() as conn:
            total = int(
                conn.execute(
                    self.LATEST_ANALYSIS_CTE + f"SELECT COUNT(*) {base} WHERE {where}",
                    params,
                ).fetchone()[0]
            )
            rows = conn.execute(
                self.LATEST_ANALYSIS_CTE
                + f"""
                SELECT s.sample_id, s.source_id, s.sample_date, s.ph, s.ec_value, s.ec_unit,
                       s.tds_value, s.tds_unit, s.sar, ws.source_type,
                       COALESCE(NULLIF(ws.source_name,''), NULLIF(ws.river,''), s.source_id, '—') source_label,
                       COALESCE(la.overall_status,'unknown') overall_status,
                       COALESCE(la.overall_color,'gray') overall_color
                {base}
                WHERE {where}
                ORDER BY date(s.sample_date) DESC, s.sample_id DESC
                LIMIT ? OFFSET ?
                """,
                [*params, max(1, f.limit), max(0, f.offset)],
            ).fetchall()
        return ArchivePageData(
            rows=tuple(
                ArchiveSampleRow(
                    sample_id=str(r["sample_id"]), source_id=r["source_id"],
                    source_label=str(r["source_label"]), source_type=r["source_type"],
                    date=r["sample_date"], ph=float(r["ph"]), ec_value=float(r["ec_value"]),
                    ec_unit=str(r["ec_unit"]), tds_value=float(r["tds_value"]),
                    tds_unit=str(r["tds_unit"]), sar=float(r["sar"]),
                    overall_status=str(r["overall_status"]), overall_color=str(r["overall_color"]),
                ) for r in rows
            ),
            total_count=total,
        )

    def get_sample(self, sample_id: str) -> WaterSample | None:
        return self.samples.get(sample_id)
