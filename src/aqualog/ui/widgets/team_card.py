from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from .card import Card


class TeamCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(6)

        title = QLabel("Development Team")
        title.setObjectName("TeamCardTitle")
        root.addWidget(title)

        self._member(root, "Sara Saberi", "Lead Developer")
        for text, url in [
            ("GitHub · github.com/ZalSaberi", "https://github.com/ZalSaberi"),
            ("Email · Zal.saberi.s@gmail.com", "mailto:Zal.saberi.s@gmail.com"),
            ("LinkedIn · linkedin.com/in/saberisara", "https://linkedin.com/in/saberisara"),
        ]:
            btn = QPushButton(text)
            btn.setProperty("variant", "link")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            root.addWidget(btn)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("TeamDivider")
        root.addSpacing(2)
        root.addWidget(line)
        root.addSpacing(2)

        self._member(root, "Maryam Shahidi", "Research & Documentation Intern")

    @staticmethod
    def _member(layout, name: str, role: str) -> None:
        name_label = QLabel(name)
        name_label.setObjectName("TeamMemberName")
        role_label = QLabel(role)
        role_label.setObjectName("TeamMemberRole")
        role_label.setWordWrap(True)
        layout.addWidget(name_label)
        layout.addWidget(role_label)
