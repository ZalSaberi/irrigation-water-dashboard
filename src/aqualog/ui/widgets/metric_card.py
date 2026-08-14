from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from .card import Card
from aqualog.ui.icons import icon
from aqualog.ui.theme.tokens import Colors


class MetricCard(Card):
    def __init__(
        self,
        title: str,
        value: str = "—",
        *,
        subtitle: str = "",
        icon_name: str = "fa5s.layer-group",
        accent: str = Colors.ACCENT,
        parent=None,
    ):
        super().__init__(parent=parent)

        self.setMinimumHeight(78)
        self.setMaximumHeight(78)

        # IMPORTANT:
        # physical layout:
        #
        # LEFT                                 RIGHT
        # [NUMBER]       [TITLE/SUBTITLE] [ICON]
        #
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 9, 14, 9)
        root.setSpacing(10)
        root.setDirection(QHBoxLayout.Direction.LeftToRight)

        # ---------------- Number / physical LEFT ----------------
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("MetricValue")
        self.value_label.setFixedWidth(68)
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignAbsolute |
            Qt.AlignmentFlag.AlignVCenter
        )

        root.addWidget(
            self.value_label,
            0,
            Qt.AlignmentFlag.AlignVCenter
        )

        # فقط همین Stretch فضای کنترل‌شده ایجاد می‌کند
        root.addStretch(1)

        # ---------------- Text ----------------
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricLabel")
        self.title_label.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignAbsolute |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.title_label.setWordWrap(False)

        text_col.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("MetricSubtitle")
            self.subtitle_label.setLayoutDirection(
                Qt.LayoutDirection.RightToLeft
            )
            self.subtitle_label.setAlignment(
                Qt.AlignmentFlag.AlignRight |
                Qt.AlignmentFlag.AlignAbsolute |
                Qt.AlignmentFlag.AlignVCenter
            )
            self.subtitle_label.setWordWrap(False)

            text_col.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None

        root.addLayout(text_col)

        # ---------------- Icon / physical RIGHT ----------------
        self.icon_holder = QLabel()
        self.icon_holder.setObjectName("MetricIconHolder")
        self.icon_holder.setFixedSize(44, 44)
        self.icon_holder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.icon_holder.setPixmap(
            icon(
                icon_name,
                Colors.ACCENT_HOVER
            ).pixmap(QSize(22, 22))
        )

        root.addWidget(
            self.icon_holder,
            0,
            Qt.AlignmentFlag.AlignVCenter
        )

    def set_value(self, value: object) -> None:
        self.value_label.setText(str(value))
