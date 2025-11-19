from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from baltra_sdk.domain.models.screening_conversation import ConversationBatch


class WorkerQueueRepository(ABC):
    @abstractmethod
    def acquire_priority_batch(self, debounce_seconds: float) -> Optional[ConversationBatch]:
        """Fetch the next conversation batch respecting priority rules and mark it as processing."""

    @abstractmethod
    def release_batch(self, conversation_id: int, message_ids: Sequence[int]) -> None:
        """Release a previously acquired batch (set messages back to pending and conversation to waiting)."""

    @abstractmethod
    def complete_batch(self, conversation_id: int, message_ids: Sequence[int]) -> None:
        """Persist completion: delete processed messages and return the conversation to waiting state."""

    @abstractmethod
    def recover_inflight_batches(self) -> int:
        """Return conversations stuck in PROCESSING to WAITING (used at startup)."""

    @abstractmethod
    def requeue_stale_batches(self, older_than_seconds: float) -> int:
        """Return conversations that exceeded the processing TTL back to WAITING."""


class BatchQueuePublisher(ABC):
    @abstractmethod
    def publish(
        self,
        batch: ConversationBatch,
        *,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None,
    ) -> None:
        """Publish the batch to an external queue (e.g., SQS)."""
