from __future__ import annotations

from typing import Iterable, Mapping, Protocol

from .entities import (
    CandidateSnapshot,
    QuestionPrompt,
    ReferenceResult,
    ReferenceSnapshot,
    ReminderJob,
    ReminderSchedule,
    ScreeningMessage,
    ScreeningResult,
)


class ScreeningEngine(Protocol):
    """Port responsible for orchestrating the screening conversation."""

    def process(self, message: ScreeningMessage, snapshot: CandidateSnapshot | None = None) -> ScreeningResult:
        """Process an inbound message and return the resulting actions."""
        ...


class CandidateRepository(Protocol):
    """Loads and mutates candidate data."""

    def get_or_create(self, wa_id_user: str, wa_id_system: str) -> CandidateSnapshot:
        ...


class QuestionRepository(Protocol):
    """Provides prompts/templates based on candidate state."""

    def build_prompt(self, candidate: CandidateSnapshot) -> QuestionPrompt:
        ...


class MessageRenderer(Protocol):
    """Transforms prompts into final WhatsApp payloads."""

    def render(self, prompt: QuestionPrompt, candidate: CandidateSnapshot) -> ScreeningResult:
        ...


class IntentClassifier(Protocol):
    """Determines the conversational intent derived from a message."""

    def classify(self, message: ScreeningMessage, candidate: CandidateSnapshot) -> str:
        ...


class ConversationProgression(Protocol):
    """Persists answers and advances the questionnaire cursor."""

    def advance(self, candidate: CandidateSnapshot, answer_text: str) -> CandidateSnapshot | None:
        ...


class EligibilityEvaluator(Protocol):
    """Evaluates candidate eligibility for the available roles."""

    def evaluate(self, candidate: CandidateSnapshot) -> None:
        """Trigger the eligibility evaluation (sync or async)."""
        ...


class ReminderRepository(Protocol):
    """Provides the list of reminder jobs that must be dispatched."""

    def list_application_jobs(self) -> Iterable[ReminderJob]:
        ...

    def list_interview_jobs(self, schedule: ReminderSchedule) -> Iterable[ReminderJob]:
        ...

    def mark_sent(self, job: ReminderJob) -> None:
        ...


class ReminderNotifier(Protocol):
    """Sends reminder messages via WhatsApp (or the configured channel)."""

    def send(self, job: ReminderJob) -> None:
        ...


class ReferenceRepository(Protocol):
    """Loads reference conversations for the reference WhatsApp channel."""

    def get_or_create(self, wa_id_reference: str) -> ReferenceSnapshot:
        ...

    def mark_assessment(self, snapshot: ReferenceSnapshot, classifier_payload: Mapping[str, object]) -> None:
        ...


class ReferenceConversation(Protocol):
    """Handles messages for the reference channel."""

    def handle(
        self,
        snapshot: ReferenceSnapshot,
        message_body: str,
        whatsapp_msg_id: str | None = None,
    ) -> ReferenceResult:
        ...


class FunnelAnalytics(Protocol):
    """Tracks funnel-related events (Mixpanel in the legacy implementation)."""

    def track(self, event_name: str, candidate_id: int, company_id: int, *, reason: str | None = None) -> None:
        ...
