from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import update, delete

from baltra_sdk.infra.db.models import ScreeningConversationModel, TempMessageModel
from baltra_sdk.legacy.dashboards_folder.models import ScreeningMessages
from baltra_sdk.domain.models.screening_conversation import (
    ScreeningConversationStatusCode,
    STATUS_PROCESSING,
    STATUS_DELIVERING,
    STATUS_WAITING,
)
from baltra_sdk.infra.db.session import get_session, remove_session

_logger = logging.getLogger(__name__)
_status_start_times = {}


def _describe_status(status_id: Optional[int]) -> str:
    if status_id is None:
        return "none"
    try:
        return ScreeningConversationStatusCode(status_id).name.lower()
    except ValueError:
        return f"unknown({status_id})"


def _log_status_change(conversation_id: Optional[int], old_status: Optional[int], new_status: Optional[int], reason: str) -> None:
    if not conversation_id or old_status == new_status:
        return
    now = datetime.now(timezone.utc)
    duration = None
    if conversation_id in _status_start_times:
        start, status = _status_start_times[conversation_id]
        if status == old_status:
            duration = (now - start).total_seconds()
    _status_start_times[conversation_id] = (now, new_status)
    info = "[RunState] conversation=%s status %s -> %s (%s" % (
        conversation_id,
        _describe_status(old_status),
        _describe_status(new_status),
        reason,
    )
    if duration is not None:
        info += f", {duration:.2f}s"
    info += ")"
    _logger.info(info)


def ensure_thread_registered(conversation_id: Optional[int], thread_id: Optional[str]) -> None:
    if not conversation_id or not thread_id:
        return
    session = get_session()
    try:
        with session.begin():
            conversation = session.get(ScreeningConversationModel, conversation_id)
            if conversation is None:
                return
            if conversation.active_thread_id == thread_id:
                return
            conversation.active_thread_id = thread_id
            conversation.updated_at = datetime.now(timezone.utc)
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to register thread for conversation_id=%s", conversation_id)
    finally:
        remove_session()


def mark_status(conversation_id: Optional[int], status_code: ScreeningConversationStatusCode) -> None:
    if not conversation_id:
        return
    session = get_session()
    try:
        with session.begin():
            conversation = session.get(ScreeningConversationModel, conversation_id)
            if conversation is None:
                return
            if conversation.status_id == status_code.value:
                return
            now = datetime.now(timezone.utc)
            old_status = conversation.status_id
            conversation.status_id = status_code.value
            conversation.status_changed_at = now
            conversation.updated_at = now
            _log_status_change(conversation_id, old_status, conversation.status_id, f"mark_status:{status_code.name.lower()}")
    except Exception:  # noqa: BLE001
        _logger.exception(
            "Failed to mark status %s for conversation_id=%s",
            status_code,
            conversation_id,
        )
    finally:
        remove_session()


def mark_delivering(conversation_id: Optional[int]) -> None:
    mark_status(conversation_id, ScreeningConversationStatusCode.DELIVERING)


def is_cancel_requested(conversation_id: Optional[int]) -> bool:
    if not conversation_id:
        return False
    session = get_session()
    try:
        conversation = session.get(ScreeningConversationModel, conversation_id)
        if conversation is None:
            return False
        return bool(conversation.cancel_requested)
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to read cancel_requested for conversation_id=%s", conversation_id)
        return False
    finally:
        remove_session()


def set_active_run(
    conversation_id: Optional[int],
    thread_id: Optional[str],
    run_id: Optional[str],
    priority: Optional[str] = None,
) -> None:
    if not conversation_id or not run_id:
        return
    session = get_session()
    try:
        with session.begin():
            conversation = session.get(ScreeningConversationModel, conversation_id)
            if conversation is None:
                return
            conversation.active_run_id = run_id
            if thread_id:
                conversation.active_thread_id = thread_id
            if priority:
                conversation.active_run_priority = priority
            old_status = conversation.status_id
            conversation.cancel_requested = False
            conversation.status_id = STATUS_PROCESSING.id
            conversation.status_changed_at = datetime.now(timezone.utc)
            conversation.updated_at = datetime.now(timezone.utc)
            _log_status_change(conversation_id, old_status, conversation.status_id, "openai_run_active")
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to set active run for conversation_id=%s", conversation_id)
    finally:
        remove_session()


def clear_active_run(conversation_id: Optional[int], expected_run_id: Optional[str] = None) -> None:
    if not conversation_id:
        return
    session = get_session()
    try:
        with session.begin():
            conversation = session.get(ScreeningConversationModel, conversation_id)
            if conversation is None:
                return
            if expected_run_id and conversation.active_run_id and conversation.active_run_id != expected_run_id:
                return
            conversation.active_run_id = None
            conversation.active_thread_id = None
            conversation.active_run_priority = None
            conversation.updated_at = datetime.now(timezone.utc)
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to clear active run for conversation_id=%s", conversation_id)
    finally:
        remove_session()


def assign_openai_message_ids(temp_message_ids: Optional[Sequence[int]], openai_message_id: str) -> None:
    if not temp_message_ids or not openai_message_id:
        return
    session = get_session()
    try:
        with session.begin():
            session.execute(
                update(TempMessageModel)
                .where(TempMessageModel.id.in_(list(temp_message_ids)))
                .values(openai_message_id=openai_message_id)
            )
    except Exception:  # noqa: BLE001
        _logger.exception(
            "Failed to assign OpenAI message id to temp messages %s",
            temp_message_ids,
        )
    finally:
        remove_session()


def reset_conversation_state(
    conversation_id: Optional[int],
    temp_message_ids: Optional[Sequence[int]] = None,
    extra_openai_ids: Optional[Sequence[str]] = None,
) -> None:
    if not conversation_id:
        return
    session = get_session()
    try:
        with session.begin():
            conversation = session.get(ScreeningConversationModel, conversation_id)
            if conversation is None:
                return
            query = (
                session.query(TempMessageModel.id, TempMessageModel.message_id, TempMessageModel.openai_message_id)
                .filter(TempMessageModel.conversation_id == conversation_id)
            )
            if temp_message_ids:
                query = query.filter(TempMessageModel.id.in_(list(temp_message_ids)))
            rows = query.all()

            wa_ids = [row.message_id for row in rows if row.message_id]
            openai_ids = [row.openai_message_id for row in rows if row.openai_message_id]
            if extra_openai_ids:
                openai_ids.extend(extra_openai_ids)
            _logger.info(
                "[RunState] Resetting conversation %s (temp_rows=%s wa_ids=%s openai_ids=%s extra_openai=%s)",
                conversation_id,
                len(rows),
                len(wa_ids),
                len([oid for oid in openai_ids if oid]),
                len(extra_openai_ids or []),
            )
            _delete_screening_messages(session, wa_ids)
            _delete_openai_messages(conversation.active_thread_id, openai_ids)

            if rows:
                session.execute(
                    update(TempMessageModel)
                    .where(TempMessageModel.id.in_([row.id for row in rows]))
                    .values(openai_message_id=None)
                )

            now = datetime.now(timezone.utc)
            old_status = conversation.status_id
            conversation.active_run_id = None
            conversation.active_thread_id = None
            conversation.active_run_priority = None
            conversation.cancel_requested = False
            conversation.status_id = STATUS_WAITING.id
            conversation.status_changed_at = now
            conversation.updated_at = now
            _log_status_change(conversation_id, old_status, conversation.status_id, "reset_state")
            session.execute(
                update(TempMessageModel)
                .where(TempMessageModel.conversation_id == conversation_id)
                .values(processing=False)
            )
            _logger.info(
                "[RunState] Conversation %s reset to waiting; temp messages requeued.",
                conversation_id,
            )
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to reset conversation state for conversation_id=%s", conversation_id)
    finally:
        remove_session()


def _delete_screening_messages(session, whatsapp_ids: Sequence[str]) -> None:
    if not whatsapp_ids:
        return
    try:
        _logger.info(
            "[RunState] Deleting %s screening_messages rows for whatsapp ids.",
            len(whatsapp_ids),
        )
        session.execute(
            delete(ScreeningMessages).where(ScreeningMessages.whatsapp_msg_id.in_(list(whatsapp_ids)))
        )
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to delete screening messages for whatsapp ids %s", whatsapp_ids)


def _delete_openai_messages(thread_id: Optional[str], message_ids: Sequence[str]) -> None:
    if not thread_id or not message_ids:
        return
    try:
        from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client
    except Exception:  # noqa: BLE001
        _logger.exception("Failed to import OpenAI client for cleanup")
        return
    client = get_openai_client()
    for mid in message_ids:
        if not mid:
            continue
        try:
            client.beta.threads.messages.delete(thread_id=thread_id, message_id=mid)
            _logger.info(
                "[RunState] Deleted OpenAI message %s from thread %s.",
                mid,
                thread_id,
            )
        except Exception as exc:  # noqa: BLE001
            if getattr(exc, "status_code", None) == 404:
                _logger.debug(
                    "OpenAI message %s already deleted for thread %s.",
                    mid,
                    thread_id,
                )
            else:
                _logger.exception(
                    "Failed to delete OpenAI message %s for thread %s during reset",
                    mid,
                    thread_id,
                )
