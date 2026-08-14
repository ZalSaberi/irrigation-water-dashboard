from __future__ import annotations
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from aqualog.bootstrap import build_services
from aqualog.ui.main_window import MainWindow
from aqualog.ui.theme import build_stylesheet, load_application_fonts

def run() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app=QApplication(sys.argv); app.setApplicationName("Grovity Irrigation Water"); app.setOrganizationName("Grovity Software Team"); app.setLayoutDirection(Qt.LayoutDirection.RightToLeft); family=load_application_fonts(app); app.setStyleSheet(build_stylesheet(family)); services=build_services(); window=MainWindow(services); window.show(); return app.exec()
