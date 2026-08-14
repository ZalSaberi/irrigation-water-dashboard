from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class NavButton(QPushButton):
    def __init__(self, text: str, icon_name: str = '', parent=None):
        super().__init__(text, parent)
        self.setProperty('nav', 'true')
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
