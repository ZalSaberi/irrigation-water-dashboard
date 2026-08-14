from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from aqualog.data.database import SQLiteDatabase


@dataclass(frozen=True, slots=True)
class DashboardFilters:
    source_id: str | None = None
    status: str | None = None
    date_from: date | str | None = None
    date_to: date | str | None = None
    date_preset: str | None = None  # Supported values: None, "all", "6m", and "12m".
    parameter: str = "ec"


@dataclass(frozen=True, slots=True)
class TrendPoint:
    date: str
    value: float
    source_id: str | None
    sample_id: str


@dataclass(frozen=True, slots=True)
class RecentSampleRow:
    sample_id: str
    source_id: str | None
    source_label: str
    date: str | None
    ec_value: float
    ec_unit: str
    sar: float
    overall_status: str
    overall_color: str


@dataclass(frozen=True, slots=True)
class StatusDistribution:
    suitable: int = 0
    caution: int = 0
    unsuitable: int = 0

    @property
    def total(self) -> int:
        return self.suitable + self.caution + self.unsuitable


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    total_samples: int
    source_count: int
    suitable_count: int
    caution_count: int
    unsuitable_count: int
    attention_count: int
    latest_sample_date: str | None
    status_distribution: StatusDistribution
    trend_points: tuple[TrendPoint, ...]
    recent_samples: tuple[RecentSampleRow, ...]
    last_updated: str | None


class DashboardQueryService:
    """Build consistent dashboard read models from the persisted sample data."""

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

    @staticmethod
    def _date_text(value: date | str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return str(value)[:10]

    @classmethod
    def _where(cls, filters: DashboardFilters) -> tuple[str, list[object]]:
        conditions: list[str] = []
        params: list[object] = []
        if filters.source_id:
            conditions.append("s.source_id = ?")
            params.append(filters.source_id)
        if filters.status:
            conditions.append("la.overall_status = ?")
            params.append(filters.status)
        if filters.date_from:
            conditions.append("date(s.sample_date) >= date(?)")
            params.append(cls._date_text(filters.date_from))
        if filters.date_to:
            conditions.append("date(s.sample_date) <= date(?)")
            params.append(cls._date_text(filters.date_to))
        if not filters.date_from and filters.date_preset in {"6m", "12m"}:
            months = -6 if filters.date_preset == "6m" else -12
            conditions.append(
                "date(s.sample_date) >= date((SELECT MAX(sample_date) FROM samples), ?)"
            )
            params.append(f"{months} months")
        return (" AND ".join(conditions) if conditions else "1=1"), params

    def list_sources(self) -> list[tuple[str, str]]:
        with self.database.connect() as conn:
            rows = conn.execute(
                """
                SELECT source_id,
                       COALESCE(NULLIF(source_name, ''), NULLIF(river, ''), source_id) AS label
                FROM water_sources
                ORDER BY label COLLATE NOCASE, source_id
                """
            ).fetchall()
        return [(str(row["source_id"]), str(row["label"])) for row in rows]

    def get_snapshot(
        self,
        filters: DashboardFilters | None = None,
        *,
        recent_limit: int = 5,
        trend_limit: int = 600,
    ) -> DashboardSnapshot:
        filters = filters or DashboardFilters()
        where, params = self._where(filters)
        parameter = (filters.parameter or "ec").lower()
        expressions = {
            "ec": "CASE WHEN lower(s.ec_unit) IN ('µs/cm','us/cm','μs/cm') THEN s.ec_value / 1000.0 ELSE s.ec_value END",
            "tds": "s.tds_value",
            "sar": "s.sar",
            "ph": "s.ph",
        }
        if parameter not in expressions:
            parameter = "ec"
        expr = expressions[parameter]

        base_from = """
        FROM samples s
        LEFT JOIN water_sources ws ON ws.source_id = s.source_id
        LEFT JOIN latest_analysis la ON la.sample_id = s.sample_id
        """

        with self.database.connect() as conn:
            counts = conn.execute(
                self.LATEST_ANALYSIS_CTE
                + f"""
                SELECT COUNT(*) AS total,
                       COUNT(DISTINCT CASE WHEN s.source_id IS NOT NULL THEN s.source_id END) AS sources,
                       SUM(CASE WHEN la.overall_status='suitable' THEN 1 ELSE 0 END) AS suitable,
                       SUM(CASE WHEN la.overall_status='caution' THEN 1 ELSE 0 END) AS caution,
                       SUM(CASE WHEN la.overall_status='unsuitable' THEN 1 ELSE 0 END) AS unsuitable,
                       MAX(s.sample_date) AS latest_sample_date
                {base_from}
                WHERE {where}
                """,
                params,
            ).fetchone()

            trend_rows = conn.execute(
                self.LATEST_ANALYSIS_CTE
                + f"""
                SELECT s.sample_id, s.source_id, s.sample_date, {expr} AS value
                {base_from}
                WHERE {where} AND s.sample_date IS NOT NULL
                ORDER BY date(s.sample_date), s.sample_id
                LIMIT ?
                """,
                [*params, trend_limit],
            ).fetchall()

            recent_rows = conn.execute(
                self.LATEST_ANALYSIS_CTE
                + f"""
                SELECT s.sample_id, s.source_id, s.sample_date, s.ec_value, s.ec_unit, s.sar,
                       COALESCE(NULLIF(ws.source_name, ''), NULLIF(ws.river, ''), s.source_id, '—') AS source_label,
                       COALESCE(la.overall_status, 'unknown') AS overall_status,
                       COALESCE(la.overall_color, 'gray') AS overall_color
                {base_from}
                WHERE {where}
                ORDER BY date(s.sample_date) DESC, s.sample_id DESC
                LIMIT ?
                """,
                [*params, recent_limit],
            ).fetchall()

            last_updated = conn.execute(
                "SELECT MAX(analyzed_at) FROM analysis_results"
            ).fetchone()[0]

        suitable = int(counts["suitable"] or 0)
        caution = int(counts["caution"] or 0)
        unsuitable = int(counts["unsuitable"] or 0)
        distribution = StatusDistribution(suitable, caution, unsuitable)
        trend = tuple(
            TrendPoint(
                date=str(row["sample_date"]),
                value=float(row["value"]),
                source_id=row["source_id"],
                sample_id=str(row["sample_id"]),
            )
            for row in trend_rows
            if row["value"] is not None
        )
        recent = tuple(
            RecentSampleRow(
                sample_id=str(row["sample_id"]),
                source_id=row["source_id"],
                source_label=str(row["source_label"]),
                date=row["sample_date"],
                ec_value=float(row["ec_value"]),
                ec_unit=str(row["ec_unit"]),
                sar=float(row["sar"]),
                overall_status=str(row["overall_status"]),
                overall_color=str(row["overall_color"]),
            )
            for row in recent_rows
        )
        return DashboardSnapshot(
            total_samples=int(counts["total"] or 0),
            source_count=int(counts["sources"] or 0),
            suitable_count=suitable,
            caution_count=caution,
            unsuitable_count=unsuitable,
            attention_count=caution + unsuitable,
            latest_sample_date=counts["latest_sample_date"],
            status_distribution=distribution,
            trend_points=trend,
            recent_samples=recent,
            last_updated=last_updated,
        )
