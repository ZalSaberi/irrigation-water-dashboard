from PyQt6.QtWidgets import QFrame

class Card(QFrame):
    def __init__(self, *, soft: bool=False, accent: bool=False, parent=None):
        super().__init__(parent)
        self.setProperty("card", "accent" if accent else ("soft" if soft else "true"))
