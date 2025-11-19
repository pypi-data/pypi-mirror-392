from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class ScreeningMessage:
    """Value object representing an inbound message that must be processed."""

    wa_id_user: str
    wa_id_system: str
    whatsapp_msg_id: str
    message_payload: Dict[str, Any]
    raw_webhook: Dict[str, Any]


@dataclass(frozen=True)
class OutboundMessage:
    """Represents a WhatsApp payload ready to be dispatched."""

    payload: Any
    campaign_id: Optional[str] = None


@dataclass(frozen=True)
class ScreeningResult:
    """Result of processing a screening message."""

    outbound_messages: List[OutboundMessage] = field(default_factory=list)
    should_end_conversation: bool = False
    candidate_data: Optional[Dict[str, Any]] = None
    sent_by: Optional[str] = None
    message_id: Optional[str] = None
    raw_response_text: Optional[str] = None


@dataclass(frozen=True)
class CandidateSnapshot:
    """Lightweight representation of the candidate and current funnel state."""

    candidate_id: Optional[int]
    wa_id_user: str
    wa_id_system: str
    funnel_state: str
    current_question: Optional[str]
    next_question: Optional[str]
    first_question_flag: bool
    raw_payload: Dict[str, Any]


@dataclass(frozen=True)
class QuestionPrompt:
    """Represents a template that must be rendered and delivered."""

    keyword: str
    text_response: Optional[str]
    whatsapp_payload: Optional[Any]


@dataclass(frozen=True)
class ReminderSchedule:
    """Describes how and when reminders must be triggered for a company."""

    company_id: int
    schedule_type: str  # e.g. "fixed", "flexible", "application"
    window_start_minutes: Optional[int] = None
    window_end_minutes: Optional[int] = None
    time_of_day: Optional[str] = None  # "20:00" etc.
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReminderJob:
    """Represents a candidate that must receive a reminder message."""

    candidate_id: int
    wa_id_user: str
    wa_id_system: str
    kind: str  # "application" | "interview"
    schedule: ReminderSchedule
    context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReferenceSnapshot:
    """Reference conversation context loaded from the legacy schema."""

    reference_id: Optional[int]
    candidate_id: Optional[int]
    wa_id_reference: str
    question_id: Optional[int]
    thread_id: str
    assistant_id: str
    classifier_id: str
    raw_payload: Dict[str, Any]


@dataclass(frozen=True)
class ReferenceResult:
    """WhatsApp payload emitted by the reference conversation."""

    outbound_messages: List[OutboundMessage] = field(default_factory=list)
    should_end_conversation: bool = False
    reference_data: Optional[Dict[str, Any]] = None
    raw_response_text: Optional[str] = None
