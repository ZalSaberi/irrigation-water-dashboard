from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    code: str
    message_fa: str
    message_en: str


class WaterSampleValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = tuple(issues)
        message = "; ".join(f"{issue.field}: {issue.message_en}" for issue in issues)
        super().__init__(message)
