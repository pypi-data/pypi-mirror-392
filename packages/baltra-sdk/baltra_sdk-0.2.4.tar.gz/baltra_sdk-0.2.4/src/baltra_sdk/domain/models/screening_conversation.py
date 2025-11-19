from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Mapping, Optional, List

from baltra_sdk.domain.dispatch import PriorityClass

@dataclass(frozen=True, slots=True)
class ScreeningConversationStatus:
    id: int
    code: str
    description: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ScreeningConversation:
    id: Optional[int]
    wa_phone_id: str
    user_phone: str
    status: ScreeningConversationStatus
    status_changed_at: Optional[datetime]
    last_webhook_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    active_run_id: Optional[str] = None
    active_thread_id: Optional[str] = None
    active_run_priority: Optional[str] = None
    cancel_requested: bool = False


@dataclass(frozen=True, slots=True)
class TempMessage:
    id: Optional[int]
    conversation_id: Optional[int]
    message_id: Optional[str]
    wa_id: Optional[str]
    body: Optional[Mapping[str, Any]]
    received_at: Optional[datetime]
    processing: bool
    wa_type: Optional[str] = None
    wa_interactive_type: Optional[str] = None
    wa_type_id: Optional[int] = None
    wa_interactive_type_id: Optional[int] = None
    openai_message_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ConversationBatch:
    conversation: ScreeningConversation
    messages: List[TempMessage]
    priority: PriorityClass


def serialize_conversation_batch(batch: ConversationBatch) -> Dict[str, Any]:
    conversation = batch.conversation
    return {
        "conversation": {
            "id": conversation.id,
            "wa_phone_id": conversation.wa_phone_id,
            "user_phone": conversation.user_phone,
            "status": conversation.status.code,
        },
        "priority": batch.priority.value,
        "messages": [
            {
                "id": message.id,
                "message_id": message.message_id,
                "wa_id": message.wa_id,
                "wa_type": message.wa_type,
                "wa_type_id": message.wa_type_id,
                "wa_interactive_type": message.wa_interactive_type,
                "wa_interactive_type_id": message.wa_interactive_type_id,
                "received_at": message.received_at.isoformat() if message.received_at else None,
                "payload": message.body,
            }
            for message in batch.messages
        ],
    }


class ScreeningConversationStatusCode(IntEnum):
    WAITING = 1
    PROCESSING = 2
    FINISHED = 3
    MOUNTING = 4
    DELIVERING = 5


_STATUS_DEFINITIONS: Dict[ScreeningConversationStatusCode, ScreeningConversationStatus] = {
    ScreeningConversationStatusCode.WAITING: ScreeningConversationStatus(
        id=ScreeningConversationStatusCode.WAITING.value,
        code="waiting",
        description="Conversation ready to be picked by the worker",
    ),
    ScreeningConversationStatusCode.PROCESSING: ScreeningConversationStatus(
        id=ScreeningConversationStatusCode.PROCESSING.value,
        code="processing",
        description="Conversation is being processed by worker/OpenAI batch",
    ),
    ScreeningConversationStatusCode.FINISHED: ScreeningConversationStatus(
        id=ScreeningConversationStatusCode.FINISHED.value,
        code="finished",
        description="Conversation processed and no longer pending",
    ),
    ScreeningConversationStatusCode.MOUNTING: ScreeningConversationStatus(
        id=ScreeningConversationStatusCode.MOUNTING.value,
        code="mounting",
        description="Conversation acquired by worker; preparing OpenAI run",
    ),
    ScreeningConversationStatusCode.DELIVERING: ScreeningConversationStatus(
        id=ScreeningConversationStatusCode.DELIVERING.value,
        code="delivering",
        description="Conversation finished processing and delivering outbound messages",
    ),
}


def status_from_enum(code: ScreeningConversationStatusCode) -> ScreeningConversationStatus:
    return _STATUS_DEFINITIONS[code]


def status_from_id(status_id: int) -> ScreeningConversationStatus:
    try:
        enum_code = ScreeningConversationStatusCode(status_id)
    except ValueError:
        return ScreeningConversationStatus(id=status_id, code="unknown", description=None)
    return status_from_enum(enum_code)


STATUS_WAITING = status_from_enum(ScreeningConversationStatusCode.WAITING)
STATUS_PROCESSING = status_from_enum(ScreeningConversationStatusCode.PROCESSING)
STATUS_FINISHED = status_from_enum(ScreeningConversationStatusCode.FINISHED)
STATUS_MOUNTING = status_from_enum(ScreeningConversationStatusCode.MOUNTING)
STATUS_DELIVERING = status_from_enum(ScreeningConversationStatusCode.DELIVERING)
