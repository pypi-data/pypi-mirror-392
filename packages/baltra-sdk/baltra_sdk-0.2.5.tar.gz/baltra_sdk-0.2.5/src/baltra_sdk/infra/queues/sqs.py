from __future__ import annotations

import json
from typing import Optional

import boto3

from baltra_sdk.domain.models.screening_conversation import ConversationBatch, serialize_conversation_batch
from baltra_sdk.domain.ports.worker_queue import BatchQueuePublisher


class SqsBatchPublisher(BatchQueuePublisher):
    """Publicador de lotes hacia Amazon SQS."""

    def __init__(
        self,
        queue_url: str,
        *,
        client: Optional[boto3.client] = None,
        message_attributes: Optional[dict] = None,
    ) -> None:
        self._queue_url = queue_url
        self._client = client or boto3.client("sqs")
        self._base_attributes = message_attributes or {}

    def publish(
        self,
        batch: ConversationBatch,
        *,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None,
    ) -> None:
        payload = serialize_conversation_batch(batch)
        params = {
            "QueueUrl": self._queue_url,
            "MessageBody": json.dumps(payload, default=_json_default),
        }

        if message_group_id is not None:
            params["MessageGroupId"] = message_group_id
        if message_deduplication_id is not None:
            params["MessageDeduplicationId"] = message_deduplication_id

        if self._base_attributes:
            params["MessageAttributes"] = self._base_attributes

        self._client.send_message(**params)


def _json_default(value):  # pragma: no cover - fallback serializer
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
