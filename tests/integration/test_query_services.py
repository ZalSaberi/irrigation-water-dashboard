from __future__ import annotations

from pathlib import Path

from aqualog.data.database import SQLiteDatabase
from aqualog.services.analysis_service import AnalysisService
from aqualog.services.archive_query_service import ArchiveFilters, ArchiveQueryService
from aqualog.services.dashboard_query_service import DashboardFilters, DashboardQueryService
from aqualog.services.import_service import ImportService


FIXTURE = Path("data/fixtures/rfp/rfp_input_20_sources.csv")


def _seed(tmp_path):
    db = SQLiteDatabase(tmp_path / "query.sqlite3")
    db.initialize()
    analysis = AnalysisService(db)
    report = ImportService(analysis).import_and_analyze(FIXTURE)
    assert report.successful_rows == 300
    return db


def test_dashboard_snapshot_matches_fixture_counts(tmp_path):
    db = _seed(tmp_path)
    service = DashboardQueryService(db)
    snap = service.get_snapshot()
    assert snap.total_samples == 300
    assert snap.source_count == 20
    assert (snap.suitable_count, snap.caution_count, snap.unsuitable_count) == (77, 141, 82)
    assert snap.attention_count == 223
    assert len(snap.recent_samples) == 5
    assert len(snap.trend_points) == 300


def test_dashboard_filters_status_and_source(tmp_path):
    db = _seed(tmp_path)
    service = DashboardQueryService(db)
    caution = service.get_snapshot(DashboardFilters(status="caution"))
    assert caution.total_samples == 141
    assert caution.caution_count == 141
    source_id = service.list_sources()[0][0]
    source = service.get_snapshot(DashboardFilters(source_id=source_id))
    assert source.total_samples > 0
    assert source.source_count == 1


def test_archive_search_and_status_filter(tmp_path):
    db = _seed(tmp_path)
    service = ArchiveQueryService(db)
    page = service.list_samples(ArchiveFilters(status="unsuitable", limit=1000))
    assert page.total_count == 82
    assert len(page.rows) == 82
    sample = service.get_sample(page.rows[0].sample_id)
    assert sample is not None
