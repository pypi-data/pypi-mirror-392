from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VerificationOutcome:
    verified: bool
    message: str
    raw_result: Dict[str, Any]
    extra: Optional[Dict[str, Any]] = None


@dataclass
class RFCInput:
    candidate_id: int
    rfc: str


@dataclass
class INEInput:
    candidate_id: int
    front_media_id: int
    back_media_id: int


@dataclass
class CURPInput:
    candidate_id: int
    curp: str

