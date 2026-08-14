from __future__ import annotations
import qtawesome as qta
from PyQt6.QtGui import QIcon
from .theme.tokens import Colors


def icon(name: str, color: str | None = None) -> QIcon:
    try:
        return qta.icon(name, color=color or Colors.TEXT_MUTED)
    except Exception:
        return QIcon()
