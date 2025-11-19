from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any, Optional
import json
import logging

from baltra_sdk.domain.screening.entities import CandidateSnapshot, ScreeningMessage
from baltra_sdk.domain.screening.ports import IntentClassifier
from baltra_sdk.shared.utils.screening.openai_utils import (
    build_additional_instructions,
    get_openai_client,
    run_assistant_stream,
)

_logger = logging.getLogger(__name__)


def _extract_message_type(payload: Mapping[str, Any]) -> str | None:
    message_type = payload.get("type")
    if isinstance(message_type, str):
        return message_type
    return None


@dataclass
class KeywordIntentClassifier(IntentClassifier):
    """Rule-based classifier that returns `question_response` for standard inputs."""

    default_intent: str = "question_response"

    def classify(self, message: ScreeningMessage, candidate: CandidateSnapshot) -> str:
        payload = message.message_payload or {}
        msg_type = _extract_message_type(payload)

        if msg_type in {"text", "button", "audio"}:
            return "question_response"

        if msg_type == "interactive":
            interactive = payload.get("interactive") or {}
            interactive_type = interactive.get("type")
            if interactive_type in {"button_reply", "list_reply"}:
                return "question_response"

        return self.default_intent


@dataclass
class OpenAIIntentClassifier(IntentClassifier):
    """Delegates classification to the existing OpenAI classifier assistant."""

    fallback: IntentClassifier | None = None

    def classify(self, message: ScreeningMessage, candidate: CandidateSnapshot) -> str:
        fallback = self.fallback or KeywordIntentClassifier()
        payload = candidate.raw_payload or {}
        assistant_id = payload.get("classifier_assistant_id")
        if not assistant_id:
            return fallback.classify(message, candidate)

        client = get_openai_client()
        instructions = build_additional_instructions("classifier", payload)
        message_type = message.message_payload.get("type") if isinstance(message.message_payload, dict) else None
        thread_id = payload.get("thread_id")
        _logger.debug(
            "[SOLID QUALIFIER] start candidate=%s assistant_id=%s message_type=%s current_question=%s payload=%s instructions=%s",
            candidate.candidate_id,
            assistant_id,
            message_type,
            payload.get("current_question"),
            json.dumps(payload, ensure_ascii=False),
            instructions.encode("unicode_escape").decode(),
        )
        if thread_id:
            curl_payload = {
                "assistant_id": assistant_id,
                "additional_instructions": instructions,
                "stream": True,
            }
            curl_cmd = (
                "curl https://api.openai.com/v1/threads/{thread}/runs "
                "-H 'Authorization: Bearer $OPENAI_API_KEY' "
                "-H 'Content-Type: application/json' "
                "-H 'OpenAI-Beta: assistants=v2' "
                "-d '{body}'"
            ).format(thread=thread_id, body=json.dumps(curl_payload).replace("'", "\\'"))
            _logger.debug("[SOLID QUALIFIER] curl=%s", curl_cmd)
        try:
            response, *_ = run_assistant_stream(client, payload, assistant_id, instructions)
            _logger.debug(
                "[SOLID QUALIFIER] raw_response candidate=%s response=%s",
                candidate.candidate_id,
                response,
            )
        except Exception:
            _logger.exception("[SOLID QUALIFIER] run_assistant_stream failed candidate=%s", candidate.candidate_id)
            return fallback.classify(message, candidate)

        if not response or not response.strip():
            _logger.debug("[SOLID QUALIFIER] empty response candidate=%s", candidate.candidate_id)
            return fallback.classify(message, candidate)

        try:
            parsed = json.loads(response)
            intent = parsed.get("intent")
            if isinstance(intent, str) and intent:
                _logger.debug(
                    "[SOLID QUALIFIER] parsed intent candidate=%s intent=%s",
                    candidate.candidate_id,
                    intent,
                )
                return intent
        except json.JSONDecodeError:
            _logger.exception("[SOLID QUALIFIER] invalid JSON candidate=%s", candidate.candidate_id)
            return fallback.classify(message, candidate)

        _logger.debug("[SOLID QUALIFIER] fallback invoked candidate=%s", candidate.candidate_id)
        return fallback.classify(message, candidate)
