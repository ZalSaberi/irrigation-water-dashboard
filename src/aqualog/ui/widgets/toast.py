from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PyQt6.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel
from aqualog.ui.theme.tokens import Colors

class Toast(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(46)
        self.setMinimumWidth(320)
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.label = QLabel()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.addWidget(self.label)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)

    def show_message(self, text: str, kind: str='info', duration: int=3500) -> None:
        colors = {'success': Colors.SUCCESS, 'error': Colors.DANGER, 'warning': Colors.CAUTION, 'info': Colors.INFO}
        color = colors.get(kind, Colors.INFO)
        self.setStyleSheet(f'QFrame{{background:{Colors.SURFACE_3}; border:1px solid {color}70; border-radius:12px;}} QLabel{{color:{Colors.TEXT_PRIMARY}; font-weight:600;}}')
        self.label.setText(text)
        self.adjustSize()
        self._reposition()
        self.effect.setOpacity(0.0)
        self.show()
        self.raise_()
        anim = QPropertyAnimation(self.effect, b'opacity', self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim = anim
        anim.start()
        self.timer.start(duration)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition()

    def _reposition(self):
        if not self.parentWidget():
            return
        p = self.parentWidget()
        x = 20
        y = max(20, p.height() - self.height() - 20)
        self.move(x, y)

    def _fade_out(self):
        anim = QPropertyAnimation(self.effect, b'opacity', self)
        anim.setDuration(180)
        anim.setStartValue(self.effect.opacity())
        anim.setEndValue(0.0)
        anim.finished.connect(self.hide)
        self._anim = anim
        anim.start()
