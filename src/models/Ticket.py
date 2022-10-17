from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from dataclasses_json import dataclass_json

PRICE = {"POLLADA": 20, "PARRILLADA": 20, "ROCOTO": 15, "LECHON": 25, "ARROZ": 15}


@dataclass_json
@dataclass(kw_only=True)
class Ticket:
    ticketid = None
    name: str
    level: str
    grade: str
    state: str
    write_udi: str
    write_at: field(default_factory=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    category: List[str] = field(
        default_factory=lambda: ["POLLADA", "PARRILLADA", "ROCOTO", "LECHON", "ARROZ"]
    )
