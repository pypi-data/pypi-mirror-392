from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Callable

from baltra_sdk.domain.screening.entities import OutboundMessage, ReferenceResult, ReferenceSnapshot
from baltra_sdk.domain.screening.ports import ReferenceConversation, ReferenceRepository
from baltra_sdk.shared.utils.screening.openai_utils import (
    add_msg_to_thread,
    build_additional_instructions,
    get_openai_client,
    run_assistant_stream,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input
from baltra_sdk.shared.utils.screening.sql_utils import store_message_reference

_logger = logging.getLogger(__name__)


FALLBACK_REFERENCE_MESSAGE = (
    "✨ Gracias por escribirnos.\n📱 Este número es administrado por Baltra para ayudar a las empresas a hacer "
    "chequeos de referencias laborales de sus candidatos.\n❗ Parece que aún no estás vinculado como referencia.\n"
    "👉 Por favor, asegúrate que el candidato haya compartido tu número correctamente.\n"
    "💬 Si quieres conocer más sobre Baltra, escríbenos a info@baltra.ai.\n¡Gracias por tu tiempo! 🙌"
)


@dataclass
class LegacyReferenceConversation(ReferenceConversation):
    """Reimplementation of `reference_flow` using SOLID contracts."""

    repository: ReferenceRepository
    client_factory: Callable[[], object] = get_openai_client

    def handle(
        self,
        snapshot: ReferenceSnapshot,
        message_body: str,
        whatsapp_msg_id: str | None = None,
    ) -> ReferenceResult:
        client = self.client_factory()
        raw = snapshot.raw_payload

        user_msg_id, user_sent_by = add_msg_to_thread(raw["thread_id"], message_body, "user", client)
        store_message_reference(user_msg_id, raw, user_sent_by, message_body, whatsapp_msg_id)

        if snapshot.candidate_id == 9999:
            return self._build_fallback(raw, client)

        response, assistant_msg_id, assistant_sent_by = run_assistant_stream(
            client,
            raw,
            raw["reference_assistant"],
            build_additional_instructions("reference_context", raw),
        )
        outbound_payload = get_text_message_input(snapshot.wa_id_reference, response)
        store_message_reference(assistant_msg_id, raw, assistant_sent_by, response, "")

        classifier_json, _, _ = run_assistant_stream(client, raw, raw["reference_classifier"])
        self._persist_classifier(snapshot, classifier_json)

        return ReferenceResult(
            outbound_messages=[OutboundMessage(payload=outbound_payload)],
            reference_data=raw,
            raw_response_text=response,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _build_fallback(self, payload, client) -> ReferenceResult:
        assistant_msg_id, sent_by = add_msg_to_thread(payload["thread_id"], FALLBACK_REFERENCE_MESSAGE, "assistant", client)
        store_message_reference(assistant_msg_id, payload, sent_by, FALLBACK_REFERENCE_MESSAGE, "")
        outbound_payload = get_text_message_input(payload["wa_id"], FALLBACK_REFERENCE_MESSAGE)
        return ReferenceResult(
            outbound_messages=[OutboundMessage(payload=outbound_payload)],
            reference_data=payload,
            raw_response_text=FALLBACK_REFERENCE_MESSAGE,
            should_end_conversation=True,
        )

    def _persist_classifier(self, snapshot: ReferenceSnapshot, classifier_json: str | None) -> None:
        if not classifier_json:
            return
        try:
            payload = json.loads(classifier_json)
        except json.JSONDecodeError:
            _logger.error("Failed to parse classifier payload for reference %s", snapshot.reference_id)
            return

        if payload.get("continue") is False:
            self.repository.mark_assessment(snapshot, payload)
