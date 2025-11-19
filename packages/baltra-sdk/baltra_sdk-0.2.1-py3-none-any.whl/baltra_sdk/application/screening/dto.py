from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ScreeningMessageDTO:
    """Data transfer object representing the payload consumed by the use case."""

    wa_id_user: str
    wa_id_system: str
    whatsapp_msg_id: str
    message_payload: Dict[str, Any]
    raw_webhook: Dict[str, Any]

