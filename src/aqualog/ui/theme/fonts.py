from __future__ import annotations

from pathlib import Path
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

_FONT_NAMES = (
    "SHABNAM.TTF",
    "SHABNAM-MEDIUM.TTF",
    "SHABNAM-BOLD.TTF",
    "SHABNAM-LIGHT.TTF",
)


def _candidate_dirs() -> list[Path]:
    here = Path(__file__).resolve()
    package = here.parents[2]
    cwd = Path.cwd()
    return [
        package / "resources" / "fonts",
        cwd / "src" / "aqualog" / "resources" / "fonts",
        cwd / "resources" / "fonts",
    ]


def load_application_fonts(app: QApplication) -> str:
    loaded_families: list[str] = []
    for directory in _candidate_dirs():
        if not directory.exists():
            continue
        for filename in _FONT_NAMES:
            path = directory / filename
            if not path.exists():
                continue
            font_id = QFontDatabase.addApplicationFont(str(path))
            if font_id >= 0:
                loaded_families.extend(QFontDatabase.applicationFontFamilies(font_id))
    family = next((f for f in loaded_families if "shabnam" in f.lower()), None)
    if not family:
        family = "Shabnam" if "Shabnam" in QFontDatabase.families() else "Segoe UI"
    app.setFont(QFont(family, 10))
    return family
