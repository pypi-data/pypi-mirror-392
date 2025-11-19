from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True, slots=True)
class Location:
    location_id: Optional[int]
    company_id: Optional[int]
    latitude: float
    longitude: float
    url: Optional[str] = None
    address: Optional[str] = None
