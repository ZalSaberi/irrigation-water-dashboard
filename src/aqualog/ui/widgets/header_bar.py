from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from aqualog.ui.icons import icon
from aqualog.ui.theme.tokens import Colors
from .status_pill import StatusPill


class HeaderBar(QFrame):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(88)

        # Keep physical widget ordering LTR while the Persian title itself remains RTL.
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        root = QHBoxLayout(self)
        root.setContentsMargins(6, 6, 0, 10)
        root.setSpacing(14)
        root.setDirection(QHBoxLayout.Direction.LeftToRight)

        # Operational controls stay on the physical left side of the header.
        actions_widget = QFrame()
        actions_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        actions = QHBoxLayout(actions_widget)
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.setDirection(QHBoxLayout.Direction.LeftToRight)

        self.refresh = QPushButton()
        self.refresh.setFixedSize(38, 38)
        self.refresh.setProperty("variant", "ghost")
        self.refresh.setIcon(icon("fa5s.sync-alt", Colors.TEXT_SECONDARY))
        self.refresh.setToolTip("بروزرسانی اطلاعات")
        self.refresh.clicked.connect(self.refresh_requested)

        self.updated = QLabel("آخرین بروزرسانی: —")
        self.updated.setObjectName("Muted")
        self.updated.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.updated.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.db_status = StatusPill("suitable", "دیتابیس متصل")
        self.db_status.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        actions.addWidget(self.refresh)
        actions.addWidget(self.updated)
        actions.addWidget(self.db_status)
        root.addWidget(actions_widget, 0)

        root.addStretch(1)

        self.hero_title = QLabel("پایش و تحلیل داده‌های کیفیت آب آبیاری")
        self.hero_title.setObjectName("HeroTitle")
        self.hero_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.hero_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        root.addWidget(self.hero_title, 0)

    def set_page(self, title: str, subtitle: str) -> None:
        # The header uses a fixed product descriptor across pages.
        return

    def set_database_ok(self, ok: bool) -> None:
        self.db_status.set_status(
            "suitable" if ok else "unsuitable",
            "دیتابیس متصل" if ok else "خطای دیتابیس",
        )

    def set_last_updated(self, value: str | None) -> None:
        if not value:
            self.updated.setText("آخرین بروزرسانی: —")
            return
        text = str(value)
        stamp = text[11:16] if len(text) >= 16 else text
        self.updated.setText(f"آخرین بروزرسانی: {stamp}")
