from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional
import logging

from baltra_sdk.domain.dispatch import PriorityClass, WaMessageTypeId, WaInteractiveTypeId
from baltra_sdk.domain.ports.whatsapp_repositories import (
    ClassifierPolicy,
    ConversationRepository,
    TempMessageRepository,
    WebhookObjectStore,
)

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HandleIncomingWhatsAppMessage:
    store: WebhookObjectStore
    conversations: ConversationRepository
    temp_messages: TempMessageRepository
    classifier: ClassifierPolicy

    def execute(self, payload: Mapping[str, Any], *, context_factory) -> None:
        # Persist raw webhook
        self.store.save_raw(payload)

        # Extract basic addressing
        entry = (payload.get("entry") or [{}])[0]
        change = (entry.get("changes") or [{}])[0]
        value = change.get("value") or {}
        metadata = value.get("metadata") or {}
        wa_phone_id = metadata.get("phone_number_id")
        contacts = value.get("contacts") or [{}]
        user_phone = contacts[0].get("wa_id")

        if not wa_phone_id or not user_phone:
            raise ValueError("Missing wa_phone_id or user_phone in payload")

        # We expect repository to manage transactionality; context ensures Flask app context
        with context_factory():
            wa_type_id, wa_interactive_type_id = self.classifier.classify(payload)
            incoming_priority = _priority_from_classifier(wa_type_id, wa_interactive_type_id)
            _logger.debug(
                "[Webhook] upsert conversation wa_phone_id=%s user_phone=%s incoming_priority=%s",
                wa_phone_id,
                user_phone,
                incoming_priority,
            )
            conversation_id = self.conversations.upsert(
                wa_phone_id,
                user_phone,
                incoming_priority=incoming_priority,
            )
            self.temp_messages.insert(
                conversation_id,
                payload,
                wa_type_id=wa_type_id,
                wa_interactive_type_id=wa_interactive_type_id,
            )


def _priority_from_classifier(
    wa_type_id: Optional[int],
    wa_interactive_type_id: Optional[int],
) -> Optional[str]:
    if wa_type_id == WaMessageTypeId.TEXT.value:
        return PriorityClass.TEXT_GROUPED.value
    if wa_type_id == WaMessageTypeId.INTERACTIVE.value and wa_interactive_type_id in {
        WaInteractiveTypeId.BUTTON_REPLY.value,
        WaInteractiveTypeId.LIST_REPLY.value,
    }:
        return PriorityClass.INTERACTIVE_SOLO.value
    return None
