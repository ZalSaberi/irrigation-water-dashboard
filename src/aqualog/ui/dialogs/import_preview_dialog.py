from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout
from aqualog.data.importers import ImportBatch
from aqualog.ui.widgets.card import Card

class ImportPreviewDialog(QDialog):
    def __init__(self,batch:ImportBatch,file_name:str,parent=None):
        super().__init__(parent); self.setWindowTitle("پیش‌نمایش ورود داده"); self.setMinimumSize(760,560); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        root=QVBoxLayout(self); root.setContentsMargins(22,22,22,22); root.setSpacing(12)
        title=QLabel("پیش‌نمایش ورود داده"); title.setObjectName("PageTitle"); root.addWidget(title)
        sub=QLabel(file_name); sub.setObjectName("Muted"); sub.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); root.addWidget(sub)
        summary=Card(soft=True); sb=QHBoxLayout(summary); sb.setContentsMargins(14,10,14,10); sb.addWidget(QLabel(f"کل ردیف‌ها: {batch.total_rows}")); sb.addWidget(QLabel(f"معتبر: {batch.valid_rows}")); sb.addWidget(QLabel(f"نامعتبر: {batch.failed_rows}")); sb.addStretch(1); root.addWidget(summary)
        table=QTableWidget(); table.setColumnCount(6); table.setHorizontalHeaderLabels(["شناسه","منبع","تاریخ","pH","EC","SAR"]); preview=batch.samples[:10]; table.setRowCount(len(preview)); table.setAlternatingRowColors(True)
        for r,s in enumerate(preview):
            vals=[s.sample_id,s.source_id or "—",str(s.sample_date or "—"),str(s.ph),f"{s.ec} {s.ec_unit}",str(s.sar)]
            for c,v in enumerate(vals): item=QTableWidgetItem(v); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter); table.setItem(r,c,item)
        table.horizontalHeader().setStretchLastSection(True); root.addWidget(table,1)
        if batch.issues:
            issue_text="\n".join(f"ردیف {i.row_number}: {i.message}" for i in batch.issues[:8]); issues=QLabel(issue_text + ("\n…" if len(batch.issues)>8 else "")); issues.setObjectName("ErrorText"); issues.setWordWrap(True); root.addWidget(issues)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok); buttons.button(QDialogButtonBox.StandardButton.Ok).setText("تأیید و ورود"); buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف"); buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(batch.valid_rows>0); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); root.addWidget(buttons)
