from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable

from aqualog.data.importers import ImportIssue, TabularWaterSampleImporter
from aqualog.domain.models import AnalysisResult

from .analysis_service import AnalysisFailure, AnalysisService


@dataclass(frozen=True, slots=True)
class ImportAnalysisReport:
    file_path: Path
    total_rows: int
    imported_rows: int
    import_issues: tuple[ImportIssue, ...]
    analysis_results: tuple[AnalysisResult, ...]
    analysis_failures: tuple[AnalysisFailure, ...]

    @property
    def successful_rows(self) -> int:
        return len(self.analysis_results)

    @property
    def failed_rows(self) -> int:
        return len(self.import_issues) + len(self.analysis_failures)


class ImportService:
    def __init__(
        self,
        analysis_service: AnalysisService,
        *,
        importer: TabularWaterSampleImporter | None = None,
    ):
        self.analysis_service = analysis_service
        self.importer = importer or TabularWaterSampleImporter()

    def import_and_analyze(
        self,
        path: str | Path,
        *,
        persist: bool = True,
        continue_on_error: bool = True,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> ImportAnalysisReport:
        file_path = Path(path)
        imported = self.importer.load(
            file_path,
            continue_on_error=continue_on_error,
        )
        analyzed = self.analysis_service.analyze_many(
            imported.samples,
            persist=persist,
            continue_on_error=continue_on_error,
            progress_callback=progress_callback,
        )
        return ImportAnalysisReport(
            file_path=file_path,
            total_rows=imported.total_rows,
            imported_rows=imported.valid_rows,
            import_issues=imported.issues,
            analysis_results=analyzed.results,
            analysis_failures=analyzed.failures,
        )
