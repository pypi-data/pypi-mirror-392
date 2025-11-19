from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from baltra_sdk.domain.models.screening_conversation import ConversationBatch
from baltra_sdk.domain.ports.worker_queue import WorkerQueueRepository


@dataclass(frozen=True)
class WorkerQueueService:
    repository: WorkerQueueRepository
    debounce_seconds: float = 5.0

    def acquire_batch(self) -> Optional[ConversationBatch]:
        """Fetch next batch based on priority rules."""
        return self.repository.acquire_priority_batch(self.debounce_seconds)

    def release_batch(self, batch: ConversationBatch) -> None:
        """Release a batch (used when dispatching fails before handing off)."""
        message_ids = [msg.id for msg in batch.messages if msg.id is not None]
        if batch.conversation.id is None:
            raise ValueError("Conversation lacks an ID; cannot release batch")
        self.repository.release_batch(batch.conversation.id, message_ids)

    def complete_batch(self, batch: ConversationBatch) -> None:
        """Delete processed messages and return the conversation to waiting state."""
        message_ids = [msg.id for msg in batch.messages if msg.id is not None]
        if batch.conversation.id is None:
            raise ValueError("Conversation lacks an ID; cannot complete batch")
        self.repository.complete_batch(batch.conversation.id, message_ids)

    def recover_inflight_batches(self) -> int:
        """Reset conversations left in PROCESSING (used on startup)."""
        return self.repository.recover_inflight_batches()

    def requeue_stale_batches(self, older_than_seconds: float) -> int:
        """Reset conversations that exceeded the processing TTL."""
        return self.repository.requeue_stale_batches(older_than_seconds)
