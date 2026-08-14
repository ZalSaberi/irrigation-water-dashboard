from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from aqualog.services.dashboard_query_service import DashboardFilters, DashboardQueryService
from aqualog.ui.charts import StatusDonutChart, TrendChart
from aqualog.ui.models import RecentSamplesTableModel, StatusPillDelegate
from aqualog.ui.services_types import DashboardFilterState
from aqualog.ui.theme.tokens import Colors
from aqualog.ui.widgets import Card, DashboardFilterBar, MetricCard, StatePanel


class DashboardPage(QWidget):
    open_analysis_requested = pyqtSignal()
    open_archive_requested = pyqtSignal()
    sample_detail_requested = pyqtSignal(str)
    snapshot_updated = pyqtSignal(object)
    toast_requested = pyqtSignal(str, str)
    query_failed = pyqtSignal(str)

    def __init__(self, service: DashboardQueryService, parent=None):
        super().__init__(parent)
        self.service = service
        self._build()

    def _build(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        outer.addLayout(root, 1)

        self.filters = DashboardFilterBar()
        self.filters.filters_changed.connect(self.refresh)
        root.addWidget(self.filters)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        data = QWidget()
        body = QVBoxLayout(data)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)

        kpis = QHBoxLayout()
        kpis.setContentsMargins(0, 0, 0, 0)
        kpis.setSpacing(10)

        self.k_attention = MetricCard(
            'نیازمند توجه',
            subtitle='احتیاط + نامناسب',
            icon_name='fa5s.exclamation-triangle',
            accent=Colors.ACCENT,
        )
        self.k_good = MetricCard('نمونه‌های مناسب', icon_name='fa5s.check', accent=Colors.ACCENT)
        self.k_sources = MetricCard('منابع آب', icon_name='fa5s.water', accent=Colors.ACCENT)
        self.k_total = MetricCard('کل نمونه‌ها', icon_name='fa5s.layer-group', accent=Colors.ACCENT)

        for card in (self.k_attention, self.k_good, self.k_sources, self.k_total):
            kpis.addWidget(card, 1)
        body.addLayout(kpis)

        charts = QHBoxLayout()
        charts.setContentsMargins(0, 0, 0, 0)
        charts.setSpacing(10)

        status_card = Card()
        status_card.setMinimumHeight(300)
        status_card.setMaximumHeight(300)

        sb = QVBoxLayout(status_card)
        sb.setContentsMargins(14, 12, 14, 12)
        sb.setSpacing(6)

        status_title = QLabel("وضعیت کلی")
        status_title.setObjectName("SectionTitle")
        status_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        status_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        status_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        status_title.setWordWrap(False)
        sb.addWidget(status_title)

        status_subtitle = QLabel("توزیع تحلیل‌ها بر اساس وضعیت")
        status_subtitle.setObjectName("Muted")
        status_subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        status_subtitle.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        status_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        status_subtitle.setWordWrap(False)
        sb.addWidget(status_subtitle)

        self.donut = StatusDonutChart()
        self.donut.setMinimumHeight(200)

        self.legend_counts = {}

        legend = QVBoxLayout()
        legend.setSpacing(4)

        for label_text, key, color in [
            (
                "مناسب",
                "suitable",
                Colors.SUCCESS,
            ),
            (
                "نیازمند احتیاط",
                "caution",
                Colors.CAUTION,
            ),
            (
                "نامناسب",
                "unsuitable",
                Colors.DANGER,
            ),
        ]:
            row = QHBoxLayout()
            row.setDirection(QHBoxLayout.Direction.LeftToRight)
            row.setSpacing(6)

            dot = QLabel("●")
            dot.setStyleSheet(
                f"color:{color}; font-size:12px;"
            )

            text = QLabel(label_text)
            text.setObjectName("Muted")
            text.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            text.setAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignAbsolute
                | Qt.AlignmentFlag.AlignVCenter
            )

            count = QLabel("0")
            count.setStyleSheet(
                "font-weight:700;"
            )

            # Keep the count left and the Persian status label right.
            row.addWidget(
                count,
                0,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute,
            )
            row.addStretch(1)
            row.addWidget(text)
            row.addWidget(dot)

            legend.addLayout(row)
            self.legend_counts[key] = count

        sb.addWidget(self.donut, 1)
        sb.addLayout(legend)

        charts.addWidget(status_card, 1)

        trend_card = Card()
        trend_card.setMinimumHeight(300)
        trend_card.setMaximumHeight(300)

        tb = QVBoxLayout(trend_card)
        tb.setContentsMargins(14, 12, 14, 12)
        tb.setSpacing(6)

        trend_header = QWidget()

        # Header geometry is physical LTR; Persian labels keep their own RTL direction.
        trend_header.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        top = QGridLayout(trend_header)
        top.setOriginCorner(Qt.Corner.TopLeftCorner)
        top.setContentsMargins(0, 0, 0, 0)
        top.setHorizontalSpacing(8)
        top.setVerticalSpacing(0)

        top.setColumnStretch(0, 0)
        top.setColumnStretch(1, 1)
        top.setColumnStretch(2, 0)

        self.parameter = QComboBox()
        self.parameter.addItem("EC", "ec")
        self.parameter.addItem("TDS", "tds")
        self.parameter.addItem("SAR", "sar")
        self.parameter.addItem("pH", "ph")

        self.parameter.setFixedWidth(72)
        self.parameter.currentIndexChanged.connect(self.refresh)

        top.addWidget(
            self.parameter,
            0, 0, 1, 1,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop,
        )

        trend_titles = QWidget()

        # The container uses physical coordinates; labels handle RTL text independently.
        trend_titles.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        trend_titles.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        trend_titles_layout = QVBoxLayout(trend_titles)
        trend_titles_layout.setContentsMargins(0, 0, 0, 0)
        trend_titles_layout.setSpacing(1)

        self.trend_title = QLabel("روند شوری آب")
        self.trend_title.setObjectName("SectionTitle")
        self.trend_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.trend_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.trend_title.setWordWrap(False)

        self.trend_subtitle = QLabel(
            "تغییرات EC بر اساس تاریخ نمونه‌برداری"
        )
        self.trend_subtitle.setObjectName("Muted")
        self.trend_subtitle.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )
        self.trend_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.trend_subtitle.setWordWrap(False)

        trend_titles_layout.addWidget(self.trend_title)
        trend_titles_layout.addWidget(self.trend_subtitle)

        top.addWidget(
            trend_titles,
            0, 2, 1, 1,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop,
        )

        tb.addWidget(trend_header)

        self.trend = TrendChart()
        tb.addWidget(self.trend, 1)

        charts.addWidget(trend_card, 2)

        body.addLayout(charts)

        recent = Card()
        recent.setMinimumHeight(274)
        recent.setMaximumHeight(274)

        rb = QVBoxLayout(recent)
        rb.setContentsMargins(14, 12, 14, 12)
        rb.setSpacing(8)

        recent_header = QWidget()

        # Match the trend header geometry for consistent alignment.
        recent_header.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        rh = QGridLayout(recent_header)
        rh.setOriginCorner(Qt.Corner.TopLeftCorner)
        rh.setContentsMargins(0, 0, 0, 0)
        rh.setHorizontalSpacing(8)
        rh.setVerticalSpacing(0)

        rh.setColumnStretch(0, 0)
        rh.setColumnStretch(1, 1)
        rh.setColumnStretch(2, 0)

        all_btn = QPushButton("مشاهده همه")
        all_btn.setProperty("variant", "ghost")
        all_btn.clicked.connect(self.open_archive_requested)

        rh.addWidget(
            all_btn,
            0, 0, 1, 1,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop,
        )

        recent_titles = QWidget()
        recent_titles.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        recent_titles.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        recent_titles_layout = QVBoxLayout(recent_titles)
        recent_titles_layout.setContentsMargins(0, 0, 0, 0)
        recent_titles_layout.setSpacing(1)

        recent_title = QLabel("آخرین نمونه‌ها")
        recent_title.setObjectName("SectionTitle")
        recent_title.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        recent_title.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        recent_title.setWordWrap(False)

        recent_sub = QLabel(
            "برای مشاهده جزئیات روی هر ردیف دوبار کلیک کنید"
        )
        recent_sub.setObjectName("Muted")
        recent_sub.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        recent_sub.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignVCenter
        )
        recent_sub.setWordWrap(False)

        recent_titles_layout.addWidget(recent_title)
        recent_titles_layout.addWidget(recent_sub)

        rh.addWidget(
            recent_titles,
            0, 2, 1, 1,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignAbsolute
            | Qt.AlignmentFlag.AlignTop,
        )

        rb.addWidget(recent_header)

        self.model = RecentSamplesTableModel(
            self
        )

        self.table = QTableView()

        # Keep this compact table focused on the most recent samples.
        self.table.setStyleSheet("""
            QTableView {
                font-size: 13px;
            }

            QHeaderView::section {
                font-size: 13px;
                font-weight: 700;
                padding: 5px;
            }
        """)
        self.table.setModel(self.model)

        self.table.setAlternatingRowColors(
            True
        )
        self.table.setShowGrid(True)

        self.table.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.table.verticalHeader().hide()

        # Reserve enough height for five readable rows.
        self.table.verticalHeader().setDefaultSectionSize(
            32
        )

        self.table.horizontalHeader().setFixedHeight(
            36
        )



        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setItemDelegateForColumn(
            5,
            StatusPillDelegate(self.table),
        )

        self.table.doubleClicked.connect(
            self._open_row
        )

        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Size the card to fit the header, five rows, and the border cleanly.
        self.table.setFixedHeight(200)

        rb.addWidget(self.table)

        body.addWidget(recent)

        self.stack.addWidget(data)

        self.empty = StatePanel(
            'هنوز نمونه‌ای ثبت نشده است',
            'برای شروع، اولین نمونه را تحلیل کنید یا داده‌ها را از فایل وارد کنید.',
            icon_name='fa5s.tint',
            action_text='تحلیل اولین نمونه',
        )
        self.empty.action_clicked.connect(self.open_analysis_requested)
        self.stack.addWidget(self.empty)

        self.no_results = StatePanel(
            'نتیجه‌ای پیدا نشد',
            'نمونه‌ای با فیلترهای فعلی وجود ندارد.',
            icon_name='fa5s.search',
            action_text='پاک کردن فیلترها',
        )
        self.no_results.action_clicked.connect(self.filters.reset)
        self.stack.addWidget(self.no_results)

        self.error = StatePanel(
            'دریافت اطلاعات انجام نشد',
            'در خواندن اطلاعات داشبورد مشکلی رخ داده است.',
            icon_name='fa5s.exclamation-triangle',
            action_text='تلاش مجدد',
        )
        self.error.action_clicked.connect(self.refresh)
        self.stack.addWidget(self.error)

    def _open_row(self, index):
        sample_id = self.model.sample_id_at(index.row())
        if sample_id:
            self.sample_detail_requested.emit(sample_id)

    def _filters_state(self) -> DashboardFilterState:
        return self.filters.state()

    def _make_filters(self) -> DashboardFilters:
        state = self._filters_state()
        return DashboardFilters(
            source_id=state.source_id,
            status=state.status,
            date_from=state.date_from,
            date_to=state.date_to,
            date_preset=state.date_preset,
            parameter=self.parameter.currentData() or 'ec',
        )

    def refresh(self) -> None:
        try:
            self.filters.set_sources(self.service.list_sources())
            snapshot = self.service.get_snapshot(self._make_filters())
            self._apply(snapshot)
            self.snapshot_updated.emit(snapshot)
        except Exception as exc:
            self.stack.setCurrentWidget(self.error)
            self.toast_requested.emit(f'خطا در بروزرسانی داشبورد: {exc}', 'error')
            self.query_failed.emit(str(exc))

    def _apply(self, snapshot) -> None:
        if snapshot.total_samples == 0:
            state = self._filters_state()
            has_filter = bool(
                state.source_id or state.status or state.date_preset or state.date_from or state.date_to
            )
            self.stack.setCurrentWidget(self.no_results if has_filter else self.empty)
            return

        self.stack.setCurrentIndex(0)
        self.k_total.set_value(snapshot.total_samples)
        self.k_sources.set_value(snapshot.source_count)
        self.k_good.set_value(snapshot.suitable_count)
        self.k_attention.set_value(snapshot.attention_count)

        mapping = {
            'ec': ('روند شوری آب', 'تغییرات EC بر اساس تاریخ نمونه‌برداری'),
            'tds': ('روند TDS', 'تغییرات کل مواد جامد محلول'),
            'sar': ('روند SAR', 'تغییرات نسبت جذب سدیم'),
            'ph': ('روند pH', 'تغییرات اسیدیته آب'),
        }
        param = self.parameter.currentData() or 'ec'
        title, subtitle = mapping[param]
        self.trend_title.setText(title)
        self.trend_subtitle.setText(subtitle)
        self.trend.set_data(snapshot.trend_points, param)

        self.donut.set_counts(
            snapshot.status_distribution.suitable,
            snapshot.status_distribution.caution,
            snapshot.status_distribution.unsuitable,
        )
        self.legend_counts['suitable'].setText(str(snapshot.status_distribution.suitable))
        self.legend_counts['caution'].setText(str(snapshot.status_distribution.caution))
        self.legend_counts['unsuitable'].setText(str(snapshot.status_distribution.unsuitable))

        self.model.set_rows(snapshot.recent_samples[:5])
