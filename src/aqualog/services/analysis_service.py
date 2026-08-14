from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable

from aqualog.core.engine import IrrigationAnalysisEngine
from aqualog.data.database import SQLiteDatabase
from aqualog.data.repositories import (
    AnalysisResultRepository,
    WaterSampleRepository,
    WaterSourceRepository,
)
from aqualog.domain.models import AnalysisResult, WaterSample


@dataclass(frozen=True, slots=True)
class AnalysisFailure:
    sample_id: str
    message: str


@dataclass(frozen=True, slots=True)
class BatchAnalysisReport:
    results: tuple[AnalysisResult, ...]
    failures: tuple[AnalysisFailure, ...]

    @property
    def analyzed_count(self) -> int:
        return len(self.results)

    @property
    def failed_count(self) -> int:
        return len(self.failures)


class AnalysisService:
    """Application boundary between GUI/import code and the scientific engine."""

    def __init__(
        self,
        database: SQLiteDatabase,
        *,
        engine: IrrigationAnalysisEngine | None = None,
    ):
        self.database = database
        self.engine = engine or IrrigationAnalysisEngine()
        self.sources = WaterSourceRepository(database)
        self.samples = WaterSampleRepository(database)
        self.results = AnalysisResultRepository(database)

    def analyze(self, sample: WaterSample, *, persist: bool = True) -> AnalysisResult:
        result = self.engine.analyze(sample)
        if persist:
            with self.database.transaction() as connection:
                self.sources.upsert_from_sample(sample, connection=connection)
                self.samples.upsert(sample, connection=connection)
                self.results.upsert(
                    result,
                    engine_version=self.engine.VERSION,
                    standard_profile=self.engine.STANDARD_PROFILE,
                    connection=connection,
                )
        return result

    def analyze_many(
        self,
        samples: list[WaterSample] | tuple[WaterSample, ...],
        *,
        persist: bool = True,
        continue_on_error: bool = True,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> BatchAnalysisReport:
        results: list[AnalysisResult] = []
        failures: list[AnalysisFailure] = []
        total = len(samples)
        for index, sample in enumerate(samples, start=1):
            try:
                results.append(self.analyze(sample, persist=persist))
            except Exception as exc:
                failures.append(AnalysisFailure(sample.sample_id, str(exc)))
                if not continue_on_error:
                    raise
            finally:
                if progress_callback is not None:
                    progress_callback(index, total)
        return BatchAnalysisReport(tuple(results), tuple(failures))
