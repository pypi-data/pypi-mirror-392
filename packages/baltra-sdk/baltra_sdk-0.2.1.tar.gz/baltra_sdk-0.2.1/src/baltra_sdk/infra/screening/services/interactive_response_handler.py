from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional

from flask import current_app

from baltra_sdk.domain.screening.entities import CandidateSnapshot, OutboundMessage, ScreeningResult
from baltra_sdk.infra.screening.repositories.sqlalchemy_candidate_repository import (
    SqlAlchemyCandidateRepository,
)
from baltra_sdk.infra.screening.services.solid_template_renderer import SolidTemplateRenderer
from baltra_sdk.shared.utils.screening.openai_utils import (
    get_openai_client,
    run_assistant_stream,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import (
    get_text_message_input,
)
from baltra_sdk.shared.utils.screening.sql_utils import (
    handle_role_selection,
    update_list_reply,
    save_candidate_grade,
)

_logger = logging.getLogger(__name__)
END_CHAT = (
    "Muchas gracias por tu tiempo, si quisieras continuar tu aplicación más tarde nos puedes volver a escribir en cualquier momento"
)


@dataclass
class InteractiveOutcome:
    handled: bool = False
    stop_processing: bool = False
    snapshot: Optional[CandidateSnapshot] = None
    result: Optional[ScreeningResult] = None


class InteractiveResponseHandler:
    """Reimplements the legacy list/button reply behaviors for the SOLID flow."""

    def __init__(
        self,
        candidate_repo: SqlAlchemyCandidateRepository,
        template_renderer: Optional[SolidTemplateRenderer] = None,
    ) -> None:
        self.candidates = candidate_repo
        self.templates = template_renderer or SolidTemplateRenderer()

    def handle(
        self,
        snapshot: CandidateSnapshot,
        message: dict,
        message_body: str,
        message_type: Optional[str],
    ) -> InteractiveOutcome:
        if message_type != "interactive":
            return InteractiveOutcome()

        interactive = message.get("interactive") or {}
        if interactive.get("type") == "list_reply":
            return self._handle_list_reply(snapshot, interactive.get("list_reply"))
        if interactive.get("type") == "button_reply":
            return self._handle_button_reply(snapshot, interactive.get("button_reply"))
        return InteractiveOutcome()

    def _handle_list_reply(self, snapshot: CandidateSnapshot, list_reply: Optional[dict]) -> InteractiveOutcome:
        if not list_reply:
            return InteractiveOutcome()
        list_id = list_reply.get("id")
        if not list_id:
            return InteractiveOutcome()

        candidate_data = dict(snapshot.raw_payload)
        conversation_id = candidate_data.get("conversation_id")
        conversation_priority = candidate_data.get("conversation_priority")
        wa_id_user = snapshot.wa_id_user
        wa_id_system = snapshot.wa_id_system

        if list_id.startswith("role_id$") or list_id == "no_preference":
            success, selected_role_id, selection_message = handle_role_selection(
                candidate_data["candidate_id"], list_id
            )
            refreshed = self.candidates.get_or_create(wa_id_user=wa_id_user, wa_id_system=wa_id_system)
            if conversation_id:
                refreshed.raw_payload["conversation_id"] = conversation_id
            if conversation_priority:
                refreshed.raw_payload["conversation_priority"] = conversation_priority
            if selection_message:
                return InteractiveOutcome(
                    handled=True,
                    stop_processing=True,
                    snapshot=refreshed,
                    result=self._text_result(refreshed, selection_message),
                )
            return InteractiveOutcome(handled=True, snapshot=refreshed)

        confirmation_msg = update_list_reply(list_id, candidate_data)
        refreshed = self.candidates.get_or_create(wa_id_user=wa_id_user, wa_id_system=wa_id_system)
        if conversation_id:
            refreshed.raw_payload["conversation_id"] = conversation_id
        if conversation_priority:
            refreshed.raw_payload["conversation_priority"] = conversation_priority

        if list_id.startswith("interview_date_time$") and confirmation_msg:
            result = self._text_result(refreshed, confirmation_msg)
            self._calculate_grade(refreshed.raw_payload)
            return InteractiveOutcome(handled=True, stop_processing=True, snapshot=refreshed, result=result)

        return InteractiveOutcome(handled=True, snapshot=refreshed)

    def _handle_button_reply(self, snapshot: CandidateSnapshot, button_reply: Optional[dict]) -> InteractiveOutcome:
        if not button_reply:
            return InteractiveOutcome()
        button_id = button_reply.get("id")
        if not button_id:
            return InteractiveOutcome()

        candidate_data = dict(snapshot.raw_payload)
        if button_id == "no-button":
            rendered = self.templates.render("confirm_exit", candidate_data)
            text_response = rendered.text or END_CHAT
            payload = rendered.payload or get_text_message_input(candidate_data.get("wa_id"), text_response)
            return InteractiveOutcome(
                handled=True,
                stop_processing=True,
                snapshot=snapshot,
                result=self._payload_result(candidate_data, payload, text_response),
            )

        if button_id == "yes-exit-button":
            return InteractiveOutcome(
                handled=True,
                stop_processing=True,
                snapshot=snapshot,
                result=self._text_result(snapshot, END_CHAT),
            )

        return InteractiveOutcome()

    def _text_result(self, snapshot: CandidateSnapshot, message: str) -> ScreeningResult:
        payload = get_text_message_input(snapshot.wa_id_user, message)
        return self._payload_result(snapshot.raw_payload, payload, message)

    def _payload_result(
        self, candidate_data: dict, payload: dict | str, text_response: str
    ) -> ScreeningResult:
        outbound = OutboundMessage(payload=payload)
        return ScreeningResult(
            outbound_messages=[outbound],
            candidate_data=candidate_data,
            sent_by="assistant",
            raw_response_text=text_response,
        )

    def _calculate_grade(self, candidate_data: dict) -> None:
        try:
            client = get_openai_client()
            response, _, _ = run_assistant_stream(
                client,
                candidate_data,
                current_app.config["CANDIDATE_GRADING_ASSISTANT_ID"],
            )
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to calculate candidate grade for %s", candidate_data.get("candidate_id"))
            return

        try:
            grade_json = json.loads(response or "{}")
            experience_grade = float(grade_json.get("grade_experience", 0))
            dependents_grade = float(grade_json.get("grade_dependents", 0))
        except (ValueError, json.JSONDecodeError):
            _logger.warning("Invalid grade response for candidate %s", candidate_data.get("candidate_id"))
            return

        travel_grade = self._travel_time_score(candidate_data.get("travel_time_minutes"))
        total_grade = int(50 + 0.20 * travel_grade + 0.25 * experience_grade + 0.00 * dependents_grade)
        try:
            save_candidate_grade(candidate_data["candidate_id"], total_grade)
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to save candidate grade for %s", candidate_data.get("candidate_id"))

    @staticmethod
    def _travel_time_score(value) -> float:
        try:
            minutes = float(value)
        except (TypeError, ValueError):
            return 0
        if minutes <= 30:
            return 100
        if minutes >= 180:
            return 0
        return 100 * (1 - (minutes - 30) / 150)
