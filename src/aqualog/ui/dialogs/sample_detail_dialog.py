from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout
from aqualog.domain.models import AnalysisResult
from aqualog.ui.theme.tokens import STATUS_LABELS
from aqualog.ui.widgets.card import Card
from aqualog.ui.widgets.status_pill import StatusPill

class SampleDetailDialog(QDialog):

    def __init__(self, result: AnalysisResult, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'جزئیات نمونه {result.sample.sample_id}')
        self.setMinimumSize(650, 560)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)
        top = QHBoxLayout()
        title = QLabel(f'نمونه {result.sample.sample_id}')
        title.setObjectName('PageTitle')
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(StatusPill(result.overall.status.value, result.overall.status_fa))
        root.addLayout(top)
        meta = Card(soft=True)
        grid = QGridLayout(meta)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(22)
        grid.setVerticalSpacing(8)
        fields = [('منبع', result.sample.source_id or '—'), ('تاریخ', str(result.sample.sample_date or '—')), ('استاندارد', result.ec.standard), ('نسخه موتور', '1.0.0')]
        for i, (k, v) in enumerate(fields):
            key = QLabel(k)
            key.setObjectName('Muted')
            val = QLabel(v)
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(key, i, 0)
            grid.addWidget(val, i, 1)
        root.addWidget(meta)
        results = Card()
        rg = QGridLayout(results)
        rg.setContentsMargins(16, 14, 16, 14)
        rg.setSpacing(12)
        items = [('pH', result.ph.value, result.ph.unit, result.ph.title_fa, result.ph.level.value), ('EC', result.ec.value, result.ec.unit, result.ec.title_fa, result.ec.level.value), ('TDS', result.tds.value, result.tds.unit, result.tds.title_fa, result.tds.level.value), ('SAR', result.sar.value, result.sar.unit, result.sar.title_fa, result.sar.level.value)]
        for i, (name, value, unit, title, status) in enumerate(items):
            box = Card(soft=True)
            b = QVBoxLayout(box)
            b.setContentsMargins(12, 10, 12, 10)
            b.setSpacing(3)
            n = QLabel(name)
            n.setObjectName('Muted')
            val = QLabel(f"{value:,.2f} {(unit if unit != '-' else '')}".strip())
            val.setStyleSheet('font-size:17px; font-weight:700;')
            desc = QLabel(title)
            desc.setWordWrap(True)
            desc.setObjectName('Muted')
            b.addWidget(n)
            b.addWidget(val)
            b.addWidget(StatusPill(status))
            b.addWidget(desc)
            rg.addWidget(box, i // 2, i % 2)
        root.addWidget(results)
        inf = Card(soft=True)
        ib = QVBoxLayout(inf)
        ib.setContentsMargins(14, 12, 14, 12)
        t = QLabel('ریسک نفوذپذیری خاک')
        t.setObjectName('SectionTitle')
        ib.addWidget(t)
        ib.addWidget(StatusPill(result.infiltration.level.value, result.infiltration.title_fa))
        if result.infiltration.note_fa:
            note = QLabel(result.infiltration.note_fa)
            note.setObjectName('Muted')
            note.setWordWrap(True)
            ib.addWidget(note)
        root.addWidget(inf)
        if result.warnings:
            warn = QLabel('\n'.join((f'• {w}' for w in result.warnings)))
            warn.setWordWrap(True)
            warn.setObjectName('Muted')
            root.addWidget(warn)
        root.addStretch(1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        root.addWidget(buttons)
