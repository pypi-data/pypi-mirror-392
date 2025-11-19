from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Mapping, Optional


class BatchMode(Enum):
    SOLO = "solo"
    GROUPED = "grouped"


class PriorityClass(Enum):
    INTERACTIVE_SOLO = "interactive_solo"
    TEXT_GROUPED = "text_grouped"
    OTHER_IMMEDIATE = "other_immediate"


class WaMessageTypeId(IntEnum):
    TEXT = 1
    INTERACTIVE = 2


class WaInteractiveTypeId(IntEnum):
    BUTTON_REPLY = 1
    LIST_REPLY = 2


@dataclass(frozen=True)
class DispatchPlan:
    batch_mode: BatchMode
    priority: PriorityClass
    wa_type_id: Optional[int]
    wa_interactive_type_id: Optional[int]


def classify_payload(body: Mapping[str, object]) -> DispatchPlan:
    """Classify an incoming WhatsApp webhook payload into a dispatch plan.

    No DB lookups; uses static enums/mappings. Only prioritizes interactive button/list as SOLO; text is GROUPED.
    All other message types default to immediate SOLO to preserve previous behavior.
    """
    try:
        value = (body.get("entry") or [{}])[0].get("changes")[0]["value"]  # type: ignore[index]
        message = (value.get("messages") or [None])[0]  # type: ignore[assignment]
    except Exception:
        # Fallback: treat as other immediate
        return DispatchPlan(
            batch_mode=BatchMode.SOLO,
            priority=PriorityClass.OTHER_IMMEDIATE,
            wa_type_id=None,
            wa_interactive_type_id=None,
        )

    if not isinstance(message, Mapping):
        return DispatchPlan(
            batch_mode=BatchMode.SOLO,
            priority=PriorityClass.OTHER_IMMEDIATE,
            wa_type_id=None,
            wa_interactive_type_id=None,
        )

    msg_type = message.get("type")

    if msg_type == "text":
        return DispatchPlan(
            batch_mode=BatchMode.GROUPED,
            priority=PriorityClass.TEXT_GROUPED,
            wa_type_id=WaMessageTypeId.TEXT.value,
            wa_interactive_type_id=None,
        )

    if msg_type == "interactive":
        interactive = message.get("interactive")
        sub_type = interactive.get("type") if isinstance(interactive, Mapping) else None
        if sub_type == "button_reply":
            return DispatchPlan(
                batch_mode=BatchMode.SOLO,
                priority=PriorityClass.INTERACTIVE_SOLO,
                wa_type_id=WaMessageTypeId.INTERACTIVE.value,
                wa_interactive_type_id=WaInteractiveTypeId.BUTTON_REPLY.value,
            )
        if sub_type == "list_reply":
            return DispatchPlan(
                batch_mode=BatchMode.SOLO,
                priority=PriorityClass.INTERACTIVE_SOLO,
                wa_type_id=WaMessageTypeId.INTERACTIVE.value,
                wa_interactive_type_id=WaInteractiveTypeId.LIST_REPLY.value,
            )

    # Other kinds: template, flow(nfm_reply), document, reaction, etc. → immediate
    return DispatchPlan(
        batch_mode=BatchMode.SOLO,
        priority=PriorityClass.OTHER_IMMEDIATE,
        wa_type_id=None,
        wa_interactive_type_id=None,
    )

