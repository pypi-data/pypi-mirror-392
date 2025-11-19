from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class EligibilityEvaluation:
    role_id: int
    role_name: str
    is_eligible: bool
    reasoning: Mapping[str, object] | None = None
