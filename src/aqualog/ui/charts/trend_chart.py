from __future__ import annotations

from datetime import datetime

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from aqualog.services.dashboard_query_service import TrendPoint
from aqualog.ui.theme.tokens import Colors


class TrendChart(QWidget):
    THRESHOLDS = {
        "ec": ((0.7, "0.7"), (3.0, "3.0")),
        "tds": ((450.0, "450"), (2000.0, "2000")),
        "sar": ((3.0, "3"), (9.0, "9")),
        "ph": ((6.5, "6.5"), (8.4, "8.4")),
    }

    UNITS = {
        "ec": "dS/m",
        "tds": "mg/L",
        "sar": "SAR",
        "ph": "pH",
    }

    _EPOCH = datetime(1970, 1, 1)

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        axis = pg.DateAxisItem(orientation="bottom")
        self.plot = pg.PlotWidget(axisItems={"bottom": axis})
        self.plot.setBackground(None)
        self.plot.showGrid(x=False, y=True, alpha=.18)
        self.plot.setMouseEnabled(x=True, y=False)
        self.plot.setMenuEnabled(False)

        for axis_name in ("left", "bottom"):
            plot_axis = self.plot.getAxis(axis_name)
            plot_axis.setPen(pg.mkPen(Colors.BORDER_DEFAULT))
            plot_axis.setTextPen(pg.mkPen(Colors.TEXT_MUTED))
            plot_axis.setTickFont(QFont("Shabnam", 8))

        self.curve = None
        self.scatter = None
        self.points: list[TrendPoint] = []
        self._parsed_points: list[tuple[float, TrendPoint]] = []
        self.parameter = "ec"

        self.tooltip = QLabel(self)
        self.tooltip.setStyleSheet(
            f"background:{Colors.SURFACE_3};"
            f"color:{Colors.TEXT_PRIMARY};"
            f"border:1px solid {Colors.BORDER_DEFAULT};"
            "border-radius:7px;"
            "padding:6px 8px;"
        )
        self.tooltip.hide()

        root.addWidget(self.plot)

        self.proxy = pg.SignalProxy(
            self.plot.scene().sigMouseMoved,
            rateLimit=25,
            slot=self._mouse_moved,
        )

    @classmethod
    def _date_to_epoch(cls, value: str) -> float | None:
        """Convert ISO dates without relying on platform-specific pre-1970 timestamps."""
        try:
            dt = datetime.fromisoformat(str(value)[:10])
        except (TypeError, ValueError):
            return None
        return (dt - cls._EPOCH).total_seconds()

    def set_data(self, points: tuple[TrendPoint, ...], parameter: str) -> None:
        self.parameter = parameter if parameter in self.UNITS else "ec"
        self.points = list(points)
        self._parsed_points = []

        self.plot.clear()
        self.tooltip.hide()
        self.plot.setLabel(
            "left",
            self.UNITS[self.parameter],
            color=Colors.TEXT_MUTED,
        )

        for value, label in self.THRESHOLDS.get(self.parameter, ()):
            line = pg.InfiniteLine(
                pos=value,
                angle=0,
                pen=pg.mkPen(
                    Colors.TEXT_DISABLED,
                    width=1,
                    style=Qt.PenStyle.DashLine,
                ),
                label=label,
                labelOpts={
                    "color": Colors.TEXT_DISABLED,
                    "position": 0.96,
                    "fill": None,
                },
            )
            self.plot.addItem(line)

        xs: list[float] = []
        ys: list[float] = []

        for point in points:
            epoch = self._date_to_epoch(point.date)
            if epoch is None:
                continue
            xs.append(epoch)
            ys.append(point.value)
            self._parsed_points.append((epoch, point))

        if not xs:
            return

        self.curve = self.plot.plot(
            xs,
            ys,
            pen=pg.mkPen(Colors.ACCENT, width=2.1),
        )

        if len(xs) <= 120:
            self.scatter = pg.ScatterPlotItem(
                xs,
                ys,
                size=5,
                brush=pg.mkBrush(Colors.ACCENT),
                pen=pg.mkPen(Colors.SURFACE_1, width=1),
            )
            self.plot.addItem(self.scatter)

        self.plot.enableAutoRange()

    def _mouse_moved(self, event):
        if not self._parsed_points:
            self.tooltip.hide()
            return

        scene_pos = event[0]
        if not self.plot.sceneBoundingRect().contains(scene_pos):
            self.tooltip.hide()
            return

        pos = self.plot.plotItem.vb.mapSceneToView(scene_pos)
        mouse_x = pos.x()

        point_x, point = min(
            self._parsed_points,
            key=lambda item: abs(item[0] - mouse_x),
        )

        x_range = self.plot.plotItem.vb.viewRange()[0]
        view_width = max(1.0, x_range[1] - x_range[0])

        if abs(point_x - mouse_x) > view_width * .04:
            self.tooltip.hide()
            return

        unit = self.UNITS[self.parameter]
        self.tooltip.setText(
            f"{str(point.date)[:10]}\n"
            f"منبع: {point.source_id or '—'}\n"
            f"{self.parameter.upper()}: {point.value:,.2f} {unit}"
        )

        local = self.mapFromGlobal(
            self.plot.mapToGlobal(scene_pos.toPoint())
        )
        self.tooltip.adjustSize()
        self.tooltip.move(
            min(
                max(8, local.x() + 12),
                max(8, self.width() - self.tooltip.width() - 8),
            ),
            max(8, local.y() - self.tooltip.height() - 8),
        )
        self.tooltip.show()
        self.tooltip.raise_()
