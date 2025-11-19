from __future__ import annotations

from dataclasses import dataclass

from baltra_sdk.domain.screening.entities import ScreeningMessage, ScreeningResult
from baltra_sdk.domain.screening.ports import ScreeningEngine

from ..dto import ScreeningMessageDTO


@dataclass
class HandleScreeningMessageUseCase:
    """Coordinates the processing of an inbound screening message."""

    engine: ScreeningEngine

    def execute(self, dto: ScreeningMessageDTO, candidate_snapshot=None) -> ScreeningResult:
        message = ScreeningMessage(
            wa_id_user=dto.wa_id_user,
            wa_id_system=dto.wa_id_system,
            whatsapp_msg_id=dto.whatsapp_msg_id,
            message_payload=dto.message_payload,
            raw_webhook=dto.raw_webhook,
        )
        return self.engine.process(message, snapshot=candidate_snapshot)
