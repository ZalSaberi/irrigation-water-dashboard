from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QGuiApplication, QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from aqualog.bootstrap import ApplicationServices
from aqualog.ui.dialogs import SampleDetailDialog
from aqualog.ui.pages import AnalysisPage, DashboardPage, SamplesPage
from aqualog.ui.widgets import HeaderBar, NavButton, TeamCard, Toast
from aqualog.ui.rtl_layout import normalize_rtl_pages


class MainWindow(QMainWindow):
    PAGES = (
        ("گزارش کلی", "خلاصه وضعیت منابع آب و آخرین تحلیل‌های ثبت‌شده"),
        ("تحلیل نمونه", "پارامترهای کیفیت آب را وارد کنید تا وضعیت آب برای آبیاری ارزیابی شود"),
        ("آرشیو نمونه‌ها", "جستجو، فیلتر و مشاهده تاریخچه نمونه‌های ثبت‌شده"),
    )

    def __init__(self, services: ApplicationServices, parent=None):
        super().__init__(parent)
        self.services = services
        self.setWindowTitle("Grovity Irrigation Water")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._build()
        self._wire()
        self._fit_to_screen()
        self.navigate(0)

    def _fit_to_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.resize(1460, 900)
            self.setFixedSize(self.size())
            return

        rect = screen.availableGeometry()
        width = min(max(int(rect.width() * 0.96), 1240), 1600)
        height = min(max(int(rect.height() * 0.95), 780), 940)
        x = rect.x() + (rect.width() - width) // 2
        y = rect.y() + (rect.height() - height) // 2
        self.setGeometry(x, y, width, height)
        self.setFixedSize(width, height)

    def _build(self) -> None:
        root = QWidget()
        root.setObjectName("AppRoot")
        root.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setCentralWidget(root)

        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        content = QWidget()
        content.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 12, 14, 8)
        content_layout.setSpacing(10)

        self.header = HeaderBar()
        content_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)
        shell.addWidget(content, 1)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(246)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 18, 12, 10)
        side.setSpacing(10)

        title = QLabel("Grovity Irrigation Water")
        title.setObjectName("BrandTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        subtitle = QLabel("By Grovity Software Team")
        subtitle.setObjectName("BrandSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        side.addWidget(title)
        side.addWidget(subtitle)
        side.addSpacing(8)

        # Three large navigation boxes use the available middle space.
        nav_wrap = QWidget()
        nav_layout = QVBoxLayout(nav_wrap)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(12)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav = []

        for index, (text, icon_name) in enumerate((
            ("گزارش کلی", "fa5s.th-large"),
            ("تحلیل نمونه", "fa5s.flask"),
            ("آرشیو نمونه‌ها", "fa5s.database"),
        )):
            button = NavButton(text, icon_name)
            button.clicked.connect(lambda _=False, i=index: self.navigate(i))
            self.nav_group.addButton(button, index)
            self.nav.append(button)
            nav_layout.addWidget(button, 1)

        side.addWidget(nav_wrap, 1)

        # Development card stays toward the lower section.
        self.team = TeamCard()
        side.addWidget(self.team, 0)

        # Grovity logo card. User should place the logo at:
        # src/aqualog/resources/images/grovity_logo.png
        self.logo_card = QFrame()
        self.logo_card.setObjectName("SidebarLogoCard")
        self.logo_card.setFixedHeight(118)
        logo_layout = QVBoxLayout(self.logo_card)
        logo_layout.setContentsMargins(10, 8, 10, 8)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        logo_path = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / "images"
            / "grovity_logo.png"
        )
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            self.logo_label.setPixmap(
                pixmap.scaled(
                    200,
                    100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.logo_card.setVisible(True)
        else:
            # Hide the empty card until the real image is added to the expected path.
            self.logo_card.setVisible(False)

        logo_layout.addWidget(self.logo_label)
        side.addWidget(self.logo_card, 0)

        version = QLabel("v0.1.0")
        version.setObjectName("SidebarVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        side.addWidget(version)

        shell.addWidget(sidebar)

        self.dashboard = DashboardPage(self.services.dashboard)
        self.analysis = AnalysisPage(self.services.analysis, self.services.importer)
        self.samples = SamplesPage(self.services.archive)

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.analysis)
        self.stack.addWidget(self.samples)

        normalize_rtl_pages(
            self.dashboard,
            self.analysis,
            self.samples,
        )

        self.toast = Toast(content)

    def _wire(self) -> None:
        self.header.refresh_requested.connect(self._refresh_current)
        self.dashboard.snapshot_updated.connect(self._dashboard_snapshot_ok)
        self.dashboard.query_failed.connect(self._dashboard_query_failed)
        self.dashboard.open_analysis_requested.connect(lambda: self.navigate(1))
        self.dashboard.open_archive_requested.connect(lambda: self.navigate(2))
        self.dashboard.sample_detail_requested.connect(self._open_detail)
        self.dashboard.toast_requested.connect(self.toast.show_message)

        self.analysis.data_changed.connect(self._data_changed)
        self.analysis.toast_requested.connect(self.toast.show_message)

        self.samples.sample_detail_requested.connect(self._open_detail)
        self.samples.toast_requested.connect(self.toast.show_message)

    def navigate(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setChecked(i == index)
        title, subtitle = self.PAGES[index]
        self.header.set_page(title, subtitle)

        page = self.stack.currentWidget()
        self._fade(page)
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()

    def _fade(self, page: QWidget) -> None:
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(170)
        animation.setStartValue(0.72)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.finished.connect(lambda: page.setGraphicsEffect(None))
        self._page_anim = animation
        animation.start()

    def _refresh_current(self) -> None:
        page = self.stack.currentWidget()
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()

    def _data_changed(self) -> None:
        self.dashboard.refresh()
        self.samples.refresh()

    def _dashboard_snapshot_ok(self, snap) -> None:
        self.header.set_database_ok(True)
        self.header.set_last_updated(snap.last_updated)

    def _dashboard_query_failed(self, message: str) -> None:
        self.header.set_database_ok(False)

    def _open_detail(self, sample_id: str) -> None:
        try:
            sample = self.services.archive.get_sample(sample_id)
            if sample is None:
                self.toast.show_message("نمونه موردنظر پیدا نشد.", "error")
                return
            result = self.services.analysis.analyze(sample, persist=False)
            SampleDetailDialog(result, self).exec()
        except Exception as exc:
            self.toast.show_message(f"نمایش جزئیات انجام نشد: {exc}", "error")
