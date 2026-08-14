from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from .card import Card
from aqualog.ui.icons import icon
from aqualog.ui.theme.tokens import Colors


class StatePanel(Card):
    action_clicked = pyqtSignal()

    def __init__(
        self,
        title: str,
        description: str,
        *,
        icon_name="fa5s.water",
        action_text: str | None = None,
        parent=None,
    ):
        super().__init__(soft=True, parent=parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 34, 28, 34)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image = QLabel()
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setPixmap(
            icon(icon_name, Colors.TEXT_DISABLED).pixmap(30, 30)
        )

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.description_label = QLabel(description)
        self.description_label.setObjectName("Muted")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setMaximumWidth(620)

        layout.addWidget(image)
        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)

        if action_text:
            btn = QPushButton(action_text)
            btn.setProperty("variant", "primary")
            btn.clicked.connect(self.action_clicked)
            layout.addSpacing(8)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

    def set_description(self, text: str) -> None:
        self.description_label.setText(text)
