from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen=True, slots=True)
class Role:
    role_id: Optional[int]
    company_id: int
    role_name: str
    role_info: Optional[Dict[str, Any]]
    active: bool
    set_id: Optional[int]
    eligibility_criteria: Optional[Dict[str, Any]]
    default_role: bool
    is_deleted: bool
    shift: Optional[str]
    location_id: Optional[int]
