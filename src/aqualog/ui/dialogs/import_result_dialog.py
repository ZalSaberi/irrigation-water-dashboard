from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from aqualog.services.import_service import ImportAnalysisReport
from aqualog.ui.widgets.card import Card

class ImportResultDialog(QDialog):
    def __init__(self,report:ImportAnalysisReport,parent=None):
        super().__init__(parent); self.setWindowTitle("نتیجه ورود داده"); self.setMinimumWidth(520); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        root=QVBoxLayout(self); root.setContentsMargins(22,22,22,22); root.setSpacing(12)
        title=QLabel("ورود داده تکمیل شد"); title.setObjectName("PageTitle"); root.addWidget(title)
        card=Card(soft=True); b=QVBoxLayout(card); b.setContentsMargins(16,14,16,14); b.addWidget(QLabel(f"کل ردیف‌ها: {report.total_rows}")); b.addWidget(QLabel(f"تحلیل و ذخیره موفق: {report.successful_rows}")); b.addWidget(QLabel(f"ناموفق: {report.failed_rows}")); root.addWidget(card)
        messages=[]
        messages += [f"ردیف {i.row_number}: {i.message}" for i in report.import_issues[:8]]
        messages += [f"{i.sample_id}: {i.message}" for i in report.analysis_failures[:8]]
        if messages:
            label=QLabel("\n".join(messages)+("\n…" if report.failed_rows>len(messages) else "")); label.setObjectName("ErrorText"); label.setWordWrap(True); root.addWidget(label)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(self.reject); buttons.accepted.connect(self.accept); root.addWidget(buttons)
