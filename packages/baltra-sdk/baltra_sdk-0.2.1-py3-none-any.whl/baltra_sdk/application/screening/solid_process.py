from __future__ import annotations

import json
import logging
import uuid
from enum import Enum
from typing import Any, Callable, ContextManager, Mapping, Optional, Sequence

from flask import current_app

from baltra_sdk.application.screening.use_cases.handle_message import HandleScreeningMessageUseCase
from baltra_sdk.domain.screening.entities import CandidateSnapshot
from baltra_sdk.infra.screening.orchestrator import ScreeningOrchestrator
from baltra_sdk.infra.screening.repositories.sqlalchemy_candidate_repository import (
    SqlAlchemyCandidateRepository,
)
from baltra_sdk.infra.screening.repositories.sqlalchemy_question_repository import (
    SqlAlchemyQuestionRepository,
)
from baltra_sdk.infra.screening.repositories.sqlalchemy_reference_repository import (
    SqlAlchemyReferenceRepository,
)
from baltra_sdk.infra.screening.services.conversation_progression import (
    SqlAlchemyConversationProgression,
)
from baltra_sdk.infra.screening.services.intent_classifier import OpenAIIntentClassifier
from baltra_sdk.infra.screening.services.legacy_renderer import LegacyMessageRenderer
from baltra_sdk.infra.screening.services.eligibility_service import ThreadedEligibilityEvaluator
from baltra_sdk.infra.screening.services.reference_conversation import (
    LegacyReferenceConversation,
)
from baltra_sdk.infra.screening.services.solid_engine import SolidScreeningEngine
from baltra_sdk.infra.screening.services.interactive_response_handler import (
    InteractiveResponseHandler,
)
from baltra_sdk.infra.screening.services.candidate_state_service import CandidateStateService
from baltra_sdk.infra.screening.services.location_answer_handler import LocationAnswerHandler
from baltra_sdk.infra.screening.services.location_data_service import LocationDataService
from baltra_sdk.infra.screening.services.location_transit_service import LocationTransitService
from baltra_sdk.infra.screening.services.role_lookup_service import RoleLookupService
from baltra_sdk.infra.screening.services.post_screening_service import PostScreeningService
from baltra_sdk.infra.screening.services.document_upload_service import DocumentUploadService
from baltra_sdk.infra.screening.services.reference_contact_service import ReferenceContactService
from baltra_sdk.infra.screening.services.solid_template_renderer import (
    SolidTemplateRenderer,
)
from baltra_sdk.shared.utils.whatsapp_utils import get_account_config, send_message
from baltra_sdk.shared.utils.screening.document_verification import (
    handle_document_verification_flow,
)
from baltra_sdk.shared.utils.screening.openai_utils import (
    add_msg_to_thread,
    get_openai_client,
)
from baltra_sdk.shared.utils.screening.screening_flow import get_nfm_reply_response
from baltra_sdk.infra.screening.services.message_store import (
    store_message,
    store_message_reference,
)
from baltra_sdk.infra.screening.services.conversation_run_state import (
    ensure_thread_registered,
    mark_delivering,
    is_cancel_requested,
    reset_conversation_state,
    assign_openai_message_ids,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import (
    get_keyword_response_from_db,
    get_text_message_input,
)
from baltra_sdk.shared.utils.screening.whatsapp_utils import get_message_body
from baltra_sdk.legacy.dashboards_folder.models import db

_logger = logging.getLogger(__name__)


class ProcessStatus(str, Enum):
    PROCESSED = "processed"
    REQUEUE = "requeue"


def _new_app_context(app_context_factory: Callable[[], ContextManager[Any]]):
    if not callable(app_context_factory):
        raise TypeError("app_context_factory must be a callable returning a context manager")
    ctx = app_context_factory()
    if not hasattr(ctx, "__enter__") or not hasattr(ctx, "__exit__"):
        raise TypeError("app_context_factory() must return a context manager")
    return ctx


def _build_solid_screening_orchestrator() -> ScreeningOrchestrator:
    candidate_repo = SqlAlchemyCandidateRepository()
    template_renderer = SolidTemplateRenderer()
    candidate_state = CandidateStateService()
    post_screening = PostScreeningService(candidate_state=candidate_state, template_renderer=template_renderer)
    reference_contacts = ReferenceContactService(
        template_renderer=template_renderer,
        owner_wa_id=current_app.config.get("wa_id_ID_owner"),
    )
    engine = SolidScreeningEngine(
        candidates=candidate_repo,
        questions=SqlAlchemyQuestionRepository(),
        renderer=LegacyMessageRenderer(),
        intents=OpenAIIntentClassifier(),
        progression=SqlAlchemyConversationProgression(),
        eligibility=ThreadedEligibilityEvaluator(context_factory=current_app.app_context),
        post_screening=post_screening,
        reference_contacts=reference_contacts,
    )
    return ScreeningOrchestrator(
        use_case=HandleScreeningMessageUseCase(engine=engine)
    )


def _build_interactive_handler() -> InteractiveResponseHandler:
    return InteractiveResponseHandler(
        SqlAlchemyCandidateRepository(),
        template_renderer=SolidTemplateRenderer(),
    )


def _build_location_handler() -> LocationAnswerHandler:
    repo = SqlAlchemyCandidateRepository()
    state_service = CandidateStateService()
    return LocationAnswerHandler(
        repo,
        candidate_state=state_service,
        location_data=LocationDataService(),
        transit_service=LocationTransitService(),
        role_lookup=RoleLookupService(),
    )


def _build_document_upload_service() -> DocumentUploadService:
    return DocumentUploadService(
        candidate_state=CandidateStateService(),
        context_factory=current_app.app_context,
    )

_SOLID_SCREENING_ORCHESTRATOR = None
_REFERENCE_REPOSITORY = None
_REFERENCE_CONVERSATION = None
_INTERACTIVE_HANDLER = None
_LOCATION_HANDLER = None
_DOCUMENT_UPLOAD_SERVICE = None


def process_solid_whatsapp_message(
    body: Mapping[str, Any],
    app_context_factory: Callable[[], ContextManager[Any]],
    *,
    conversation_id: int | None = None,
    conversation_priority: str | None = None,
    temp_message_ids: Sequence[int] | None = None,
    batched_payloads: Sequence[Mapping[str, Any]] | None = None,
    batch_priority: str | None = None,
) -> ProcessStatus:
    """Process a WhatsApp webhook payload through the SOLID screening engine."""

    global _SOLID_SCREENING_ORCHESTRATOR, _INTERACTIVE_HANDLER, _LOCATION_HANDLER, _DOCUMENT_UPLOAD_SERVICE
    _logger.debug("[SOLID 1.1] SOLID process invoked; payload keys=%s", list(body.keys()))
    if _SOLID_SCREENING_ORCHESTRATOR is None:
        with _new_app_context(app_context_factory):
            _SOLID_SCREENING_ORCHESTRATOR = _build_solid_screening_orchestrator()
    if _INTERACTIVE_HANDLER is None:
        _INTERACTIVE_HANDLER = _build_interactive_handler()
    if _LOCATION_HANDLER is None:
        _LOCATION_HANDLER = _build_location_handler()
    if _DOCUMENT_UPLOAD_SERVICE is None:
        with _new_app_context(app_context_factory):
            _DOCUMENT_UPLOAD_SERVICE = _build_document_upload_service()

    candidate_snapshot: Optional[CandidateSnapshot] = None
    try:
        with _new_app_context(app_context_factory):
            try:
                wa_id_system = _extract_system_wa_id(body)
                wa_id_user = _extract_user_wa_id(body)
            except ValueError as exc:
                _logger.error("Invalid webhook payload (missing ids): %s", exc)
                return ProcessStatus.PROCESSED

            account_config = get_account_config(wa_id_system)
            logging_prefix = f"[Account: {account_config['account_type']}]"
            _logger.debug("[SOLID 1.2] %s Parsed platform IDs system=%s user=%s", logging_prefix, wa_id_system, wa_id_user)

            try:
                message = _extract_message(body)
            except ValueError as exc:
                _logger.error("%s Invalid webhook message payload: %s", logging_prefix, exc)
                return ProcessStatus.PROCESSED

            try:
                message_body, message_type = get_message_body(message)
            except Exception:  # noqa: BLE001
                message_body, message_type = "", message.get("type")
            _logger.debug("[SOLID 1.3] %s Resolved message type=%s body=%s", logging_prefix, message_type, message_body)
            extra_text_messages: list[Mapping[str, Any]] = []
            if batched_payloads:
                message_body, extra_text_messages = _combine_text_messages(
                    message,
                    message_body,
                    message_type,
                    batched_payloads,
                )

            reference_wa_id = current_app.config.get("wa_id_ID_owner")
            if reference_wa_id and wa_id_system == reference_wa_id:
                _handle_reference_message(
                    wa_id_user=wa_id_user,
                    wa_id_system=wa_id_system,
                    message=message,
                    message_body=message_body,
                    logging_prefix=logging_prefix,
                )
                return ProcessStatus.PROCESSED

            if message_type == "reaction":
                _logger.info("%s Reaction message ignored for wa_id %s", logging_prefix, wa_id_user)
                return ProcessStatus.PROCESSED


            def _ensure_snapshot() -> CandidateSnapshot:
                nonlocal candidate_snapshot
                if candidate_snapshot is None:
                    candidate_snapshot = _get_candidate_snapshot(
                        wa_id_user,
                        wa_id_system,
                        conversation_id=conversation_id,
                        conversation_priority=batch_priority,
                    )
                return candidate_snapshot

            candidate_snapshot = _ensure_snapshot()
            if isinstance(candidate_snapshot.raw_payload, dict):
                candidate_snapshot.raw_payload.setdefault("_cancelled_run", False)
            _logger.debug(
                "[SOLID 1.4] %s Loaded candidate snapshot id=%s flow_state=%s current_question=%s",
                logging_prefix,
                candidate_snapshot.candidate_id,
                candidate_snapshot.raw_payload.get("flow_state"),
                candidate_snapshot.raw_payload.get("current_question"),
            )
            if conversation_id:
                candidate_snapshot.raw_payload["conversation_id"] = conversation_id
            if batch_priority:
                candidate_snapshot.raw_payload["conversation_priority"] = batch_priority
            candidate_snapshot.raw_payload["_temp_message_ids"] = list(temp_message_ids or [])
            if conversation_id:
                ensure_thread_registered(conversation_id, candidate_snapshot.raw_payload.get("thread_id"))
            _append_user_message_to_thread(
                candidate_snapshot.raw_payload,
                message_body,
                temp_message_ids=temp_message_ids,
            )

            if message_type == "interactive":
                snapshot_for_interactive = _ensure_snapshot()
                outcome = _INTERACTIVE_HANDLER.handle(snapshot_for_interactive, message, message_body, message_type)
                if outcome.handled:
                    candidate_snapshot = outcome.snapshot or snapshot_for_interactive
                    if outcome.stop_processing and outcome.result and candidate_snapshot is not None:
                        candidate_data = candidate_snapshot.raw_payload
                        _log_inbound_message(candidate_data, message, message.get("id"))
                        requeue = _dispatch_screening_result(outcome.result, candidate_data, wa_id_system)
                        if requeue:
                            return ProcessStatus.REQUEUE
                        return ProcessStatus.PROCESSED

            if message_type == "flow_documents" and candidate_snapshot is not None:
                handled = _handle_flow_documents(
                    message_body,
                    message,
                    candidate_snapshot,
                    wa_id_user,
                    wa_id_system,
                    logging_prefix,
                )
                if handled:
                    return ProcessStatus.PROCESSED
            elif message_type == "nfm_reply" and candidate_snapshot is not None:
                handled = _handle_nfm_reply(message_body, candidate_snapshot, wa_id_user, wa_id_system)
                if handled:
                    return ProcessStatus.PROCESSED

            if _LOCATION_HANDLER:
                snapshot_for_location = _ensure_snapshot()
                location_outcome = _LOCATION_HANDLER.handle(snapshot_for_location, message, message_body, message_type)
                if location_outcome.handled:
                    candidate_snapshot = location_outcome.snapshot or snapshot_for_location
                    if location_outcome.stop_processing and location_outcome.result and candidate_snapshot is not None:
                        candidate_data = candidate_snapshot.raw_payload
                        _log_inbound_message(candidate_data, message, message.get("id"))
                        requeue = _dispatch_screening_result(location_outcome.result, candidate_data, wa_id_system)
                        if requeue:
                            return ProcessStatus.REQUEUE
                        return ProcessStatus.PROCESSED

            orchestrator = _SOLID_SCREENING_ORCHESTRATOR or _build_solid_screening_orchestrator()
            result = orchestrator.handle_webhook(body, candidate_snapshot=candidate_snapshot)
            _logger.debug(
                "%s Orchestrator returned should_end=%s outbound=%d candidate_id=%s",
                logging_prefix,
                result.should_end_conversation,
                len(result.outbound_messages),
                result.candidate_data.get("candidate_id") if result.candidate_data else None,
            )
            if result.should_end_conversation:
                if candidate_snapshot and isinstance(candidate_snapshot.raw_payload, dict) and candidate_snapshot.raw_payload.get("_cancelled_run"):
                    _logger.info("%s SOLID engine ending early due to cancellation (no outbound).", logging_prefix)
                    return ProcessStatus.REQUEUE
                _logger.info("%s SOLID engine requested to end conversation (no outbound).", logging_prefix)
                return ProcessStatus.PROCESSED

            candidate_data = result.candidate_data or {}
            whatsapp_msg_id = message.get("id") if isinstance(message, Mapping) else None
            _log_inbound_message(candidate_data, message, whatsapp_msg_id)
            for extra_message in extra_text_messages:
                _log_inbound_message(candidate_data, extra_message, extra_message.get("id"))
            requeue = _dispatch_screening_result(result, candidate_data, wa_id_system)
            if requeue:
                return ProcessStatus.REQUEUE
            if candidate_data.get("_cancelled_run"):
                return ProcessStatus.REQUEUE
            if candidate_snapshot and isinstance(candidate_snapshot.raw_payload, dict) and candidate_snapshot.raw_payload.get("_cancelled_run"):
                return ProcessStatus.REQUEUE
    finally:
        if candidate_snapshot and isinstance(candidate_snapshot.raw_payload, dict):
            candidate_snapshot.raw_payload["_temp_message_ids"] = []
            if not candidate_snapshot.raw_payload.get("_cancelled_run"):
                candidate_snapshot.raw_payload["_cancelled_run"] = False

    return ProcessStatus.PROCESSED


def _handle_flow_documents(
    message_body: Any,
    message: Mapping[str, Any],
    snapshot: CandidateSnapshot,
    wa_id_user: str,
    wa_id_system: str,
    logging_prefix: str,
) -> bool:
    candidate_data = snapshot.raw_payload
    client = get_openai_client()
    if candidate_data.get("funnel_state") == "document_verification":
        result = handle_document_verification_flow(
            candidate_data,
            message_body,
            wa_id_user,
            wa_id_system,
            message.get("id"),
            client,
        )
        if result and result[0] is not None:
            _log_inbound_message(candidate_data, message, message.get("id"))
            _dispatch_legacy_result(result, wa_id_system)
        return True

    global _DOCUMENT_UPLOAD_SERVICE
    if _DOCUMENT_UPLOAD_SERVICE is None:
        _DOCUMENT_UPLOAD_SERVICE = _build_document_upload_service()
    response_text = _DOCUMENT_UPLOAD_SERVICE.handle_flow_submission(candidate_data, message_body, message.get("id"))
    message["type"] = "text"
    message["text"] = {"body": response_text}
    message.pop("interactive", None)
    return False


def _handle_nfm_reply(
    message_body: str,
    snapshot: CandidateSnapshot,
    wa_id_user: str,
    wa_id_system: str,
) -> bool:
    candidate_data = snapshot.raw_payload
    _log_inbound_message(candidate_data, {}, None)
    client = get_openai_client()
    response = get_nfm_reply_response(message_body, candidate_data)

    if response == "slot_full":
        error_message = "Lo sentimos, el horario que seleccionaste ya no está disponible. Por favor, selecciona otro horario."
        _send_text_response(error_message, candidate_data, wa_id_user, wa_id_system, client)
        current_keyword = candidate_data.get("current_question")
        if current_keyword:
            text_response, wa_payload = get_keyword_response_from_db(
                session=db.session,
                keyword=current_keyword,
                candidate_data=candidate_data,
            )
            if wa_payload:
                payload_to_send = wa_payload
                if isinstance(payload_to_send, dict):
                    try:
                        payload_to_send = json.dumps(payload_to_send, ensure_ascii=False)
                    except Exception:
                        _logger.exception("Failed to serialize wa_payload to JSON; skipping send")
                        return True
                send_message(payload_to_send, wa_id_system)
                thread_message = text_response or "Enviando formulario de agendamiento"
                add_msg_to_thread(candidate_data["thread_id"], thread_message, "assistant", client)
        return True

    if response:
        _send_text_response(response, candidate_data, wa_id_user, wa_id_system, client)
    return True


def _send_text_response(text: str, candidate_data: Mapping[str, Any], wa_id_user: str, wa_id_system: str, client) -> None:
    conversation_id = candidate_data.get("conversation_id") if candidate_data else None
    if conversation_id and is_cancel_requested(conversation_id):
        _logger.info(
            "[SOLID] Skipping text response for conversation %s due to cancellation request.",
            conversation_id,
        )
        reset_conversation_state(
            conversation_id,
            temp_message_ids=candidate_data.get("_temp_message_ids"),
        )
        if isinstance(candidate_data, dict):
            candidate_data["_cancelled_run"] = True
        return
    if conversation_id:
        _logger.debug(
            "[SOLID] Delivering text response for conversation %s (len=%s).",
            conversation_id,
            len(text or ""),
        )
    payload = get_text_message_input(candidate_data.get("wa_id", wa_id_user), text)
    if isinstance(payload, dict):
        try:
            payload = json.dumps(payload, ensure_ascii=False)
        except Exception:
            _logger.exception("Failed to serialize text payload to JSON; skipping send")
            return
    send_message(payload, wa_id_system)
    message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], text, "assistant", client)
    store_message(message_id, candidate_data, sent_by, text, "")


def _dispatch_legacy_result(result: tuple, wa_id_system: str) -> None:
    data, message_id, candidate_data, sent_by, text = result
    if text and "<end conversation>" in text:
        return
    payload = data
    if isinstance(payload, dict):
        try:
            payload = json.dumps(payload, ensure_ascii=False)
        except Exception:
            _logger.exception("Failed to serialize legacy data payload to JSON; skipping send")
            return
    status_response = send_message(payload, wa_id_system)
    try:
        if status_response and status_response.status_code == 200:
            response_text = json.loads(status_response.text)
            outbound_id = response_text["messages"][0]["id"]
            if candidate_data.get("reference_id"):
                store_message_reference(message_id, candidate_data, sent_by, text, outbound_id)
            else:
                store_message(message_id, candidate_data, sent_by, text, outbound_id)
    except (AttributeError, KeyError, IndexError, json.JSONDecodeError) as error:
        _logger.error("Failed to store SOLID special message: %s", error)


def _get_candidate_snapshot(
    wa_id_user: str,
    wa_id_system: str,
    conversation_id: int | None = None,
    conversation_priority: str | None = None,
) -> CandidateSnapshot:
    repo = SqlAlchemyCandidateRepository()
    snapshot = repo.get_or_create(wa_id_user=wa_id_user, wa_id_system=wa_id_system)
    if conversation_id:
        snapshot.raw_payload["conversation_id"] = conversation_id
    if conversation_priority:
        snapshot.raw_payload["conversation_priority"] = conversation_priority
    return snapshot


def _extract_system_wa_id(body: Mapping[str, Any]) -> str:
    value = _extract_value(body)
    metadata = value.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("Webhook payload missing metadata")
    phone_id = metadata.get("phone_number_id")
    if not isinstance(phone_id, str):
        raise ValueError("Webhook payload missing phone_number_id")
    return phone_id


def _extract_user_wa_id(body: Mapping[str, Any]) -> str:
    value = _extract_value(body)
    contacts = value.get("contacts")
    if isinstance(contacts, list) and contacts:
        wa_id = contacts[0].get("wa_id")
        if isinstance(wa_id, str):
            return wa_id
    raise ValueError("Webhook payload missing wa_id user")


def _extract_message(body: Mapping[str, Any]) -> Mapping[str, Any]:
    value = _extract_value(body)
    messages = value.get("messages")
    if isinstance(messages, list) and messages:
        msg = messages[0]
        if isinstance(msg, Mapping):
            return msg
    raise ValueError("Webhook payload missing messages")


def _extract_value(body: Mapping[str, Any]) -> Mapping[str, Any]:
    entry = body.get("entry")
    if not isinstance(entry, list) or not entry:
        raise ValueError("Webhook payload missing entry")
    changes = entry[0].get("changes")
    if not isinstance(changes, list) or not changes:
        raise ValueError("Webhook payload missing changes")
    value = changes[0].get("value")
    if not isinstance(value, Mapping):
        raise ValueError("Webhook payload missing value")
    return value


def _log_inbound_message(candidate_data: Mapping[str, Any], message: Mapping[str, Any], whatsapp_msg_id: str | None) -> None:
    if not candidate_data:
        return
    try:
        message_body = _extract_message_body(message)
        message_id = f"solid-in-{candidate_data.get('candidate_id')}-{uuid.uuid4().hex}"
        store_message(message_id, candidate_data, "candidate", message_body, whatsapp_msg_id)
    except Exception as error:  # noqa: BLE001
        _logger.error("Failed to log inbound SOLID screening message: %s", error)


def _append_user_message_to_thread(
    candidate_data: Mapping[str, Any],
    message_body: Any,
    temp_message_ids: Sequence[int] | None = None,
) -> None:
    if not candidate_data or not candidate_data.get("thread_id"):
        return
    if message_body is None:
        return
    text = message_body
    if isinstance(message_body, (dict, list)):
        try:
            text = json.dumps(message_body, ensure_ascii=False)
        except TypeError:
            text = str(message_body)
    elif not isinstance(message_body, str):
        text = str(message_body)
    if not text:
        return
    try:
        client = get_openai_client()
        message_id, _ = add_msg_to_thread(candidate_data["thread_id"], text, "user", client)
        if temp_message_ids and message_id and message_id != "error":
            assign_openai_message_ids(temp_message_ids, message_id)
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to append inbound message to OpenAI thread for candidate %s", candidate_data.get("candidate_id"))


def _dispatch_screening_result(result, candidate_data, wa_id_system: str) -> bool:
    conversation_id = candidate_data.get("conversation_id") if candidate_data else None
    if conversation_id and candidate_data.get("_cancelled_run"):
        _logger.info(
            "[SOLID] Conversation %s already flagged for cancellation; requeueing batch.",
            conversation_id,
        )
        return True
    if conversation_id and is_cancel_requested(conversation_id):
        _logger.info(
            "[SOLID] Skipping outbound send for conversation %s due to pending cancellation request.",
            conversation_id,
        )
        reset_conversation_state(
            conversation_id,
            temp_message_ids=candidate_data.get("_temp_message_ids"),
        )
        if isinstance(candidate_data, dict):
            candidate_data["_cancelled_run"] = True
        return True
    if conversation_id:
        mark_delivering(conversation_id)
    for outbound in result.outbound_messages:
        payload = outbound.payload
        if isinstance(payload, dict):
            try:
                payload = json.dumps(payload, ensure_ascii=False)
            except Exception:
                _logger.exception("Failed to serialize outbound payload to JSON; skipping send")
                continue
        status_response = send_message(payload, wa_id_system, outbound.campaign_id)
        try:
            if status_response and status_response.status_code == 200:
                response_text = json.loads(status_response.text)
                outbound_id = response_text["messages"][0]["id"]
                sent_by = result.sent_by or "assistant"
                text = result.raw_response_text or ""
                message_id = result.message_id or f"solid-out-{candidate_data.get('candidate_id')}-{uuid.uuid4().hex}"
                if candidate_data.get("reference_id"):
                    store_message_reference(message_id, candidate_data, sent_by, text, outbound_id)
                else:
                    store_message(message_id, candidate_data, sent_by, text, outbound_id)
        except (AttributeError, KeyError, IndexError, json.JSONDecodeError) as error:
            _logger.error("Error storing SOLID screening message: %s", error)
    return False


def _extract_message_body(message: Mapping[str, Any]) -> str:
    message_type = message.get("type")
    if message_type == "text":
        return message.get("text", {}).get("body", "")
    if message_type == "button":
        button = message.get("button", {})
        return button.get("text") or button.get("payload") or ""
    if message_type == "interactive":
        interactive = message.get("interactive", {})
        interactive_type = interactive.get("type")
        if interactive_type == "button_reply":
            button_reply = interactive.get("button_reply", {})
            return button_reply.get("title") or button_reply.get("id") or ""
        if interactive_type == "list_reply":
            list_reply = interactive.get("list_reply", {})
            return list_reply.get("title") or list_reply.get("id") or ""
    if message_type == "voice" and "audio" in message:
        audio = message.get("audio") or {}
        return audio.get("id", "")
    return json.dumps(message, ensure_ascii=False)


def _combine_text_messages(
    primary_message: Mapping[str, Any],
    primary_body: Any,
    primary_type: str | None,
    batched_payloads: Sequence[Mapping[str, Any]],
) -> tuple[str, list[Mapping[str, Any]]]:
    if primary_type != "text":
        return primary_body, []

    parts: list[str] = []
    if isinstance(primary_body, str) and primary_body:
        parts.append(primary_body)
    extra_messages: list[Mapping[str, Any]] = []

    for payload in batched_payloads:
        try:
            extra_message = _extract_message(payload)
        except ValueError:
            continue
        extra_body, extra_type = get_message_body(extra_message)
        if extra_type != "text":
            continue
        extra_messages.append(extra_message)
        if isinstance(extra_body, str) and extra_body:
            parts.append(extra_body)

    if len(parts) <= 1:
        return primary_body, extra_messages

    combined_body = "\n".join(parts)
    text_section = primary_message.get("text")
    if isinstance(text_section, Mapping):
        updated = dict(text_section)
        updated["body"] = combined_body
    else:
        updated = {"body": combined_body}
    primary_message["text"] = updated
    return combined_body, extra_messages


def _handle_reference_message(
    wa_id_user: str,
    wa_id_system: str,
    message: Mapping[str, Any],
    message_body: str,
    logging_prefix: str,
) -> None:
    global _REFERENCE_REPOSITORY, _REFERENCE_CONVERSATION
    if _REFERENCE_REPOSITORY is None or _REFERENCE_CONVERSATION is None:
        _REFERENCE_REPOSITORY = SqlAlchemyReferenceRepository()
        _REFERENCE_CONVERSATION = LegacyReferenceConversation(repository=_REFERENCE_REPOSITORY)

    snapshot = _REFERENCE_REPOSITORY.get_or_create(wa_id_user)
    result = _REFERENCE_CONVERSATION.handle(snapshot, message_body, message.get("id"))

    for outbound in result.outbound_messages:
        payload = outbound.payload
        if isinstance(payload, dict):
            try:
                payload = json.dumps(payload, ensure_ascii=False)
            except Exception:
                _logger.exception("Failed to serialize reference payload to JSON; skipping send")
                continue
        response = send_message(payload, wa_id_system)
        if not response or response.status_code != 200:
            _logger.error("%s Failed to send reference message for wa_id %s", logging_prefix, wa_id_user)
_LOCATION_HANDLER = None
