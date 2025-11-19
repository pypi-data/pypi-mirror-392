from typing import Optional, Dict, Any, Iterator, Tuple, Protocol

class ElevenLabsConversationsRepositoryPort(Protocol):
    def list_conversations_from_elevenlabs(self, agent_id: Optional[str], cursor: Optional[str]) -> Dict[str, Any]:
        ...

    def get_conversation_from_elevenlabs(self, conversation_id: str) -> Dict[str, Any]:
        ...

    def stream_conversation_audio_from_elevenlabs(self, conversation_id: str) -> Tuple[Iterator[bytes], str]:
        ...
