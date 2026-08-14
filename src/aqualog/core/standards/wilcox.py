from __future__ import annotations

from aqualog.domain.enums import WilcoxClass


def classify_sodium_percentage(value: float) -> WilcoxClass:
    if value < 0 or value > 100:
        raise ValueError("Sodium percentage must be between 0 and 100.")
    if value < 20:
        return WilcoxClass.EXCELLENT
    if value < 40:
        return WilcoxClass.GOOD
    if value < 60:
        return WilcoxClass.PERMISSIBLE
    if value < 80:
        return WilcoxClass.DOUBTFUL
    return WilcoxClass.UNSUITABLE
