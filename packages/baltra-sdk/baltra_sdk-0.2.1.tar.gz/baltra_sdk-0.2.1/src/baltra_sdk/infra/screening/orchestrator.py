from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from baltra_sdk.application.screening.dto import ScreeningMessageDTO
from baltra_sdk.application.screening.use_cases.handle_message import (
    HandleScreeningMessageUseCase,
)
from baltra_sdk.domain.screening.entities import ScreeningResult


class ScreeningOrchestrator:
    """Transforms the webhook payload into domain DTOs and invokes the use case."""

    def __init__(self, use_case: HandleScreeningMessageUseCase) -> None:
        self._use_case = use_case

    def handle_webhook(self, body: Mapping[str, Any], candidate_snapshot=None) -> ScreeningResult:
        message = self._extract_message(body)
        dto = ScreeningMessageDTO(
            wa_id_user=self._extract_user_wa_id(body),
            wa_id_system=self._extract_system_wa_id(body),
            whatsapp_msg_id=message.get("id", ""),
            message_payload=message,
            raw_webhook=dict(body),
        )
        return self._use_case.execute(dto, candidate_snapshot=candidate_snapshot)

    def _extract_entry(self, body: Mapping[str, Any]) -> Mapping[str, Any]:
        entry = _first(body.get("entry"))
        if entry is None:
            raise ValueError("Webhook payload does not contain 'entry'.")
        return entry

    def _extract_change(self, body: Mapping[str, Any]) -> Mapping[str, Any]:
        entry = self._extract_entry(body)
        change = _first(entry.get("changes"))
        if change is None:
            raise ValueError("Webhook payload does not contain 'changes'.")
        return change

    def _extract_value(self, body: Mapping[str, Any]) -> Mapping[str, Any]:
        change = self._extract_change(body)
        value = change.get("value")
        if not isinstance(value, Mapping):
            raise ValueError("Webhook payload does not contain 'value'.")
        return value

    def _extract_message(self, body: Mapping[str, Any]) -> Dict[str, Any]:
        value = self._extract_value(body)
        message = _first(value.get("messages"))
        if message is None:
            raise ValueError("Webhook payload does not contain 'messages'.")
        return dict(message)

    def _extract_user_wa_id(self, body: Mapping[str, Any]) -> str:
        value = self._extract_value(body)
        contact = _first(value.get("contacts"))
        if contact is None:
            raise ValueError("Webhook payload does not contain 'contacts'.")
        wa_id = contact.get("wa_id")
        if not isinstance(wa_id, str):
            raise ValueError("Contact does not include 'wa_id'.")
        return wa_id

    def _extract_system_wa_id(self, body: Mapping[str, Any]) -> str:
        value = self._extract_value(body)
        metadata = value.get("metadata")
        if not isinstance(metadata, Mapping):
            raise ValueError("Webhook payload does not contain metadata.")
        phone_id = metadata.get("phone_number_id")
        if not isinstance(phone_id, str):
            raise ValueError("Metadata does not include 'phone_number_id'.")
        return phone_id


def _first(sequence: Any) -> Any:
    if isinstance(sequence, Sequence) and sequence:
        return sequence[0]
    return None
