from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy
from aqualog.ui.theme.tokens import STATUS_APPEARANCES, STATUS_LABELS, Colors


class StatusPill(QLabel):
    def __init__(self, status: str = "unknown", text: str | None = None, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(30)
        self.setContentsMargins(12, 0, 12, 0)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.set_status(status, text)

    def set_status(self, status: str, text: str | None = None) -> None:
        key = str(status or "unknown").lower()
        appearance = STATUS_APPEARANCES.get(
            key,
            {
                "fg": Colors.TEXT_PRIMARY,
                "bg": Colors.SURFACE_3,
                "border": Colors.BORDER_DEFAULT,
            },
        )
        label = text or STATUS_LABELS.get(key, key)
        self.setText(label)
        self.setStyleSheet(
            f"color:{appearance['fg']}; background:{appearance['bg']}; border:1px solid {appearance['border']}; "
            "border-radius:9px; font-size:11px; font-weight:700; padding:3px 10px;"
        )
