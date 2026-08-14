from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import uuid4

from PyQt6.QtCore import QDate, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from aqualog.data.importers import TabularWaterSampleImporter
from aqualog.domain.errors import WaterSampleValidationError
from aqualog.domain.models import AnalysisResult, WaterSample
from aqualog.services.analysis_service import AnalysisService
from aqualog.services.import_service import ImportService
from aqualog.ui.dialogs import ImportPreviewDialog, ImportResultDialog
from aqualog.ui.widgets import Card, StatePanel, StatusPill
from aqualog.ui.workers import FunctionWorker


class ParameterResultCard(Card):
    def __init__(self, name, parent=None):
        super().__init__(soft=True, parent=parent)
        body = QVBoxLayout(self)
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(4)

        self.name = QLabel(name)
        self.name.setObjectName('Muted')
        self.name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignVCenter)

        self.value = QLabel('—')
        self.value.setStyleSheet('font-size:18px;font-weight:700;')
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignVCenter)

        self.pill = StatusPill()

        self.desc = QLabel('')
        self.desc.setObjectName('Muted')
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignTop)

        body.addWidget(self.name)
        body.addWidget(self.value)
        body.addWidget(self.pill, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute)
        body.addWidget(self.desc)
        body.addStretch(1)

    def set_result(self, item):
        self.value.setText(f"{item.value:,.2f} {item.unit if item.unit != '-' else ''}".strip())
        self.pill.set_status(item.level.value, item.title_fa)
        self.desc.setText(item.note_fa or '')


class AnalysisPage(QWidget):
    data_changed = pyqtSignal()
    toast_requested = pyqtSignal(str, str)

    def __init__(self, analysis_service: AnalysisService, import_service: ImportService, parent=None):
        super().__init__(parent)
        self.analysis_service = analysis_service
        self.import_service = import_service
        self.importer = TabularWaterSampleImporter()
        self.pool = QThreadPool.globalInstance()
        self._workers = set()
        self._build()

    def _make_field(
        self,
        title_text: str,
        widget,
        key: str | None = None,
    ):
        wrap = QWidget()

        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(
            0, 0, 0, 0
        )
        layout.setSpacing(4)

        # Give each field a full-width header so RTL alignment stays predictable.
        field_header = QWidget()
        field_header.setLayoutDirection(
            Qt.LayoutDirection.LeftToRight
        )

        field_header_layout = QHBoxLayout(
            field_header
        )
        field_header_layout.setContentsMargins(
            0, 0, 0, 0
        )
        field_header_layout.setSpacing(0)

        title = QLabel(title_text)
        title.setObjectName("FieldLabel")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        title.setWordWrap(False)

        # AlignAbsolute prevents Qt from mirroring the label to the wrong side.
        field_header_layout.addWidget(title, 1)

        layout.addWidget(
            field_header
        )

        layout.addWidget(
            widget
        )

        if key:
            err = QLabel("")
            err.setObjectName(
                "ErrorText"
            )
            err.setLayoutDirection(
                Qt.LayoutDirection.RightToLeft
            )
            err.setAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignAbsolute
                | Qt.AlignmentFlag.AlignVCenter
            )
            err.hide()

            layout.addWidget(err)
            self.errors[key] = err

        return wrap

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)
        root.setDirection(QHBoxLayout.Direction.LeftToRight)

        self.result_card = Card()
        rb = QVBoxLayout(self.result_card)
        rb.setContentsMargins(18, 16, 18, 16)
        rb.setSpacing(12)

        result_title = QLabel('نتیجه تحلیل')
        result_title.setObjectName('SectionTitle')
        result_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        result_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        result_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        result_title.setWordWrap(False)
        rb.addWidget(result_title)

        self.result_stack = QStackedWidget()
        empty = StatePanel(
            'هنوز تحلیلی انجام نشده است',
            'پارامترهای نمونه را وارد کرده و «تحلیل و ذخیره» را انتخاب کنید.',
            icon_name='fa5s.flask',
        )
        self.result_stack.addWidget(empty)

        result = QWidget()
        result_layout = QVBoxLayout(result)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(12)

        hero = Card(soft=True)
        # Use physical LTR ordering so the status pill stays right while text remains RTL.
        hero.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        hb = QHBoxLayout(hero)
        hb.setContentsMargins(14, 12, 14, 12)
        hb.setSpacing(10)
        hb.setDirection(QHBoxLayout.Direction.LeftToRight)

        hero_text_widget = QWidget()
        hero_text_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        hero_text_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hero_text = QVBoxLayout(hero_text_widget)
        hero_text.setContentsMargins(0, 0, 0, 0)
        hero_text.setSpacing(2)

        hero_title = QLabel('وضعیت کلی')
        hero_title.setObjectName('SectionTitle')
        hero_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hero_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        hero_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.overall_note = QLabel('')
        self.overall_note.setObjectName('Muted')
        self.overall_note.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.overall_note.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.overall_note.setWordWrap(True)
        self.overall_note.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop
        )

        hero_text.addWidget(hero_title)
        hero_text.addWidget(self.overall_note)
        hb.addWidget(hero_text_widget, 1)

        self.overall_pill = StatusPill()
        self.overall_pill.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        hb.addWidget(
            self.overall_pill,
            0,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop,
        )
        result_layout.addWidget(hero)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        self.cards = {name: ParameterResultCard(name) for name in ('pH', 'EC', 'TDS', 'SAR')}
        grid.addWidget(self.cards['pH'], 0, 0)
        grid.addWidget(self.cards['EC'], 0, 1)
        grid.addWidget(self.cards['TDS'], 1, 0)
        grid.addWidget(self.cards['SAR'], 1, 1)
        result_layout.addLayout(grid)

        self.infil = Card(soft=True)
        self.infil.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        ib = QVBoxLayout(self.infil)
        ib.setContentsMargins(14, 12, 14, 12)
        ib.setSpacing(8)

        infil_title = QLabel('ریسک نفوذپذیری خاک')
        infil_title.setObjectName('SectionTitle')
        infil_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        infil_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        infil_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        infil_title.setWordWrap(False)
        ib.addWidget(infil_title)

        self.infil_pill = StatusPill()
        self.infil_pill.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        ib.addWidget(
            self.infil_pill,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute,
        )

        self.infil_note = QLabel('')
        self.infil_note.setObjectName('Muted')
        self.infil_note.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.infil_note.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.infil_note.setWordWrap(True)
        self.infil_note.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop
        )
        ib.addWidget(self.infil_note)
        result_layout.addWidget(self.infil)

        self.warnings = QLabel('')
        self.warnings.setObjectName('Muted')
        self.warnings.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.warnings.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.warnings.setWordWrap(True)
        self.warnings.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop
        )
        result_layout.addWidget(self.warnings)

        disclaimer = QLabel(
            'ارزیابی بر اساس قواعد تعریف‌شده در موتور تحلیل انجام شده است. نتیجه باید در کنار نوع خاک، گیاه و شرایط بهره‌برداری تفسیر شود.'
        )
        disclaimer.setObjectName('Dim')
        disclaimer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        disclaimer.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        disclaimer.setWordWrap(True)
        disclaimer.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop
        )
        result_layout.addWidget(disclaimer)
        result_layout.addStretch(1)

        self.result_stack.addWidget(result)
        rb.addWidget(self.result_stack, 1)
        root.addWidget(self.result_card, 1)

        form_card = Card()

        # The form follows RTL flow because its labels and controls are Persian.
        form_card.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        fb = QVBoxLayout(form_card)
        fb.setContentsMargins(18, 16, 18, 16)
        fb.setSpacing(12)

        form_title = QLabel("ورود اطلاعات نمونه")
        form_title.setObjectName("SectionTitle")
        form_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        form_title.setWordWrap(False)
        fb.addWidget(form_title)

        intro = QLabel(
            "پارامترهای نمونه را وارد کنید یا از فایل CSV/Excel داده‌ها را وارد نمایید."
        )
        intro.setObjectName("Muted")
        intro.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        intro.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        intro.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        intro.setWordWrap(False)
        fb.addWidget(intro)

        self.sample_id = QLineEdit()
        self.sample_id.setPlaceholderText('خالی بگذارید تا خودکار ساخته شود')
        self.source_id = QLineEdit()
        self.source_id.setPlaceholderText('مثلاً 26-023')
        self.sample_date = QDateEdit(QDate.currentDate())
        self.sample_date.setCalendarPopup(True)
        self.sample_date.setDisplayFormat('yyyy-MM-dd')

        self.ph = QLineEdit()
        self.ec = QLineEdit()
        self.tds = QLineEdit()
        self.sar = QLineEdit()
        for w in (self.ph, self.ec, self.tds, self.sar):
            w.setValidator(QDoubleValidator(0.0, 1000000.0, 4, w))
            w.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.ec_unit = QComboBox()
        self.ec_unit.addItems(['µS/cm', 'dS/m'])

        self.errors = {}

        fields = QGridLayout()

        # Build form columns from right to left.
        fields.setOriginCorner(
            Qt.Corner.TopRightCorner
        )

        fields.setHorizontalSpacing(14)
        fields.setVerticalSpacing(8)
        fields.setColumnStretch(0, 1)
        fields.setColumnStretch(1, 1)
        fields.addWidget(self._make_field('شناسه نمونه', self.sample_id, 'sample_id'), 0, 0)
        fields.addWidget(self._make_field('منبع آب', self.source_id), 0, 1)
        fields.addWidget(self._make_field('تاریخ نمونه‌برداری', self.sample_date), 1, 0)
        fields.addWidget(self._make_field('pH', self.ph, 'ph'), 1, 1)
        fields.addWidget(self._make_field('EC', self.ec, 'ec'), 2, 0)
        fields.addWidget(self._make_field('واحد EC', self.ec_unit, 'ec_unit'), 2, 1)
        fields.addWidget(self._make_field('TDS (mg/L)', self.tds, 'tds'), 3, 0)
        fields.addWidget(self._make_field('SAR', self.sar, 'sar'), 3, 1)
        fb.addLayout(fields)
        fb.addStretch(1)

        actions_widget = QWidget()
        actions_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        actions = QHBoxLayout(actions_widget)
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(10)
        actions.setDirection(QHBoxLayout.Direction.LeftToRight)

        analyze = QPushButton("تحلیل و ذخیره")
        analyze.setProperty("variant", "primary")
        analyze.setDefault(True)
        analyze.clicked.connect(self._analyze)

        clear = QPushButton("پاک کردن فرم")
        clear.setProperty("variant", "ghost")
        clear.clicked.connect(self.clear_form)

        imp = QPushButton("ورود از فایل")
        imp.clicked.connect(self._select_import)

        # Keep the primary action at the physical right edge of the button row.
        actions.addStretch(1)
        actions.addWidget(imp)
        actions.addWidget(clear)
        actions.addWidget(analyze)
        fb.addWidget(actions_widget)

        root.addWidget(form_card, 1)

    def _sample(self):
        sid = self.sample_id.text().strip() or f"AQ-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
        return WaterSample(
            sample_id=sid,
            source_id=self.source_id.text().strip() or None,
            sample_date=self.sample_date.date().toPyDate(),
            ph=self.ph.text(),
            ec=self.ec.text(),
            ec_unit=self.ec_unit.currentText(),
            tds=self.tds.text(),
            tds_unit='mg/L',
            sar=self.sar.text(),
        )

    def _clear_errors(self):
        for e in self.errors.values():
            e.clear()
            e.hide()

    def _analyze(self):
        self._clear_errors()
        try:
            result = self.analysis_service.analyze(self._sample(), persist=True)
        except WaterSampleValidationError as exc:
            for issue in exc.issues:
                if issue.field in self.errors:
                    self.errors[issue.field].setText(issue.message_fa)
                    self.errors[issue.field].show()
            self.toast_requested.emit('لطفاً خطاهای فرم را اصلاح کنید.', 'warning')
            return
        except Exception as exc:
            self.toast_requested.emit(f'ذخیره نمونه انجام نشد: {exc}', 'error')
            return

        self.sample_id.setText(result.sample.sample_id)
        self._show_result(result)
        self.data_changed.emit()
        self.toast_requested.emit('نمونه با موفقیت تحلیل و ذخیره شد.', 'success')

    def _show_result(self, result: AnalysisResult):
        self.result_stack.setCurrentIndex(1)
        self.overall_pill.set_status(result.overall.status.value, result.overall.status_fa)
        self.overall_note.setText(result.overall.note_fa)
        self.cards['pH'].set_result(result.ph)
        self.cards['EC'].set_result(result.ec)
        self.cards['TDS'].set_result(result.tds)
        self.cards['SAR'].set_result(result.sar)
        self.infil_pill.set_status(result.infiltration.level.value, result.infiltration.title_fa)
        self.infil_note.setText(
            result.infiltration.note_fa or 'ارزیابی مشترک EC و SAR بر اساس جدول نفوذپذیری انجام شده است.'
        )
        self.warnings.setText(
            '\n'.join(f'\u200f•\u00a0{w}' for w in result.warnings)
            if result.warnings
            else 'هشدار فعالی برای این نمونه ثبت نشده است.'
        )

    def clear_form(self):
        for w in (self.sample_id, self.source_id, self.ph, self.ec, self.tds, self.sar):
            w.clear()
        self.ec_unit.setCurrentIndex(0)
        self.sample_date.setDate(QDate.currentDate())
        self._clear_errors()
        self.result_stack.setCurrentIndex(0)

    def _select_import(self):
        path, _ = QFileDialog.getOpenFileName(self, 'انتخاب فایل داده', '', 'Data files (*.csv *.xlsx *.xlsm)')
        if not path:
            return
        self.toast_requested.emit('در حال خواندن فایل…', 'info')
        worker = FunctionWorker(self.importer.load, path)
        worker.signals.result.connect(lambda batch, p=path: self._show_preview(p, batch))
        worker.signals.error.connect(
            lambda e: self.toast_requested.emit(f'فایل قابل پردازش نیست: {e}', 'error')
        )
        self._start_worker(worker)

    def _show_preview(self, path, batch):
        dialog = ImportPreviewDialog(batch, Path(path).name, self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        self.progress = QProgressDialog('در حال تحلیل و ذخیره داده‌ها…', '', 0, max(1, batch.valid_rows), self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)
        worker = FunctionWorker(self.import_service.import_and_analyze, path, progress=True)
        worker.signals.progress.connect(lambda c, t: self.progress.setValue(c))
        worker.signals.result.connect(self._import_done)
        worker.signals.error.connect(
            lambda e: (self.progress.close(), self.toast_requested.emit(f'ورود داده انجام نشد: {e}', 'error'))
        )
        self._start_worker(worker)

    def _start_worker(self, worker):
        self._workers.add(worker)
        worker.signals.finished.connect(lambda w=worker: self._workers.discard(w))
        self.pool.start(worker)

    def _import_done(self, report):
        self.progress.close()
        ImportResultDialog(report, self).exec()
        self.data_changed.emit()
        self.toast_requested.emit(
            f'{report.successful_rows} نمونه با موفقیت وارد شد.',
            'success' if report.failed_rows == 0 else 'warning',
        )
