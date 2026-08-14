from __future__ import annotations

from .tokens import Colors as C


def build_stylesheet(font_family: str = "Shabnam") -> str:
    return f"""
    * {{ font-family: "{font_family}", "Segoe UI", Tahoma; outline: none; }}
    QMainWindow, QWidget#AppRoot {{ background: {C.BG_BASE}; color: {C.TEXT_PRIMARY}; }}
    QWidget {{ color: {C.TEXT_PRIMARY}; font-size: 12px; }}

    QToolTip {{
        background: {C.SURFACE_3};
        color: {C.TEXT_PRIMARY};
        border: 1px solid {C.BORDER_DEFAULT};
        padding: 6px 8px;
        border-radius: 6px;
    }}

    QFrame#Sidebar {{
        background: {C.BG_SIDEBAR};
        border-left: 1px solid {C.BORDER_SUBTLE};
    }}
    QFrame#TopBar {{
        background: transparent;
        border-bottom: 1px solid {C.BORDER_SUBTLE};
    }}

    QFrame[card="true"] {{
        background: {C.SURFACE_1};
        border: 1px solid {C.BORDER_SUBTLE};
        border-radius: 16px;
    }}
    QFrame[card="soft"] {{
        background: {C.SURFACE_2};
        border: 1px solid {C.BORDER_SUBTLE};
        border-radius: 14px;
    }}
    QFrame[card="accent"] {{
        background: {C.SURFACE_1};
        border: 1px solid {C.BORDER_DEFAULT};
        border-radius: 16px;
    }}

    QLabel#BrandTitle {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 16px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
    }}
    QLabel#BrandSubtitle {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 11px;
        font-weight: 600;
        color: {C.ACCENT_HOVER};
    }}
    QLabel#SidebarVersion {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 10px;
        color: {C.TEXT_DISABLED};
    }}


    QLabel#HeroTitle {{
        font-size: 30px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
        padding-left: 14px;
    }}

    QFrame#SidebarLogoCard {{
        background: {C.SURFACE_1};
        border: 1px solid {C.BORDER_SUBTLE};
        border-radius: 14px;
    }}

    QLabel#PageTitle {{ font-size: 22px; font-weight: 700; color: {C.TEXT_PRIMARY}; }}
    QLabel#PageSubtitle {{ font-size: 12px; color: {C.TEXT_MUTED}; }}
    QLabel#SectionTitle {{ font-size: 15px; font-weight: 700; color: {C.TEXT_PRIMARY}; }}
QLabel#Muted {{ color: {C.TEXT_MUTED}; font-size: 11px; }}
    QLabel#Dim {{ color: {C.TEXT_DISABLED}; }}
    QLabel#ErrorText {{ color: {C.DANGER}; font-size: 11px; }}

    QLabel#TeamCardTitle {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 15px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
    }}
    QLabel#TeamMemberName {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 13px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
    }}
    QLabel#TeamMemberRole {{
        font-family: "Segoe UI", "{font_family}";
        font-size: 11px;
        color: {C.TEXT_MUTED};
    }}
    QFrame#TeamDivider {{
        color: {C.BORDER_DEFAULT};
        background: {C.BORDER_DEFAULT};
        min-height: 1px;
        max-height: 1px;
        border: 0;
    }}


    QLabel#MetricValue {{
        font-size: 25px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
        margin: 0;
        padding: 0;
    }}

    QLabel#MetricLabel {{
        font-size: 14px;
        font-weight: 700;
        color: {C.TEXT_PRIMARY};
        margin: 0;
        padding: 0;
    }}

    QLabel#MetricSubtitle {{
        font-size: 10.5px;
        font-weight: 500;
        color: {C.TEXT_MUTED};
        margin: 0;
        padding: 0;
    }}

    QLabel#MetricIconHolder {{
        background: rgba(45,212,191,0.10);
        border: 1px solid rgba(45,212,191,0.26);
        border-radius: 13px;
    }}

    QPushButton {{
        min-height: 36px;
        padding: 0 14px;
        border-radius: 10px;
        border: 1px solid {C.BORDER_SUBTLE};
        background: {C.SURFACE_2};
        color: {C.TEXT_PRIMARY};
        font-weight: 600;
    }}
    QPushButton:hover {{ background: {C.SURFACE_3}; border-color: {C.BORDER_DEFAULT}; }}
    QPushButton:pressed {{ background: {C.SURFACE_1}; }}
    QPushButton:disabled {{
        color: {C.TEXT_DISABLED};
        background: {C.SURFACE_1};
        border-color: {C.BORDER_SUBTLE};
    }}
    QPushButton[variant="primary"] {{
        background: {C.ACCENT};
        color: {C.BLACKISH};
        border-color: {C.ACCENT};
        font-weight: 700;
    }}
    QPushButton[variant="primary"]:hover {{ background: {C.ACCENT_HOVER}; }}
    QPushButton[variant="ghost"] {{
        background: transparent;
        border-color: transparent;
        color: {C.TEXT_MUTED};
    }}
    QPushButton[variant="ghost"]:hover {{
        background: {C.SURFACE_2};
        color: {C.TEXT_PRIMARY};
    }}
    QPushButton[variant="link"] {{
        min-height: 22px;
        padding: 0;
        border: 0;
        background: transparent;
        color: {C.TEXT_SECONDARY};
        text-align: right;
        font-family: "Segoe UI", "{font_family}";
        font-size: 10.5px;
    }}
    QPushButton[variant="link"]:hover {{
        color: {C.ACCENT_HOVER};
        background: transparent;
    }}

    QPushButton[nav="true"] {{
        min-height: 66px;
        border-radius: 14px;
        background: {C.SURFACE_1};
        border: 1px solid {C.BORDER_DEFAULT};
        color: {C.TEXT_PRIMARY};
        font-size: 16px;
        font-weight: 700;
        padding-right: 18px;
        padding-left: 18px;
        text-align: center;
    }}
    QPushButton[nav="true"]:hover {{
        background: {C.SURFACE_2};
        border-color: rgba(45,212,191,0.22);
        color: {C.TEXT_PRIMARY};
    }}
    QPushButton[nav="true"]:checked {{
        background: {C.SURFACE_SELECTED};
        color: {C.ACCENT};
        border: 1px solid rgba(45,212,191,0.34);
    }}

    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {{
        min-height: 36px;
        padding: 0 12px;
        border-radius: 10px;
        border: 1px solid {C.BORDER_DEFAULT};
        background: {C.SURFACE_2};
        color: {C.TEXT_PRIMARY};
        selection-background-color: {C.ACCENT};
        selection-color: {C.BLACKISH};
    }}
    QLineEdit:hover, QDoubleSpinBox:hover, QSpinBox:hover, QComboBox:hover, QDateEdit:hover {{
        border-color: #315472;
    }}
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {{
        border: 2px solid {C.ACCENT};
    }}
    QComboBox::drop-down {{ width: 26px; border: 0; }}
    QComboBox QAbstractItemView {{
        background: {C.SURFACE_2};
        color: {C.TEXT_PRIMARY};
        border: 1px solid {C.BORDER_DEFAULT};
        selection-background-color: {C.SURFACE_SELECTED};
        selection-color: {C.ACCENT_HOVER};
        padding: 4px;
    }}

    QTableView {{
        background: {C.SURFACE_1};
        alternate-background-color: rgba(255,255,255,0.015);
        border: 0;
        gridline-color: {C.BORDER_SUBTLE};
        color: {C.TEXT_PRIMARY};
        font-size: 11px;
    }}
    QHeaderView::section {{
        background: {C.SURFACE_2};
        color: {C.TEXT_MUTED};
        border: 0;
        border-bottom: 1px solid {C.BORDER_DEFAULT};
        padding: 7px 6px;
        font-weight: 600;
    }}
    QTableCornerButton::section {{
        background: {C.SURFACE_2};
        border: 0;
    }}

    QScrollBar:vertical, QScrollBar:horizontal {{
        background: transparent;
        border: 0;
        width: 10px;
        height: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: {C.SURFACE_3};
        border-radius: 4px;
        min-height: 24px;
        min-width: 24px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line,
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: transparent;
        border: 0;
    }}
    """
