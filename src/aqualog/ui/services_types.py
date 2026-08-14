from dataclasses import dataclass
from datetime import date
@dataclass(frozen=True, slots=True)
class DashboardFilterState:
    source_id: str|None=None
    status: str|None=None
    date_preset: str|None=None
    date_from: date|None=None
    date_to: date|None=None
