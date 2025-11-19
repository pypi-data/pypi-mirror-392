from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from baltra_sdk.legacy.dashboards_folder.models import (
    ScreeningMessages,
    ReferenceMessages,
    db,
)


def _truncate(value, max_len: int, *, field_name: str = "", context: str = ""):
    """Safely truncate string values to fit DB VARCHAR columns.

    Logs a warning if truncation occurs. Returns the original value for non-strings or None.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    if len(value) <= max_len:
        return value
    truncated = value[: max_len]
    try:
        logging.warning(
            "Truncated %s for %s from length %s to %s (value startswith=%r)",
            field_name or "field",
            context or "unknown",
            len(value),
            max_len,
            value[:16],
        )
    except Exception:
        # Logging should never break data flow
        pass
    return truncated


def store_message(
    message_id: str,
    candidate_data: dict,
    sent_by: str,
    message_body: str,
    whatsapp_msg_id: Optional[str],
):
    """Persist a screening message (candidate or assistant) for SOLID flow only.

    This function mirrors the legacy insert, but applies defensive truncation
    to comply with DB varchar limits without modifying legacy sql_utils.py.
    """
    context = f"candidate_id={candidate_data.get('candidate_id')}"
    try:
        rec = ScreeningMessages(
            message_id=_truncate(message_id, 50, field_name="message_id", context=context),
            wa_id=_truncate(candidate_data.get("wa_id"), 50, field_name="wa_id", context=context),
            company_id=candidate_data.get("company_id"),
            candidate_id=candidate_data.get("candidate_id"),
            thread_id=_truncate(candidate_data.get("thread_id"), 50, field_name="thread_id", context=context),
            time_stamp=datetime.now(),
            sent_by=_truncate(sent_by, 50, field_name="sent_by", context=context),
            message_body=message_body,
            conversation_type=_truncate("screening", 10, field_name="conversation_type", context=context),
            whatsapp_msg_id=_truncate(whatsapp_msg_id, 100, field_name="whatsapp_msg_id", context=context),
            set_id=candidate_data.get("set_id"),
            question_id=candidate_data.get("question_id"),
        )
        db.session.add(rec)
        db.session.commit()
        logging.info("[SOLID] Message stored for %s with message_id %s", context, message_id)
        return rec
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        logging.error("[SOLID] Error storing message for %s: %s", context, e)
        return None


def store_message_reference(
    message_id: str,
    candidate_data: dict,
    sent_by: str,
    message_body: str,
    whatsapp_msg_id: Optional[str],
):
    """Persist a reference message for SOLID flow only with defensive truncation."""
    context = f"reference_id={candidate_data.get('reference_id')}"
    try:
        rec = ReferenceMessages(
            message_id=_truncate(message_id, 50, field_name="message_id", context=context),
            wa_id=_truncate(candidate_data.get("wa_id"), 50, field_name="wa_id", context=context),
            reference_id=candidate_data.get("reference_id"),
            thread_id=_truncate(candidate_data.get("thread_id"), 50, field_name="thread_id", context=context),
            time_stamp=datetime.now(),
            sent_by=_truncate(sent_by, 50, field_name="sent_by", context=context),
            message_body=message_body,
            conversation_type=_truncate("reference", 10, field_name="conversation_type", context=context),
            whatsapp_msg_id=_truncate(whatsapp_msg_id, 100, field_name="whatsapp_msg_id", context=context),
        )
        db.session.add(rec)
        db.session.commit()
        logging.info("[SOLID] Reference message stored for %s with message_id %s", context, message_id)
        return rec
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        logging.error("[SOLID] Error storing reference message for %s: %s", context, e)
        return None
