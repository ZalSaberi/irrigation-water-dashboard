from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from aqualog.core.validation import validate_sample
from aqualog.domain.models import IonProfile, WaterSample

from .errors import ImportRowError, ImportSchemaError, UnsupportedImportFormatError


@dataclass(frozen=True, slots=True)
class ImportIssue:
    row_number: int
    sample_id: str | None
    message: str


@dataclass(frozen=True, slots=True)
class ImportBatch:
    samples: tuple[WaterSample, ...]
    issues: tuple[ImportIssue, ...]
    total_rows: int

    @property
    def valid_rows(self) -> int:
        return len(self.samples)

    @property
    def failed_rows(self) -> int:
        return len(self.issues)


class TabularWaterSampleImporter:
    """Read RFP-style CSV/XLSX files and build validated WaterSample objects."""

    REQUIRED_COLUMNS = {
        "sample_id",
        "ph",
        "ec_value",
        "tds_value",
        "sar",
    }

    def load(self, path: str | Path, *, continue_on_error: bool = True) -> ImportBatch:
        path = Path(path)
        dataframe = self._read(path)
        dataframe.columns = [self._clean_column(c) for c in dataframe.columns]

        missing = sorted(self.REQUIRED_COLUMNS.difference(dataframe.columns))
        if missing:
            raise ImportSchemaError(
                "Missing required column(s): " + ", ".join(missing)
            )

        samples: list[WaterSample] = []
        issues: list[ImportIssue] = []
        seen_ids: set[str] = set()

        for zero_index, row in dataframe.iterrows():
            # User-facing row numbers include the header row.
            row_number = int(zero_index) + 2
            raw_sample_id = self._clean_value(row.get("sample_id"))
            sample_id = None if raw_sample_id is None else str(raw_sample_id).strip()
            try:
                sample = self._row_to_sample(row)
                if sample.sample_id in seen_ids:
                    raise ImportRowError(
                        f"Duplicate sample_id inside import file: {sample.sample_id}"
                    )
                validate_sample(sample)
                seen_ids.add(sample.sample_id)
                samples.append(sample)
            except Exception as exc:
                issue = ImportIssue(row_number, sample_id, str(exc))
                issues.append(issue)
                if not continue_on_error:
                    raise ImportRowError(
                        f"Import failed at row {row_number}: {exc}"
                    ) from exc

        return ImportBatch(tuple(samples), tuple(issues), len(dataframe))

    def _read(self, path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path, encoding="utf-8-sig")
        if suffix in {".xlsx", ".xlsm"}:
            return pd.read_excel(path, engine="openpyxl")
        raise UnsupportedImportFormatError(
            f"Unsupported import format {suffix!r}; use .csv, .xlsx or .xlsm"
        )

    @staticmethod
    def _clean_column(value: object) -> str:
        return str(value).replace("\ufeff", "").strip().lower()

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
        if isinstance(value, str):
            value = value.strip()
            return value if value else None
        return value

    @classmethod
    def _text(cls, value: Any) -> str | None:
        cleaned = cls._clean_value(value)
        return None if cleaned is None else str(cleaned).strip()

    @classmethod
    def _sample_date(cls, value: Any) -> date | str | None:
        value = cls._clean_value(value)
        if value is None:
            return None
        if isinstance(value, pd.Timestamp):
            return value.date()
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        text = str(value).strip()
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return text

    def _row_to_sample(self, row: pd.Series) -> WaterSample:
        ion_keys = {
            "ca_meq_l": "ca_meq_l",
            "mg_meq_l": "mg_meq_l",
            "na_meq_l": "na_meq_l",
            "k_meq_l": "k_meq_l",
            "co3_meq_l": "co3_meq_l",
            "hco3_meq_l": "hco3_meq_l",
            "cl_meq_l": "cl_meq_l",
            "so4_meq_l": "so4_meq_l",
            "no3_meq_l": "no3_meq_l",
        }
        ion_values = {
            target: self._clean_value(row.get(source))
            for source, target in ion_keys.items()
            if source in row.index
        }
        ions = IonProfile(**ion_values) if any(v is not None for v in ion_values.values()) else None

        sample_id = self._text(row.get("sample_id")) or ""
        return WaterSample(
            sample_id=sample_id,
            source_id=self._text(row.get("source_id")),
            source_name=self._text(row.get("source_name")),
            source_type=self._text(row.get("source_type")),
            sub_basin=self._text(row.get("sub_basin")),
            river=self._text(row.get("river")),
            sample_date=self._sample_date(row.get("sample_date")),
            ph=self._clean_value(row.get("ph")),
            ec=self._clean_value(row.get("ec_value")),
            ec_unit=self._text(row.get("ec_unit")) or "µS/cm",
            tds=self._clean_value(row.get("tds_value")),
            tds_unit=self._text(row.get("tds_unit")) or "mg/L",
            sar=self._clean_value(row.get("sar")),
            ions=ions,
        )
