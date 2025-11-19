from __future__ import annotations

import json
import logging

from flask import current_app

from baltra_sdk.domain.screening.entities import CandidateSnapshot, ScreeningResult, OutboundMessage
from baltra_sdk.infra.screening.services.candidate_state_service import CandidateStateService
from baltra_sdk.infra.screening.services.solid_template_renderer import SolidTemplateRenderer
from baltra_sdk.shared.utils.screening.openai_utils import (
    build_additional_instructions,
    get_openai_client,
    run_assistant_stream,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input

_logger = logging.getLogger(__name__)


class PostScreeningService:
    def __init__(
        self,
        candidate_state: CandidateStateService | None = None,
        template_renderer: SolidTemplateRenderer | None = None,
    ) -> None:
        self.state = candidate_state or CandidateStateService()
        self.templates = template_renderer or SolidTemplateRenderer()

    # ------------------------------------------------------------------
    def handle_general_intent(self, snapshot: CandidateSnapshot) -> ScreeningResult | None:
        assistant_id = snapshot.raw_payload.get("general_purpose_assistant_id")
        if not assistant_id:
            _logger.warning("General assistant missing for candidate %s", snapshot.candidate_id)
            return None
        response = self._run_assistant(snapshot.raw_payload, assistant_id, "candidate")
        if not response:
            return None
        return self._result_from_text(snapshot, response)

    def handle_post_screening_intent(
        self,
        snapshot: CandidateSnapshot,
        intent: str,
    ) -> ScreeningResult | None:
        mapping = {
            "post_screening": ("POST_SCREENING_ASSISTANT_ID", "post_screening"),
            "post_screening_verified": ("POST_SCREENING_VERIFIED_ASSISTANT_ID", None),
            "post_screening_rejected": ("POST_SCREENING_REJECTED_ASSISTANT_ID", "post_screening_rejected"),
        }
        config_key, instruction = mapping.get(intent, (None, None))
        if not config_key:
            return None
        assistant_id = current_app.config.get(config_key)
        if not assistant_id:
            _logger.warning("Config %s missing for post-screening", config_key)
            return None
        response = self._run_assistant(snapshot.raw_payload, assistant_id, instruction)
        if not response:
            return None
        return self._result_from_text(snapshot, response)

    def update_candidate_profile(self, snapshot: CandidateSnapshot) -> None:
        assistant_id = current_app.config.get("UPDATE_DB_ASSISTANT_ID")
        if not assistant_id:
            return
        candidate_data = snapshot.raw_payload
        instructions = ""
        if candidate_data.get("company_id"):
            try:
                instructions = build_additional_instructions("update_database", candidate_data)
            except Exception:
                _logger.warning(
                    "Failed to build DB instructions for candidate %s", snapshot.candidate_id, exc_info=True
                )
        try:
            client = get_openai_client()
            updates_json, *_ = run_assistant_stream(client, candidate_data, assistant_id, instructions)
        except Exception:
            _logger.exception("Profile update assistant failed for candidate %s", snapshot.candidate_id)
            return

        if not updates_json:
            _logger.warning("Profile update assistant returned empty payload for candidate %s", snapshot.candidate_id)
            return

        fallback = current_app.config.get("RESPONSE_TO_WHATSAPP_ISSUE")
        if fallback and updates_json.strip() == fallback.strip():
            _logger.warning(
                "Profile update assistant skipped for candidate %s because thread was busy.",
                snapshot.candidate_id,
            )
            return

        try:
            parsed = json.loads(updates_json or "{}")
        except Exception:
            _logger.exception("Profile update assistant failed for candidate %s", snapshot.candidate_id)
            return
        updates = parsed.get("updates")
        if updates:
            self.state.apply_candidate_updates(snapshot.candidate_id, updates)

    def update_flow_state(self, snapshot: CandidateSnapshot, new_state: str) -> None:
        _logger.debug(
            "[SOLID 6.1] PostScreeningService.update_flow_state candidate=%s new_state=%s",
            snapshot.candidate_id,
            new_state,
        )
        self.state.update_flow_state(snapshot.raw_payload, new_state)

    # ------------------------------------------------------------------
    def _run_assistant(
        self,
        candidate_data: dict,
        assistant_id: str,
        instruction_type: str | None,
    ) -> str | None:
        try:
            client = get_openai_client()
            instructions = build_additional_instructions(instruction_type, candidate_data) if instruction_type else ""
            response, *_ = run_assistant_stream(client, candidate_data, assistant_id, instructions)
            return response
        except Exception:
            _logger.exception("Assistant %s failed for candidate %s", assistant_id, candidate_data.get("candidate_id"))
            return None

    def _result_from_text(self, snapshot: CandidateSnapshot, response: str) -> ScreeningResult:
        keyword = self._extract_keyword(response)
        if keyword and keyword != "end conversation":
            rendered = self.templates.render(keyword, snapshot.raw_payload)
            payload = self._deserialize_payload(rendered.payload)
            if payload:
                return ScreeningResult(
                    outbound_messages=[OutboundMessage(payload=payload)],
                    candidate_data=snapshot.raw_payload,
                    sent_by="assistant",
                    raw_response_text=rendered.text or response,
                )
            response = rendered.text or response
        payload = self._build_text_payload(snapshot.wa_id_user, response)
        return ScreeningResult(
            outbound_messages=[OutboundMessage(payload=payload)],
            candidate_data=snapshot.raw_payload,
            sent_by="assistant",
            raw_response_text=response,
        )

    @staticmethod
    def _extract_keyword(message: str) -> str | None:
        if not message:
            return None
        start = message.find("<")
        end = message.find(">", start + 1)
        if start != -1 and end != -1:
            return message[start + 1 : end]
        return None

    def _build_text_payload(self, recipient: str, text: str) -> dict | str | None:
        raw_payload = get_text_message_input(recipient, text)
        payload = self._deserialize_payload(raw_payload)
        if payload is not None:
            return payload
        return raw_payload

    @staticmethod
    def _deserialize_payload(payload: dict | str | None) -> dict | str | None:
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                _logger.warning("Failed to decode WhatsApp payload")
                return None
        return payload
