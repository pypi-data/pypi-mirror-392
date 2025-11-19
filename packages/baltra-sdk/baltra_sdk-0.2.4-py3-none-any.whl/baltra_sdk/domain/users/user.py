from dataclasses import dataclass
from typing import Optional, Dict

@dataclass(frozen=True)
class User:
    username: str
    email: Optional[str]
    status: Optional[str]
    enabled: bool
    attributes: Dict[str, str]
