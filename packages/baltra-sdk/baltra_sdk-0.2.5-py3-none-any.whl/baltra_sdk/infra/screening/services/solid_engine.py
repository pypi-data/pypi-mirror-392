from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping

from baltra_sdk.domain.screening.entities import (
    OutboundMessage,
    ScreeningMessage,
    ScreeningResult,
    CandidateSnapshot
)
from baltra_sdk.domain.screening.ports import (
    CandidateRepository,
    MessageRenderer,
    IntentClassifier,
    QuestionRepository,
    ScreeningEngine,
    ConversationProgression,
    EligibilityEvaluator,
)
from baltra_sdk.shared.utils.screening.openai_utils import (
    build_additional_instructions,
    get_openai_client,
    run_assistant_stream,
)
from baltra_sdk.infra.screening.services.post_screening_service import PostScreeningService
from baltra_sdk.infra.screening.services.reference_contact_service import ReferenceContactService

_logger = logging.getLogger(__name__)
END_CHAT = "Muchas gracias por tu tiempo, si quisieras continuar tu aplicación más tarde nos puedes volver a escribir en cualquier momento."


@dataclass
class SolidScreeningEngine(ScreeningEngine):
    """New implementation of the screening engine using SOLID components."""

    _ELIGIBILITY_KEYWORDS = {
        "select_eligibility_role",
        "select_eligibility_role_integer",
        "select_eligibility_role_generic",
    }

    candidates: CandidateRepository
    questions: QuestionRepository
    renderer: MessageRenderer
    intents: IntentClassifier
    progression: ConversationProgression
    eligibility: EligibilityEvaluator
    post_screening: PostScreeningService
    reference_contacts: ReferenceContactService | None = None

    def process(self, message: ScreeningMessage, snapshot: CandidateSnapshot | None = None) -> ScreeningResult:
        candidate = snapshot or self.candidates.get_or_create(
            wa_id_user=message.wa_id_user,
            wa_id_system=message.wa_id_system,
        )
        _logger.debug("[SOLID 3.0] Candidate loaded %s snapshot=%s", candidate.candidate_id, candidate.raw_payload.get("flow_state"))
        snapshot = candidate
        if candidate.first_question_flag:
            _logger.debug("[SOLID 3.0] Candidate %s is starting the screening flow (first question).", candidate.candidate_id)
        else:
            inbound_type = self._message_type(message)
            expected_type = candidate.raw_payload.get("current_response_type")
            if expected_type == "interactive" and inbound_type != "interactive":
                _logger.debug(
                    "[SOLID 3.0] Response type mismatch candidate=%s expected=interactive received=%s; forcing aclaracion intent",
                    candidate.candidate_id,
                    inbound_type,
                )
                intent_result = self._handle_intent("aclaracion", candidate)
                if intent_result:
                    return intent_result
                return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)
            intent = self.intents.classify(message, candidate)
            _logger.debug(
                "[SOLID 3.1] SolidScreeningEngine intent result candidate=%s intent=%s current_question=%s next_question=%s",
                candidate.candidate_id,
                intent,
                candidate.raw_payload.get("current_question"),
                candidate.raw_payload.get("next_question"),
            )
            intent_result = self._handle_intent(intent, candidate)
            if intent_result:
                return intent_result

            try:
                answer_text = self._extract_answer_text(message)
            except Exception:
                _logger.exception("Failed to parse inbound message payload.")
                return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)

            if not answer_text:
                _logger.info("Candidate %s sent an empty answer; ending conversation.", candidate.candidate_id)
                return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)

            previous_payload = dict(candidate.raw_payload)
            previous_response_type = previous_payload.get("current_response_type")
            try:
                snapshot = self.progression.advance(candidate, answer_text)
                _logger.debug(
                    "[SOLID 3.3] Conversation advanced for candidate %s; next_question=%s",
                    candidate.candidate_id,
                    snapshot.raw_payload.get("next_question") if snapshot else None,
                )
            except Exception:
                _logger.exception("Failed to advance conversation for candidate %s", candidate.candidate_id)
                return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)

            self._maybe_handle_reference(previous_payload, answer_text, previous_response_type)

            if snapshot is None:
                _logger.info("Candidate %s completed all questions (no further prompts).", candidate.candidate_id)
                return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)

        wait_status = self._eligibility_wait_status(snapshot)
        _logger.debug(
            "[SOLID 3.5] Eligibility check for candidate %s returned %s (roles=%s)",
            candidate.candidate_id,
            wait_status,
            snapshot.raw_payload.get("eligible_roles"),
        )
        if wait_status is not None:
            message = self._eligibility_wait_message(snapshot, wait_status)
            if wait_status == "pending":
                try:
                    self.eligibility.evaluate(snapshot)
                except Exception:  # noqa: BLE001
                    _logger.exception("Eligibility evaluation failed to start for candidate %s", snapshot.candidate_id)
            return self._build_text_result(snapshot, message)

        try:
            prompt = self.questions.build_prompt(snapshot)
        except Exception:
            _logger.exception("Failed to build prompt for candidate %s", candidate.candidate_id)
            return ScreeningResult(should_end_conversation=True)

        result = self.renderer.render(prompt, snapshot)
        _logger.debug(
            "[SOLID 3.4] Renderer returned %s outbound messages for candidate %s",
            len(result.outbound_messages),
            candidate.candidate_id,
        )
        self._maybe_trigger_eligibility(snapshot)
        _logger.debug("[SOLID 3.6] Updating flow_state to respuesta for candidate %s", snapshot.candidate_id)
        self.post_screening.update_flow_state(snapshot, "respuesta")
        self.post_screening.update_candidate_profile(snapshot)
        return result

    def _extract_answer_text(self, message: ScreeningMessage) -> str:
        payload = message.message_payload or {}
        msg_type = payload.get("type")

        if msg_type == "text":
            return payload.get("text", {}).get("body", "") or ""

        if msg_type == "interactive":
            interactive = payload.get("interactive") or {}
            if interactive.get("type") == "button_reply":
                button = interactive.get("button_reply") or {}
                return button.get("title") or button.get("id") or ""
            if interactive.get("type") == "list_reply":
                reply = interactive.get("list_reply") or {}
                return reply.get("title") or reply.get("id") or ""

        if msg_type == "button":
            button = payload.get("button") or {}
            return button.get("text") or button.get("payload") or ""

        return ""

    @staticmethod
    def _message_type(message: ScreeningMessage) -> str | None:
        payload = message.message_payload or {}
        msg_type = payload.get("type")
        if isinstance(msg_type, str):
            return msg_type
        return None

    def _maybe_trigger_eligibility(self, candidate: CandidateSnapshot) -> None:
        payload = candidate.raw_payload
        if payload.get("flow_state") != "eligibility" and payload.get("next_question") not in self._ELIGIBILITY_KEYWORDS:
            return
        try:
            self.eligibility.evaluate(candidate)
        except Exception:  # noqa: BLE001
            logging.exception("Failed to trigger eligibility evaluation for candidate %s", candidate.candidate_id)

    def _eligibility_wait_status(self, candidate: CandidateSnapshot) -> str | None:
        payload = candidate.raw_payload or {}
        keyword = payload.get("next_question") or payload.get("current_question")
        if keyword not in self._ELIGIBILITY_KEYWORDS:
            return None

        eligible_roles = payload.get("eligible_roles") or []
        has_final_roles = any(role != "run_in_progress" for role in eligible_roles)
        if has_final_roles:
            return None
        if eligible_roles:
            return "running"
        return "pending"

    def _eligibility_wait_message(self, candidate: CandidateSnapshot, status: str) -> str:
        company_id = candidate.raw_payload.get("company_id")
        if company_id == 3:
            base = (
                "¡Muchas gracias por completar las preguntas iniciales! 🙌\n\n"
                "Ahora vamos a analizar tus respuestas para determinar qué puestos son los más adecuados para ti."
            )
        else:
            base = (
                "¡Muchas gracias por completar todas las preguntas! 🙌\n\n"
                "Ahora vamos a analizar tus respuestas para determinar qué puestos son los más adecuados para ti."
            )
        if status == "running":
            return base + " Seguimos procesando tu información, te enviaremos los resultados en un momento... ⏳"
        return base + " Te enviaremos los resultados en un momento... ⏳"

    def _build_text_result(self, candidate: CandidateSnapshot, message: str) -> ScreeningResult:
        payload = {
            "messaging_product": "whatsapp",
            "to": candidate.wa_id_user,
            "type": "text",
            "text": {"body": message},
        }
        return ScreeningResult(
            outbound_messages=[OutboundMessage(payload=payload)],
            candidate_data=candidate.raw_payload,
            sent_by="assistant",
            raw_response_text=message,
        )

    def _maybe_handle_reference(
        self,
        candidate_payload: Mapping[str, Any],
        answer_text: str,
        response_type: str | None,
    ) -> None:
        if response_type != "phone_reference":
            return
        if not self.reference_contacts:
            return
        try:
            self.reference_contacts.handle_reference_submission(candidate_payload, answer_text)
        except Exception:  # noqa: BLE001
            _logger.exception(
                "Failed to process reference contact for candidate %s",
                candidate_payload.get("candidate_id"),
            )

    def _handle_intent(self, intent: str | None, candidate: CandidateSnapshot) -> ScreeningResult | None:
        normalized_intent = (intent or "").strip().lower()
        if normalized_intent == "rechazar_candidato":
            self._attempt_mark_rejected(candidate)
            self.post_screening.update_flow_state(candidate, normalized_intent)
            return None
        if normalized_intent in {"aclaracion", "pregunta"}:
            result = self.post_screening.handle_general_intent(candidate)
            self.post_screening.update_flow_state(candidate, normalized_intent)
            if result:
                self.post_screening.update_candidate_profile(candidate)
                return result
            return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)
        if normalized_intent in {"post_screening", "post_screening_verified", "post_screening_rejected"}:
            result = self.post_screening.handle_post_screening_intent(candidate, normalized_intent)
            self.post_screening.update_flow_state(candidate, normalized_intent)
            if result:
                self.post_screening.update_candidate_profile(candidate)
                return result
            return ScreeningResult(should_end_conversation=True, candidate_data=candidate.raw_payload)
        if normalized_intent == "update_database":
            self.post_screening.update_candidate_profile(candidate)
            self.post_screening.update_flow_state(candidate, normalized_intent)
            return None
        if normalized_intent == "interrumpir_chat":
            self.post_screening.update_flow_state(candidate, normalized_intent)
            return self._build_text_result(candidate, END_CHAT)
        return None

    def _attempt_mark_rejected(self, candidate: CandidateSnapshot) -> None:
        payload = candidate.raw_payload or {}
        if not payload.get("end_interview_answer"):
            return
        if candidate.candidate_id:
            self.post_screening.state.mark_flow_rejected(candidate.candidate_id, "No Identificado")
            candidate.raw_payload["funnel_state"] = "rejected"
