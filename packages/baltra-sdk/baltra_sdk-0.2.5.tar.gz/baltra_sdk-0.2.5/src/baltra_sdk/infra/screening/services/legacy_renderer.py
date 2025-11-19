from __future__ import annotations

from dataclasses import dataclass

from baltra_sdk.domain.screening.entities import (
    CandidateSnapshot,
    OutboundMessage,
    QuestionPrompt,
    ScreeningResult,
)
from baltra_sdk.domain.screening.ports import MessageRenderer


@dataclass
class LegacyMessageRenderer(MessageRenderer):
    """Renders legacy templates as WhatsApp payloads."""

    def render(self, prompt: QuestionPrompt, candidate: CandidateSnapshot) -> ScreeningResult:
        outbound_payload = prompt.whatsapp_payload
        if outbound_payload is None and prompt.text_response is not None:
            outbound_payload = {
                "messaging_product": "whatsapp",
                "to": candidate.wa_id_user,
                "type": "text",
                "text": {"body": prompt.text_response},
            }

        if outbound_payload is None:
            return ScreeningResult(should_end_conversation=True)

        return ScreeningResult(
            outbound_messages=[OutboundMessage(payload=outbound_payload)],
            should_end_conversation=False,
            candidate_data=candidate.raw_payload,
            sent_by="assistant",
            raw_response_text=prompt.text_response,
        )
