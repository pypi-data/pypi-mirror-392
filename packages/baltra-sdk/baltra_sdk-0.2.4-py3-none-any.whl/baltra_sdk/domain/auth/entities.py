"""Authentication entities."""

from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class User:
    id: int
    cognito_sub: str
    email: str
    roles: List[str] = field(default_factory=list)
