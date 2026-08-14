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
    return any(
        "\u0600" <= ch <= "\u06ff"
        for ch in text
    )


def _inside_state_panel(widget: QWidget) -> bool:
    """
    Empty/error states intentionally use centered text.
    Do not convert those to right-aligned text.
    """
    parent = widget.parentWidget()

    while parent is not None:
        if parent.__class__.__name__ == "StatePanel":
            return True

        parent = parent.parentWidget()

    return False


def _is_card(widget: QWidget | None) -> bool:
    if widget is None:
        return False

    value = widget.property("card")

    return value not in (
        None,
        False,
        "",
        0,
    )


def _reset_box_alignment(widget: QWidget) -> None:
    """
    Earlier patches sometimes used:
        addWidget(widget, ..., AlignRight)

    That makes the widget keep only its sizeHint instead of
    taking the full available width.

    Remove/reinsert it without an external alignment flag.
    Internal QLabel alignment will then control the text.
    """
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

    layout.insertWidget(
        index,
        widget,
        stretch,
    )


def _align_label(label: QLabel) -> None:
    label.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )

    label.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        label.sizePolicy().verticalPolicy(),
    )

    label.setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignAbsolute
        | Qt.AlignmentFlag.AlignVCenter
    )

    # Titles and field labels must never randomly wrap.
    if label.objectName() in {
        "SectionTitle",
        "FieldLabel",
    }:
        label.setWordWrap(False)

    _reset_box_alignment(label)


def _align_group_labels(group: QWidget) -> None:
    """
    Align title + subtitle inside the same title container.
    """
    for label in group.findChildren(
        QLabel,
        options=Qt.FindChildOption.FindDirectChildrenOnly,
    ):
        if (
            _contains_persian(label.text())
            and label.objectName()
            in PERSIAN_OBJECT_NAMES
        ):
            _align_label(label)


def _remove_spacers(layout: QHBoxLayout) -> None:
    """
    Previous patches introduced addStretch() before headers.
    Those stretches are exactly the ugly gaps visible in the
    screenshots. Remove them from header rows.
    """
    for i in range(
        layout.count() - 1,
        -1,
        -1,
    ):
        item = layout.itemAt(i)

        if item is not None and item.spacerItem() is not None:
            layout.takeAt(i)


def _pin_header_to_physical_right(
    title: QLabel,
) -> None:
    """
    The important part:

    Do NOT merely right-align the text.

    If the title belongs to a small wrapper inside a
    QHBoxLayout, physically move that wrapper to the final
    (right-side) position and let it consume all remaining
    space.

    Result:

        [left control] [================ title area ========]
                                             عنوان فارسی ↑
    """
    _align_label(title)

    group = title.parentWidget()

    if group is None:
        return

    _align_group_labels(group)

    # If title is directly inside a Card/QVBoxLayout,
    # it only needs to expand to full width.
    if _is_card(group):
        group_layout = group.layout()

        if group_layout is not None:
            try:
                group_layout.setAlignment(
                    title,
                    Qt.AlignmentFlag(0),
                )
            except TypeError:
                pass

        return

    group.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )

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

    # Force PHYSICAL layout direction:
    # first items = left, last item = right.
    outer.setLayoutDirection(
        Qt.LayoutDirection.LeftToRight
    )

    layout.setDirection(
        QBoxLayout.Direction.LeftToRight
    )

    # This removes the giant red-marked empty gap.
    _remove_spacers(layout)

    # Reinsert title group LAST.
    # Any EC selector / "مشاهده همه" button remains on left.
    layout.removeWidget(group)

    layout.addWidget(
        group,
        1,
        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignAbsolute,
    )


def _normalize_persian_labels(
    root: QWidget,
) -> None:
    """
    General Persian typography rule for the page:
    Persian UI copy is physically right-aligned.

    Centered StatePanel messages are intentionally excluded.
    """
    for label in root.findChildren(QLabel):
        text = label.text().strip()

        if not text:
            continue

        if not _contains_persian(text):
            continue

        if _inside_state_panel(label):
            continue

        if label.objectName() not in PERSIAN_OBJECT_NAMES:
            continue

        _align_label(label)


def _dashboard(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        text = label.text().strip()

        if (
            text in DASHBOARD_HEADERS
            or text.startswith("روند ")
        ):
            _pin_header_to_physical_right(label)


def _analysis(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        text = label.text().strip()

        if text in ANALYSIS_HEADERS:
            _pin_header_to_physical_right(label)

    # Field titles such as:
    # شناسه نمونه، منبع آب، pH، EC، SAR...
    for label in root.findChildren(QLabel):
        if label.objectName() == "FieldLabel":
            _align_label(label)


def _samples(root: QWidget) -> None:
    for label in root.findChildren(QLabel):
        if label.text().strip() in SAMPLES_HEADERS:
            _pin_header_to_physical_right(label)


def normalize_rtl_page(root: QWidget) -> None:
    """
    One central RTL normalization pass.
    """
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
