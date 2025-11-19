from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, Optional, Tuple


class WebhookObjectStore(ABC):
    @abstractmethod
    def save_raw(self, payload: Mapping[str, object]) -> None:  # pragma: no cover - interface
        ...


class ConversationRepository(ABC):
    @abstractmethod
    def upsert(
        self,
        wa_phone_id: str,
        user_phone: str,
        incoming_priority: Optional[str] = None,
    ) -> int:  # returns conversation_id
        ...


class TempMessageRepository(ABC):
    @abstractmethod
    def insert(
        self,
        conversation_id: int,
        payload: Mapping[str, object],
        *,
        wa_type_id: Optional[int],
        wa_interactive_type_id: Optional[int],
    ) -> int:  # returns temp_message_id
        ...


class ClassifierPolicy(ABC):
    @abstractmethod
    def classify(self, payload: Mapping[str, object]) -> Tuple[Optional[int], Optional[int]]:
        ...
