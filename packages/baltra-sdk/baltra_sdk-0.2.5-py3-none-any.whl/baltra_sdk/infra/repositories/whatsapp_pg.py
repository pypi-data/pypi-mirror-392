from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Mapping, Optional, Tuple, Sequence, List

from baltra_sdk.domain.dispatch import classify_payload, PriorityClass
from baltra_sdk.domain.ports.whatsapp_repositories import (
    ClassifierPolicy,
    ConversationRepository,
    TempMessageRepository,
    WebhookObjectStore,
)
from baltra_sdk.domain.ports.worker_queue import WorkerQueueRepository
from baltra_sdk.domain.models.screening_conversation import (
    ConversationBatch,
    TempMessage,
    ScreeningConversation,
    STATUS_PROCESSING,
    STATUS_WAITING,
    STATUS_MOUNTING,
    STATUS_DELIVERING,
)
from baltra_sdk.domain.models.screening_conversation import status_from_id
from baltra_sdk.shared.utils.postgreSQL_utils import store_wa_object
from baltra_sdk.infra.db.session import get_session, remove_session
from baltra_sdk.infra.db.models import ScreeningConversationModel, TempMessageModel
from sqlalchemy import select, exists, func, update, text, delete
from baltra_sdk.application.screening.run_priority import should_cancel_active_run
from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client


class PgWebhookObjectStore(WebhookObjectStore):
    def save_raw(self, payload: Mapping[str, object]) -> None:
        store_wa_object(payload)  # reuse existing implementation


class SqlAlchemyWebhookObjectStore(WebhookObjectStore):
    """SQLAlchemy-based persistence for raw WhatsApp webhook objects.

    This variant avoids using shared/legacy psycopg2 utils and writes directly
    via the SDK SQLAlchemy session to the whatsapp_status_updates table.
    """

    def save_raw(self, payload: Mapping[str, object]) -> None:
        session = get_session()
        try:
            entry = (payload.get("entry") or [{}])[0]
            changes = (entry.get("changes") or [{}])[0]
            value = changes.get("value") or {}
            metadata = value.get("metadata") or {}
            phone_number_id = metadata.get("phone_number_id")
            field = changes.get("field")
            object_type = payload.get("object")
            entry_id = entry.get("id")
            messaging_product = value.get("messaging_product")

            wa_id = None
            message_body = None
            timestamp = None
            conversation_id = None
            origin_type = None
            billable = None
            pricing_model = None
            category = None
            status = None
            error_info = None
            status_id = None

            if isinstance(value.get("contacts"), list):
                contacts = value.get("contacts") or [{}]
                wa_id = contacts[0].get("wa_id")
                messages = value.get("messages") or [{}]
                message = messages[0] or {}
                status_id = message.get("id")
                status = message.get("type")
                if status == "text":
                    text_obj = message.get("text") or {}
                    message_body = text_obj.get("body")
                elif status == "interactive":
                    interactive = message.get("interactive") or {}
                    itype = interactive.get("type")
                    if itype == "nfm_reply":
                        nfm = interactive.get("nfm_reply") or {}
                        message_body = nfm.get("response_json")
                        status = "flow"
                    elif itype == "button_reply":
                        btn = interactive.get("button_reply") or {}
                        message_body = btn.get("title")
                    elif itype == "list_reply":
                        lrp = interactive.get("list_reply") or {}
                        message_body = lrp.get("title")
                elif status == "location":
                    loc = message.get("location") or {}
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    if lat is not None and lon is not None:
                        message_body = f"{lat}, {lon}"
                elif status == "reaction":
                    emoji = (message.get("reaction") or {}).get("emoji") or "👍"
                    message_body = f"El usuario reacciono con el siguiente emoji: {emoji}"
                timestamp = message.get("timestamp")
            elif isinstance(value.get("statuses"), list):
                status_info = (value.get("statuses") or [{}])[0] or {}
                status_id = status_info.get("id")
                status = status_info.get("status")
                timestamp = status_info.get("timestamp")
                wa_id = status_info.get("recipient_id")

                conv = status_info.get("conversation") or {}
                if conv:
                    conversation_id = conv.get("id")
                    origin = conv.get("origin") or {}
                    origin_type = origin.get("type")

                pricing = status_info.get("pricing") or {}
                if pricing:
                    billable = pricing.get("billable")
                    pricing_model = pricing.get("pricing_model")
                    category = pricing.get("category")
                if status == "failed" and status_info.get("errors"):
                    import json as _json
                    error_info = _json.dumps(status_info.get("errors"))

            params = {
                "object_type": object_type,
                "entry_id": entry_id,
                "messaging_product": messaging_product,
                "wa_id": wa_id,
                "phone_number_id": phone_number_id,
                "message_body": message_body,
                "conversation_id": conversation_id,
                "origin_type": origin_type,
                "billable": billable,
                "pricing_model": pricing_model,
                "category": category,
                "status": status,
                "timestamp": timestamp,
                "field": field,
                "status_id": status_id,
                "error_info": error_info,
            }

            from baltra_sdk.legacy.dashboards_folder.models import WhatsappStatusUpdates

            with session.begin():
                model = WhatsappStatusUpdates(
                    object_type=params["object_type"],
                    entry_id=params["entry_id"],
                    messaging_product=params["messaging_product"],
                    wa_id=params["wa_id"],
                    phone_number_id=params["phone_number_id"],
                    message_body=params["message_body"],
                    conversation_id=params["conversation_id"],
                    origin_type=params["origin_type"],
                    billable=params["billable"],
                    pricing_model=params["pricing_model"],
                    category=params["category"],
                    status=params["status"],
                    timestamp=params["timestamp"],
                    field=params["field"],
                    status_id=params["status_id"],
                    error_info=params["error_info"],
                )
                session.add(model)
        finally:
            remove_session()


class PgConversationRepository(ConversationRepository):
    def upsert(self, wa_phone_id: str, user_phone: str, incoming_priority: Optional[str] = None) -> int:
        session = get_session()
        try:
            with session.begin():
                stmt = (
                    select(ScreeningConversationModel)
                    .where(
                        ScreeningConversationModel.wa_phone_id == wa_phone_id,
                        ScreeningConversationModel.user_phone == user_phone,
                    )
                    .with_for_update()
                )
                conversation = session.execute(stmt).scalars().first()
                now = datetime.now(timezone.utc)

                if conversation is None:
                    conversation = ScreeningConversationModel(
                        wa_phone_id=wa_phone_id,
                        user_phone=user_phone,
                        status_id=STATUS_WAITING.id,
                        status_changed_at=now,
                        last_webhook_at=now,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(conversation)
                    session.flush()
                else:
                    conversation.last_webhook_at = now
                    conversation.updated_at = now
                    if incoming_priority and conversation.status_id in {
                        STATUS_MOUNTING.id,
                        STATUS_PROCESSING.id,
                        STATUS_DELIVERING.id,
                    }:
                        _ConversationRunCoordinator.handle_cancel_request(
                            session=session,
                            conversation=conversation,
                            incoming_priority=incoming_priority,
                        )
                session.flush()
                return int(conversation.id)
        finally:
            remove_session()


class PgTempMessageRepository(TempMessageRepository):
    def insert(
        self,
        conversation_id: int,
        payload: Mapping[str, object],
        *,
        wa_type_id: Optional[int],
        wa_interactive_type_id: Optional[int],
    ) -> int:
        session = get_session()
        try:
            entry = (payload.get("entry") or [{}])[0]
            change = (entry.get("changes") or [{}])[0]
            value = change.get("value") or {}
            messages = value.get("messages") or [{}]
            message = messages[0] or {}
            message_id = message.get("id")
            contacts = value.get("contacts") or [{}]
            wa_id = contacts[0].get("wa_id")

            wa_type = None
            wa_interactive_type = None
            if wa_type_id == 1:
                wa_type = "text"
            elif wa_type_id == 2:
                wa_type = "interactive"
                if wa_interactive_type_id == 1:
                    wa_interactive_type = "button_reply"
                elif wa_interactive_type_id == 2:
                    wa_interactive_type = "list_reply"

            normalized_payload = json.loads(json.dumps(payload))

            logger = logging.getLogger(__name__)
            logger.debug(
                "Inserting temp_message: conversation_id=%s, message_id=%s, wa_type_id=%s, wa_interactive_type_id=%s",
                conversation_id,
                message_id,
                wa_type_id,
                wa_interactive_type_id,
            )

            with session.begin():
                model = TempMessageModel(
                    conversation_id=conversation_id,
                    message_id=message_id,
                    wa_id=wa_id,
                    body=normalized_payload,
                    wa_type=wa_type,
                    wa_interactive_type=wa_interactive_type,
                    wa_type_id=wa_type_id,
                    wa_interactive_type_id=wa_interactive_type_id,
                    processing=False,
                )
                session.add(model)
                session.flush()
                logger.debug(
                    "Inserted temp_message row id=%s for conversation_id=%s",
                    model.id,
                    model.conversation_id,
                )
                return int(model.id)
        finally:
            remove_session()


class StaticClassifierPolicy(ClassifierPolicy):
    def classify(self, payload: Mapping[str, object]) -> Tuple[Optional[int], Optional[int]]:
        plan = classify_payload(payload)
        return (plan.wa_type_id, plan.wa_interactive_type_id)


class PgWorkerQueueRepository(WorkerQueueRepository):
    def acquire_priority_batch(self, debounce_seconds: float) -> Optional[ConversationBatch]:
        session = get_session()
        try:
            with session.begin():
                batch = self._acquire_interactive_batch(session)
                if batch is None:
                    batch = self._acquire_grouped_batch(session, debounce_seconds)
                if batch is None:
                    return None
                return batch
        finally:
            remove_session()

    def release_batch(self, conversation_id: int, message_ids: Sequence[int]) -> None:
        session = get_session()
        try:
            with session.begin():
                if message_ids:
                    session.execute(
                        update(TempMessageModel)
                        .where(TempMessageModel.id.in_(list(message_ids)))
                        .values(processing=False)
                    )
                conversation = session.get(ScreeningConversationModel, conversation_id)
                if conversation is not None:
                    now = datetime.now(timezone.utc)
                    prev = conversation.status_id
                    conversation.status_id = STATUS_WAITING.id
                    conversation.status_changed_at = now
                    conversation.updated_at = now
                    logging.info(
                        "[WorkerQueue] conversation=%s status %s -> %s (release_batch)",
                        conversation_id,
                        status_from_id(prev).code,
                        status_from_id(conversation.status_id).code,
                    )
        finally:
            remove_session()

    def complete_batch(self, conversation_id: int, message_ids: Sequence[int]) -> None:
        session = get_session()
        try:
            with session.begin():
                if message_ids:
                    session.execute(
                        delete(TempMessageModel).where(TempMessageModel.id.in_(list(message_ids)))
                    )
                conversation = session.get(ScreeningConversationModel, conversation_id)
                if conversation is not None:
                    now = datetime.now(timezone.utc)
                    prev = conversation.status_id
                    conversation.status_id = STATUS_WAITING.id
                    conversation.status_changed_at = now
                    conversation.updated_at = now
                    logging.info(
                        "[WorkerQueue] conversation=%s status %s -> %s (complete_batch)",
                        conversation_id,
                        status_from_id(prev).code,
                        status_from_id(conversation.status_id).code,
                    )
        finally:
            remove_session()

    def recover_inflight_batches(self) -> int:
        return self._reset_processing_conversations()

    def requeue_stale_batches(self, older_than_seconds: float) -> int:
        if older_than_seconds <= 0:
            return self.recover_inflight_batches()
        threshold = datetime.now(timezone.utc) - timedelta(seconds=older_than_seconds)
        return self._reset_processing_conversations(threshold)

    def _acquire_interactive_batch(self, session) -> Optional[ConversationBatch]:
        sc = ScreeningConversationModel
        tm = TempMessageModel

        interactive_exists = exists().where(
            (tm.conversation_id == sc.id)
            & (tm.processing.is_(False))
            & ((tm.wa_type_id == 2) | (tm.wa_type == "interactive"))
        )

        conversation = (
            session.execute(
                select(sc)
                .where(sc.status_id == STATUS_WAITING.id)
                .where(interactive_exists)
                .order_by(sc.status_changed_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .first()
        )
        if conversation is None:
            return None

        message = (
            session.execute(
                select(tm)
                .where(
                    tm.conversation_id == conversation.id,
                    tm.processing.is_(False),
                    ((tm.wa_type_id == 2) | (tm.wa_type == "interactive")),
                )
                .order_by(tm.received_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .first()
        )
        if message is None:
            return None

            message.processing = True
            now = datetime.now(timezone.utc)
            prev = conversation.status_id
            conversation.status_id = STATUS_MOUNTING.id
            conversation.status_changed_at = now
            conversation.updated_at = now
            logging.info(
                "[WorkerQueue] conversation=%s status %s -> %s (interactive_acquire)",
                conversation.id,
                status_from_id(prev).code,
                status_from_id(conversation.status_id).code,
            )

        return self._build_batch(conversation, [message], PriorityClass.INTERACTIVE_SOLO)

    def _acquire_grouped_batch(self, session, debounce_seconds: float) -> Optional[ConversationBatch]:
        sc = ScreeningConversationModel
        tm = TempMessageModel

        threshold = datetime.now(timezone.utc) - timedelta(seconds=debounce_seconds)

        pending_exists = exists().where(
            (tm.conversation_id == sc.id) & (tm.processing.is_(False))
        )
        interactive_exists = exists().where(
            (tm.conversation_id == sc.id)
            & (tm.processing.is_(False))
            & ((tm.wa_type_id == 2) | (tm.wa_type == "interactive"))
        )
        old_message_exists = exists().where(
            (tm.conversation_id == sc.id)
            & (tm.processing.is_(False))
            & (tm.received_at <= threshold)
        )

        conversation = (
            session.execute(
                select(sc)
                .where(sc.status_id == STATUS_WAITING.id)
                .where(pending_exists)
                .where(old_message_exists)
                .where(~interactive_exists)
                .order_by(sc.status_changed_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .first()
        )
        if conversation is None:
            return None

        messages = (
            session.execute(
                select(tm)
                .where(
                    tm.conversation_id == conversation.id,
                    tm.processing.is_(False),
                )
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .all()
        )
        if not messages:
            return None

        for message in messages:
            message.processing = True

        now = datetime.now(timezone.utc)
        prev = conversation.status_id
        conversation.status_id = STATUS_MOUNTING.id
        conversation.status_changed_at = now
        conversation.updated_at = now
        logging.info(
            "[WorkerQueue] conversation=%s status %s -> %s (grouped_acquire)",
            conversation.id,
            status_from_id(prev).code,
            status_from_id(conversation.status_id).code,
        )

        return self._build_batch(conversation, messages, PriorityClass.TEXT_GROUPED)

    def _reset_processing_conversations(self, threshold: Optional[datetime] = None) -> int:
        session = get_session()
        try:
            with session.begin():
                stmt = (
                    select(ScreeningConversationModel.id)
                    .where(ScreeningConversationModel.status_id == STATUS_PROCESSING.id)
                    .with_for_update(skip_locked=True)
                )
                if threshold is not None:
                    stmt = stmt.where(ScreeningConversationModel.status_changed_at <= threshold)

                conversation_ids = [row for row in session.execute(stmt).scalars()]
                if not conversation_ids:
                    return 0

                session.execute(
                    update(TempMessageModel)
                    .where(TempMessageModel.conversation_id.in_(conversation_ids))
                    .values(processing=False)
                )
                session.execute(
                    update(ScreeningConversationModel)
                    .where(ScreeningConversationModel.id.in_(conversation_ids))
                    .values(
                        status_id=STATUS_WAITING.id,
                        status_changed_at=func.now(),
                        updated_at=func.now(),
                    )
                )
                return len(conversation_ids)
        finally:
            remove_session()

    def _build_batch(
        self,
        conversation_model: ScreeningConversationModel,
        message_models: Sequence[TempMessageModel],
        priority: PriorityClass,
    ) -> ConversationBatch:
        conversation = ScreeningConversation(
            id=conversation_model.id,
            wa_phone_id=conversation_model.wa_phone_id,
            user_phone=conversation_model.user_phone,
            status=status_from_id(conversation_model.status_id),
            status_changed_at=conversation_model.status_changed_at,
            last_webhook_at=conversation_model.last_webhook_at,
            created_at=conversation_model.created_at,
            updated_at=conversation_model.updated_at,
            active_run_id=conversation_model.active_run_id,
            active_thread_id=conversation_model.active_thread_id,
            active_run_priority=conversation_model.active_run_priority,
            cancel_requested=conversation_model.cancel_requested,
        )
        messages = [self._model_to_temp_message(model) for model in message_models]
        return ConversationBatch(conversation=conversation, messages=messages, priority=priority)

    @staticmethod
    def _model_to_temp_message(model: TempMessageModel) -> TempMessage:
        body = model.body
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                body = None
        return TempMessage(
            id=model.id,
            conversation_id=model.conversation_id,
            message_id=model.message_id,
            wa_id=model.wa_id,
            body=body,
            received_at=model.received_at,
            processing=model.processing,
            wa_type=model.wa_type,
            wa_interactive_type=model.wa_interactive_type,
            wa_type_id=model.wa_type_id,
            wa_interactive_type_id=model.wa_interactive_type_id,
            openai_message_id=model.openai_message_id,
        )


class _ConversationRunCoordinator:
    @staticmethod
    def handle_cancel_request(
        session,
        conversation: ScreeningConversationModel,
        incoming_priority: str,
    ) -> None:
        conversation.cancel_requested = True
        if conversation.status_id != STATUS_PROCESSING.id:
            logging.debug(
                "[RunCoordinator] Conversation %s status=%s (not processing); cancel flag stored only.",
                conversation.id,
                conversation.status_id,
            )
            _reset_processing_messages(session, conversation.id)
            return

        if not conversation.active_run_id:
            logging.debug(
                "[RunCoordinator] Conversation %s processing but no active_run_id; cancel flag stored.",
                conversation.id,
            )
            _reset_processing_messages(session, conversation.id)
            return

        if not should_cancel_active_run(conversation.active_run_priority, incoming_priority):
            logging.debug(
                "[RunCoordinator] Conversation %s active run priority=%s not cancelled for incoming=%s",
                conversation.id,
                conversation.active_run_priority,
                incoming_priority,
            )
            return

        thread_id = conversation.active_thread_id
        if not thread_id:
            logging.warning(
                "[RunCoordinator] Conversation %s missing thread_id for run %s; clearing metadata.",
                conversation.id,
                conversation.active_run_id,
            )
            conversation.active_run_id = None
            conversation.active_run_priority = None
            _reset_processing_messages(session, conversation.id)
            return

        try:
            client = get_openai_client()
            client.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=conversation.active_run_id,
            )
            logging.info(
                "Canceled active run %s for conversation %s via webhook.",
                conversation.active_run_id,
                conversation.id,
            )
        except Exception:
            logging.exception(
                "Failed to cancel active run %s for conversation %s via webhook.",
                conversation.active_run_id,
                conversation.id,
            )
        finally:
            conversation.active_run_id = None
            conversation.active_run_priority = None
            conversation.active_thread_id = None
            _reset_processing_messages(session, conversation.id)


def _reset_processing_messages(session, conversation_id: int) -> None:
    session.execute(
        update(TempMessageModel)
        .where(TempMessageModel.conversation_id == conversation_id)
        .values(processing=False)
    )
