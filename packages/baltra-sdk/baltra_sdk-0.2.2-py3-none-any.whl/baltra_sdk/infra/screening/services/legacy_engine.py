from __future__ import annotations

from typing import Any, Dict

from baltra_sdk.domain.screening.entities import (
    OutboundMessage,
    ScreeningMessage,
    ScreeningResult,
)
from baltra_sdk.domain.screening.ports import ScreeningEngine
from baltra_sdk.shared.utils.screening.screening_flow import screening_flow


class LegacyScreeningEngine(ScreeningEngine):
    """Adapter that delegates to the existing `screening_flow` implementation."""

    def process(self, message: ScreeningMessage, snapshot=None) -> ScreeningResult:
        flow_result = screening_flow(
            message.wa_id_user,
            message.message_payload,
            message.wa_id_system,
            message.whatsapp_msg_id,
        )

        if flow_result is None:
            return ScreeningResult()

        data, message_id, candidate_data, sent_by, response_text = flow_result

        should_end = False
        if isinstance(response_text, str):
            should_end = "<end conversation>" in response_text

        outbound = []
        if data and not should_end:
            outbound.append(OutboundMessage(payload=data))

        return ScreeningResult(
            outbound_messages=outbound,
            should_end_conversation=should_end,
            candidate_data=candidate_data if isinstance(candidate_data, Dict) else None,
            sent_by=sent_by,
            message_id=message_id,
            raw_response_text=response_text,
        )
