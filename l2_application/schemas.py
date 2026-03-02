from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass
class ForecastDay:
    day: date
    source: str
    data: dict

@dataclass
class ForecastResult:
    days: List[ForecastDay]