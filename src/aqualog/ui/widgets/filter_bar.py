from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDateEdit, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from aqualog.ui.services_types import DashboardFilterState


class FilterComboBox(QComboBox):
    """
    ComboBox مخصوص فیلترهای داشبورد.

    در تم Dark و RTL، indicator پیش‌فرض Qt ممکن است
    به دلیل QSS دیده نشود. این کلاس یک chevron واقعی
    و همیشه قابل مشاهده در سمت چپ ComboBox قرار می‌دهد.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._chevron = QLabel("▾", self)

        self._chevron.setObjectName(
            "FilterComboChevron"
        )

        self._chevron.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # کلیک روی فلش باید به خود ComboBox برسد
        self._chevron.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self._chevron.setFixedSize(20, 20)

        self._chevron.setStyleSheet("""
            QLabel#FilterComboChevron {
                background: transparent;
                border: none;

                color: #8EA5BA;

                font-family:
                    "Segoe UI Symbol",
                    "Segoe UI";

                font-size: 15px;
                font-weight: 700;
            }
        """)

        self._chevron.raise_()

    def setEditable(self, editable: bool) -> None:
        """
        حتی وقتی ComboBox برای وسط‌چین کردن متن editable است،
        کلیک روی LineEdit باید Popup را باز کند.
        """
        super().setEditable(editable)

        if editable and self.lineEdit() is not None:
            self.lineEdit().setReadOnly(True)

            # کلیک روی بخش متن را خودمان مدیریت می‌کنیم.
            self.lineEdit().installEventFilter(self)

            # Cursor نیز نشان می‌دهد کل کنترل clickable است.
            self.lineEdit().setCursor(
                Qt.CursorShape.PointingHandCursor
            )

    def eventFilter(self, watched, event):
        """
        کلیک روی قسمت متنی QComboBox نیز Popup را باز می‌کند.
        """
        if (
            self.lineEdit() is not None
            and watched is self.lineEdit()
            and event.type()
            == QEvent.Type.MouseButtonPress
        ):
            if (
                event.button()
                == Qt.MouseButton.LeftButton
            ):
                self.showPopup()
                return True

        return super().eventFilter(
            watched,
            event
        )

    def mousePressEvent(self, event):
        """
        کلیک روی هر نقطه از خود ComboBox = باز شدن منو.
        """
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.showPopup()
            event.accept()
            return

        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # RTL:
        # indicator در سمت چپ ComboBox
        x = 9
        y = (
            self.height()
            - self._chevron.height()
        ) // 2

        self._chevron.move(x, y)

    def enterEvent(self, event):
        self._chevron.setStyleSheet("""
            QLabel#FilterComboChevron {
                background: transparent;
                border: none;

                color: #2DD4BF;

                font-family:
                    "Segoe UI Symbol",
                    "Segoe UI";

                font-size: 15px;
                font-weight: 700;
            }
        """)

        super().enterEvent(event)

    def leaveEvent(self, event):
        self._chevron.setStyleSheet("""
            QLabel#FilterComboChevron {
                background: transparent;
                border: none;

                color: #8EA5BA;

                font-family:
                    "Segoe UI Symbol",
                    "Segoe UI";

                font-size: 15px;
                font-weight: 700;
            }
        """)

        super().leaveEvent(event)


class DashboardFilterBar(QWidget):
    filters_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.clear = QPushButton("پاک کردن فیلترها")
        self.clear.setProperty("variant", "ghost")

        self.source = self._combo("همه منابع", None)
        self.date_preset = self._combo("همه بازه‌ها", None)
        self.status = self._combo("همه وضعیت‌ها", None)

        self.date_preset.addItem("۱۲ ماه آخر داده‌ها", "12m")
        self.date_preset.addItem("۶ ماه آخر داده‌ها", "6m")
        self.date_preset.addItem("بازه سفارشی", "custom")

        self.status.addItem("مناسب", "suitable")
        self.status.addItem("نیازمند احتیاط", "caution")
        self.status.addItem("نامناسب", "unsuitable")

        self.source_wrap = QWidget()
        row = QHBoxLayout(self.source_wrap)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self.status)
        row.addWidget(self.date_preset)
        row.addWidget(self.source)

        self.date_from = self._date_edit()
        self.date_to = self._date_edit()
        self.date_row = QWidget()
        drow = QHBoxLayout(self.date_row)
        drow.setContentsMargins(0, 6, 0, 0)
        drow.setSpacing(10)
        drow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drow.addWidget(self.date_to)
        drow.addWidget(self.date_from)
        self.date_row.setVisible(False)

        group = QVBoxLayout()
        group.setContentsMargins(0, 0, 0, 0)
        group.setSpacing(0)
        group.addWidget(self.source_wrap, 0, Qt.AlignmentFlag.AlignCenter)
        group.addWidget(self.date_row, 0, Qt.AlignmentFlag.AlignCenter)

        root.addWidget(self.clear, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        root.addStretch(1)
        root.addLayout(group, 0)
        root.addStretch(1)

        self.source.currentIndexChanged.connect(self.filters_changed)
        self.status.currentIndexChanged.connect(self.filters_changed)
        self.date_preset.currentIndexChanged.connect(self._preset_changed)
        self.date_from.dateChanged.connect(self.filters_changed)
        self.date_to.dateChanged.connect(self.filters_changed)
        self.clear.clicked.connect(self.reset)

    def _combo(self, text: str, data):
        combo = FilterComboBox()
        combo.setMinimumWidth(150)
        combo.setMaximumWidth(170)
        combo.setEditable(True)
        combo.lineEdit().setReadOnly(True)
        combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        combo.lineEdit().setCursorPosition(0)
        combo.addItem(text, data)
        return combo

    def _date_edit(self):
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("yyyy-MM-dd")
        edit.setVisible(False)
        edit.setMinimumWidth(140)
        edit.setMaximumWidth(150)
        return edit

    def set_sources(self, sources: list[tuple[str, str]]) -> None:
        current = self.source.currentData()
        self.source.blockSignals(True)
        self.source.clear()
        self.source.addItem("همه منابع", None)
        for source_id, label in sources:
            self.source.addItem(label if label != source_id else source_id, source_id)
        index = self.source.findData(current)
        self.source.setCurrentIndex(max(0, index))
        self.source.lineEdit().setCursorPosition(0)
        self.source.blockSignals(False)

    def _preset_changed(self) -> None:
        custom = self.date_preset.currentData() == "custom"
        self.date_row.setVisible(custom)
        self.date_from.setVisible(custom)
        self.date_to.setVisible(custom)
        self.filters_changed.emit()

    def reset(self) -> None:
        for combo in (self.source, self.date_preset, self.status):
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.lineEdit().setCursorPosition(0)
            combo.blockSignals(False)
        self.date_row.setVisible(False)
        self.date_from.setVisible(False)
        self.date_to.setVisible(False)
        self.filters_changed.emit()

    def state(self) -> DashboardFilterState:
        custom = self.date_preset.currentData() == "custom"
        return DashboardFilterState(
            source_id=self.source.currentData(),
            status=self.status.currentData(),
            date_preset=self.date_preset.currentData() if not custom else None,
            date_from=self.date_from.date().toPyDate() if custom else None,
            date_to=self.date_to.date().toPyDate() if custom else None,
        )
