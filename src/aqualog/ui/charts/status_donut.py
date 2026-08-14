from __future__ import annotations
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget
from aqualog.ui.theme.tokens import Colors

class StatusDonutChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.values = (0, 0, 0)
        self.center_label = 'کل تحلیل\u200cها'

    def set_counts(self, suitable: int, caution: int, unsuitable: int) -> None:
        self.values = (max(0, suitable), max(0, caution), max(0, unsuitable))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        size = side * 0.67
        rect = QRectF((self.width() - size) / 2, (self.height() - size) / 2, size, size)
        width = max(14.0, size * 0.1)
        painter.setPen(QPen(QColor(Colors.SURFACE_3), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 0, 360 * 16)
        total = sum(self.values)
        start = 90 * 16
        gap = int(2.2 * 16)
        if total:
            for value, color in zip(self.values, (Colors.SUCCESS, Colors.CAUTION, Colors.DANGER)):
                if value <= 0:
                    continue
                span = int(value / total * 360 * 16)
                painter.setPen(QPen(QColor(color), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                painter.drawArc(rect, start, -max(0, span - gap))
                start -= span
        center = rect.center()
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        f = QFont(self.font())
        f.setPointSize(19)
        f.setBold(True)
        painter.setFont(f)
        painter.drawText(QRectF(center.x() - 70, center.y() - 27, 140, 34), Qt.AlignmentFlag.AlignCenter, str(total))
        painter.setPen(QColor(Colors.TEXT_MUTED))
        f.setPointSize(9)
        f.setBold(False)
        painter.setFont(f)
        painter.drawText(QRectF(center.x() - 75, center.y() + 7, 150, 24), Qt.AlignmentFlag.AlignCenter, self.center_label)
