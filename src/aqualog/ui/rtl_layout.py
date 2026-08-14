from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)


PERSIAN_OBJECT_NAMES = {
    "SectionTitle",
    "FieldLabel",
    "Muted",
    "Dim",
}

DASHBOARD_HEADERS = {
    "وضعیت کلی",
    "آخرین نمونه‌ها",
}

ANALYSIS_HEADERS = {
    "ورود اطلاعات نمونه",
    "نتیجه تحلیل",
    "ریسک نفوذپذیری خاک",
}

SAMPLES_HEADERS = {
    "آرشیو نمونه‌ها",
}


def _contains_persian(text: str) -> bool:
    return any("\u0600" <= char <= "\u06ff" for char in text)


def _inside_state_panel(widget: QWidget) -> bool:
    """Return True when a label belongs to a centered empty/error state."""
    parent = widget.parentWidget()
    while parent is not None:
        if parent.__class__.__name__ == "StatePanel":
            return True
        parent = parent.parentWidget()
    return False


def _is_card(widget: QWidget | None) -> bool:
    if widget is None:
        return False
    return widget.property("card") not in (None, False, "", 0)


def _reset_box_alignment(widget: QWidget) -> None:
    """Let the widget use the full width instead of an outer layout alignment."""
    parent = widget.parentWidget()
    if parent is None:
        return

    layout = parent.layout()
    if not isinstance(layout, QBoxLayout):
        return

    index = layout.indexOf(widget)
    if index < 0:
        return

    stretch = layout.stretch(index)
    layout.removeWidget(widget)
    layout.insertWidget(index, widget, stretch)


def _align_label(label: QLabel) -> None:
    label.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    label.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        label.sizePolicy().verticalPolicy(),
    )
    label.setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignAbsolute
        | Qt.AlignmentFlag.AlignVCenter
    )

    if label.objectName() in {"SectionTitle", "FieldLabel"}:
        label.setWordWrap(False)

    _reset_box_alignment(label)


def _align_group_labels(group: QWidget) -> None:
    """Apply RTL alignment to Persian labels in the same header group."""
    for label in group.findChildren(
        QLabel,
        options=Qt.FindChildOption.FindDirectChildrenOnly,
    ):
        if (
            _contains_persian(label.text())
            and label.objectName() in PERSIAN_OBJECT_NAMES
        ):
            _align_label(label)


def _remove_spacers(layout: QHBoxLayout) -> None:
    """Remove header spacers that can create large gaps after RTL mirroring."""
    for index in range(layout.count() - 1, -1, -1):
        item = layout.itemAt(index)
        if item is not None and item.spacerItem() is not None:
            layout.takeAt(index)


def _pin_header_to_physical_right(title: QLabel) -> None:
    """Keep a Persian header on the physical right while controls stay left."""
    _align_label(title)
    group = title.parentWidget()
    if group is None:
        return

    _align_group_labels(group)

    if _is_card(group):
        group_layout = group.layout()
        if group_layout is not None:
            try:
                group_layout.setAlignment(title, Qt.AlignmentFlag(0))
            except TypeError:
                pass
        return

    group.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    group.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        group.sizePolicy().verticalPolicy(),
    )

    outer = group.parentWidget()
    if outer is None:
        return

    layout = outer.layout()
    if not isinstance(layout, QHBoxLayout):
        return

    # Physical LTR ordering is deliberate here; Persian labels remain RTL.
    outer.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    layout.setDirection(QBoxLayout.Direction.LeftToRight)
    _remove_spacers(layout)

    layout.removeWidget(group)
    layout.addWidget(
        group,
        1,
        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignAbsolute,
    )


def _normalize_persian_labels(root: QWidget) -> None:
    """Right-align Persian UI labels while preserving centered state messages."""
    for label in root.findChildren(QLabel):
        text = label.text().strip()
        if not text or not _contains_persian(text):
            continue
        if _inside_state_panel(label):
            continue
        if label.objectName() not in PERSIAN_OBJECT_NAMES:
            continue
        _align_label(label)


def _dashboard(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        text = label.text().strip()
        if text in DASHBOARD_HEADERS or text.startswith("روند "):
            _pin_header_to_physical_right(label)


def _analysis(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        if label.text().strip() in ANALYSIS_HEADERS:
            _pin_header_to_physical_right(label)

    for label in root.findChildren(QLabel):
        if label.objectName() == "FieldLabel":
            _align_label(label)


def _samples(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        if label.text().strip() in SAMPLES_HEADERS:
            _pin_header_to_physical_right(label)


def normalize_rtl_page(root: QWidget) -> None:
    """Normalize Persian alignment for a supported application page."""
    _normalize_persian_labels(root)

    page_name = root.__class__.__name__
    if page_name == "DashboardPage":
        _dashboard(root)
    elif page_name == "AnalysisPage":
        _analysis(root)
    elif page_name == "SamplesPage":
        _samples(root)


def normalize_rtl_pages(*pages: QWidget) -> None:
    for page in pages:
        normalize_rtl_page(page)
