from __future__ import annotations

class Colors:
    BG_BASE = "#07111D"
    BG_SIDEBAR = "#091522"
    SURFACE_1 = "#0D1B2A"
    SURFACE_2 = "#112235"
    SURFACE_3 = "#162A40"
    SURFACE_SELECTED = "#123831"
    BORDER_SUBTLE = "#193149"
    BORDER_DEFAULT = "#24415C"
    BORDER_ACTIVE = "#2DD4BF"
    TEXT_PRIMARY = "#F1F6FA"
    TEXT_SECONDARY = "#B8C7D5"
    TEXT_MUTED = "#8094A8"
    TEXT_DISABLED = "#53687A"
    ACCENT = "#2DD4BF"
    ACCENT_HOVER = "#5EEAD4"
    SUCCESS = "#34D399"
    CAUTION = "#FBBF24"
    DANGER = "#FB7185"
    REVIEW = "#A78BFA"
    INFO = "#60A5FA"
    BLACKISH = "#04100E"

class Spacing:
    XS=4; SM=8; MD=12; LG=16; XL=20; XXL=24; XXXL=32

class Radii:
    INPUT=9; BUTTON=10; ICON=11; KPI=14; CARD=16; DIALOG=18

class Sizes:
    SIDEBAR=280
    HEADER=76
    NAV=44
    CONTROL=40
    KPI=94

STATUS_COLORS = {
    "suitable": Colors.SUCCESS,
    "caution": Colors.CAUTION,
    "unsuitable": Colors.DANGER,
    "none": Colors.SUCCESS,
    "slight_moderate": Colors.CAUTION,
    "severe": Colors.DANGER,
    "review": Colors.REVIEW,
    "pass": Colors.SUCCESS,
    "not_available": Colors.INFO,
    "unknown": Colors.INFO,
}

STATUS_APPEARANCES = {
    "suitable": {
        "fg": "#D6FFF0",
        "bg": "#123B32",
        "border": "#1E6E5E",
    },
    "none": {
        "fg": "#D6FFF0",
        "bg": "#123B32",
        "border": "#1E6E5E",
    },
    "pass": {
        "fg": "#D6FFF0",
        "bg": "#123B32",
        "border": "#1E6E5E",
    },
    "caution": {
        "fg": "#FFF0BF",
        "bg": "#4A390A",
        "border": "#A77B11",
    },
    "slight_moderate": {
        "fg": "#FFF0BF",
        "bg": "#4A390A",
        "border": "#A77B11",
    },
    "review": {
        "fg": "#EFE1FF",
        "bg": "#37264A",
        "border": "#7C5AC7",
    },
    "unsuitable": {
        "fg": "#FFDCE3",
        "bg": "#4A1924",
        "border": "#B8465D",
    },
    "severe": {
        "fg": "#FFDCE3",
        "bg": "#4A1924",
        "border": "#B8465D",
    },
    "not_available": {
        "fg": "#E4F1FF",
        "bg": "#22384E",
        "border": "#4B7398",
    },
    "unknown": {
        "fg": "#E4F1FF",
        "bg": "#22384E",
        "border": "#4B7398",
    },
}

STATUS_LABELS = {
    "suitable": "مناسب",
    "caution": "نیازمند احتیاط",
    "unsuitable": "نامناسب",
    "none": "بدون محدودیت",
    "slight_moderate": "محدودیت کم تا متوسط",
    "severe": "محدودیت شدید",
    "review": "نیازمند بررسی",
    "pass": "تأیید",
    "not_available": "داده ناکافی",
    "unknown": "نامشخص",
}
