from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True, slots=True)
class CompanyGroup:
    group_id: int
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    wa_id: Optional[str] = None
    phone: Optional[str] = None
