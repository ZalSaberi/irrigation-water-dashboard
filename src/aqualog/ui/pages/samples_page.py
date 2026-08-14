from __future__ import annotations
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QSizePolicy, QStackedWidget, QTableView, QVBoxLayout, QWidget
from aqualog.services.archive_query_service import ArchiveFilters, ArchiveQueryService
from aqualog.ui.models import ArchiveSamplesTableModel, StatusPillDelegate
from aqualog.ui.widgets import Card, StatePanel
from aqualog.ui.widgets.filter_bar import FilterComboBox

class SamplesPage(QWidget):
    sample_detail_requested=pyqtSignal(str); toast_requested=pyqtSignal(str,str)
    def __init__(self,service:ArchiveQueryService,parent=None): super().__init__(parent); self.service=service; self._build()
    def _build(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(12)
        bar=QHBoxLayout(); bar.setDirection(QHBoxLayout.Direction.RightToLeft); bar.setSpacing(8); self.search=QLineEdit(); self.search.setPlaceholderText("جستجو بر اساس شناسه یا منبع…"); self.search.setMinimumWidth(240); self.source=FilterComboBox(); self.source.addItem("همه منابع",None); self.status=FilterComboBox(); self.status.addItem("همه وضعیت‌ها",None); self.status.addItem("مناسب","suitable"); self.status.addItem("نیازمند احتیاط","caution"); self.status.addItem("نامناسب","unsuitable"); self.use_dates=QCheckBox("بازه تاریخ"); self.date_from=QDateEdit(QDate.currentDate().addYears(-1)); self.date_to=QDateEdit(QDate.currentDate());
        for d in (self.date_from,self.date_to): d.setCalendarPopup(True); d.setDisplayFormat("yyyy-MM-dd"); d.setVisible(False)
        clear=QPushButton("پاک کردن فیلترها"); clear.setProperty("variant","ghost"); clear.clicked.connect(self.reset_filters); bar.addWidget(self.search,1); bar.addWidget(self.source); bar.addWidget(self.status); bar.addWidget(self.use_dates); bar.addWidget(self.date_from); bar.addWidget(self.date_to); bar.addWidget(clear); root.addLayout(bar)
        self.stack=QStackedWidget(); root.addWidget(self.stack,1); card=Card(); cb=QVBoxLayout(card); cb.setContentsMargins(16,14,16,14); head_widget=QWidget(); head_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight); head=QHBoxLayout(head_widget); head.setContentsMargins(0,0,0,0); title=QLabel("آرشیو نمونه‌ها"); title.setObjectName("SectionTitle"); title.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred); title.setLayoutDirection(Qt.LayoutDirection.RightToLeft); title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter); self.count=QLabel(""); self.count.setObjectName("Muted"); head.addWidget(self.count); head.addStretch(1); head.addWidget(title); cb.addWidget(head_widget); self.model=ArchiveSamplesTableModel(self); self.table=QTableView(); self.table.setModel(self.model); self.table.setAlternatingRowColors(True); self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection); self.table.verticalHeader().hide(); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.table.setItemDelegateForColumn(8,StatusPillDelegate(self.table)); self.table.doubleClicked.connect(self._double_click); cb.addWidget(self.table,1); self.stack.addWidget(card)
        empty=StatePanel("نتیجه‌ای پیدا نشد","نمونه‌ای با فیلترهای فعلی وجود ندارد.",icon_name="fa5s.search",action_text="پاک کردن فیلترها"); empty.action_clicked.connect(self.reset_filters); self.stack.addWidget(empty); self.error=StatePanel("دریافت آرشیو انجام نشد","در خواندن داده‌ها مشکلی رخ داده است.",icon_name="fa5s.exclamation-triangle",action_text="تلاش مجدد"); self.error.action_clicked.connect(self.refresh); self.stack.addWidget(self.error)
        self.search.returnPressed.connect(self.refresh); self.source.currentIndexChanged.connect(self.refresh); self.status.currentIndexChanged.connect(self.refresh); self.use_dates.toggled.connect(self._toggle_dates); self.date_from.dateChanged.connect(self.refresh); self.date_to.dateChanged.connect(self.refresh)
    def _toggle_dates(self,on): self.date_from.setVisible(on); self.date_to.setVisible(on); self.refresh()
    def _filters(self): return ArchiveFilters(search=self.search.text().strip() or None,source_id=self.source.currentData(),status=self.status.currentData(),date_from=self.date_from.date().toPyDate() if self.use_dates.isChecked() else None,date_to=self.date_to.date().toPyDate() if self.use_dates.isChecked() else None,limit=1000)
    def refresh(self):
        try:
            current=self.source.currentData(); sources=self.service.list_sources(); self.source.blockSignals(True); self.source.clear(); self.source.addItem("همه منابع",None); [self.source.addItem(label if label!=sid else sid,sid) for sid,label in sources]; idx=self.source.findData(current); self.source.setCurrentIndex(max(0,idx)); self.source.blockSignals(False); data=self.service.list_samples(self._filters()); self.model.set_rows(data.rows); self.count.setText(f"{data.total_count} نمونه"); self.stack.setCurrentIndex(0 if data.total_count else 1)
        except Exception as exc: self.stack.setCurrentWidget(self.error); self.toast_requested.emit(f"خطا در آرشیو: {exc}","error")
    def reset_filters(self): self.search.clear(); self.source.setCurrentIndex(0); self.status.setCurrentIndex(0); self.use_dates.setChecked(False); self.refresh()
    def _double_click(self,index):
        sid=self.model.sample_id_at(index.row());
        if sid:self.sample_detail_requested.emit(sid)
