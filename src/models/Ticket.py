from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from dataclasses_json import dataclass_json

STATE = {
    "P": "PENDIENTE",
    "E": "TERMINADO",
    "X": "ANULADO",
}

PRICES = {"O": 20.0, "P": 20.0, "R": 25.0, "L": 25.0, "A": 25.0, "B": 7.0}

CATEGORIES = {
    "O": "POLLADA",
    "P": "PARRILLADA",
    "R": "ROCOTO",
    "L": "LECHON",
    "A": "ARROZ",
    "B": "BINGO",
}
LEVELS = {
    "0": "3 AÑOS",
    "1": "4 AÑOS",
    "2": "5 AÑOS",
    "3": "1RO",
    "4": "2DO",
    "5": "2DOA",
    "6": "3RO",
    "7": "4TO",
    "8": "5TO",
    "9": "6TO",
    "10": "N/A",
}
GRADES = {
    "1": "INICIAL",
    "2": "PRIMARIA",
    "3": "SECUNDARIA",
    "4": "DEUDORES",
    "5": "N/A",
}
DATE_FORMAT = "%d/%m/%Y, %H:%M:%S"


@dataclass_json
@dataclass(kw_only=True)
class Ticket:
    ticketid = None
    name: str
    personid: int = 0
    level: str = "10"
    grade: str = "5"
    state: str = "P"
    write_udi: str
    price: float = 0.0
    flag: int = 0
    idx: int = 0
    write_at: field(default_factory=datetime.now().strftime(DATE_FORMAT))
    category: List[str] = field(
        default_factory=lambda: [k for k, _ in CATEGORIES.items()]
    )
