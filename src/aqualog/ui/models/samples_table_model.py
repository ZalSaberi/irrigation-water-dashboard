from __future__ import annotations
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget
from aqualog.services.archive_query_service import ArchiveSampleRow
from aqualog.services.dashboard_query_service import RecentSampleRow
from aqualog.ui.theme.tokens import Colors, STATUS_COLORS, STATUS_LABELS
STATUS_ROLE = int(Qt.ItemDataRole.UserRole) + 1

class RecentSamplesTableModel(QAbstractTableModel):
    headers = ('شناسه', 'منبع', 'تاریخ', 'EC', 'SAR', 'وضعیت')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows: tuple[RecentSampleRow, ...] = ()

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = tuple(rows)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        return self.headers[section] if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole else None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        r = self.rows[index.row()]
        c = index.column()
        if role == STATUS_ROLE and c == 5:
            return r.overall_status
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignCenter)
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        vals = (r.sample_id, r.source_label, r.date or '—', f'{r.ec_value:,.0f} {r.ec_unit}', f'{r.sar:.2f}', STATUS_LABELS.get(r.overall_status, r.overall_status))
        return vals[c]

    def sample_id_at(self, row: int) -> str | None:
        return self.rows[row].sample_id if 0 <= row < len(self.rows) else None

class ArchiveSamplesTableModel(QAbstractTableModel):
    headers = ('شناسه', 'منبع', 'نوع منبع', 'تاریخ', 'pH', 'EC', 'TDS', 'SAR', 'وضعیت')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows: tuple[ArchiveSampleRow, ...] = ()

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = tuple(rows)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        return self.headers[section] if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole else None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        r = self.rows[index.row()]
        c = index.column()
        if role == STATUS_ROLE and c == 8:
            return r.overall_status
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignCenter)
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        vals = (r.sample_id, r.source_label, r.source_type or '—', r.date or '—', f'{r.ph:.2f}', f'{r.ec_value:,.0f} {r.ec_unit}', f'{r.tds_value:,.0f} {r.tds_unit}', f'{r.sar:.2f}', STATUS_LABELS.get(r.overall_status, r.overall_status))
        return vals[c]

    def sample_id_at(self, row: int) -> str | None:
        return self.rows[row].sample_id if 0 <= row < len(self.rows) else None

class StatusPillDelegate(QStyledItemDelegate):

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        status = index.data(STATUS_ROLE)
        if not status:
            return super().paint(painter, option, index)
        color = QColor(STATUS_COLORS.get(status, Colors.REVIEW))
        text = STATUS_LABELS.get(status, status)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = option.rect.adjusted(12, 8, -12, -8)
        max_w = min(rect.width(), 118)
        x = rect.center().x() - max_w / 2
        pill = QRectF(x, rect.y(), max_w, rect.height())
        bg = QColor(color)
        bg.setAlpha(25)
        border = QColor(color)
        border.setAlpha(90)
        painter.setBrush(bg)
        painter.setPen(border)
        painter.drawRoundedRect(pill, 8, 8)
        painter.setPen(color)
        f = QFont(option.font)
        f.setPointSize(9)
        f.setBold(True)
        painter.setFont(f)
        painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(max(42, size.height()))
        return size
