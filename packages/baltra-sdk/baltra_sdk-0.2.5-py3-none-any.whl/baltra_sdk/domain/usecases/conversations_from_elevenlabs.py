from typing import Optional, Dict, Any, Iterator, Tuple
from baltra_sdk.domain.ports.elevenlabs_conversations import ElevenLabsConversationsRepository

class GetAllConversationsFromElevenlabs:
    def __init__(self, repo: ElevenLabsConversationsRepository):
        self.repo = repo
    def execute(self, agent_id: Optional[str], cursor: Optional[str]) -> Dict[str, Any]:
        return self.repo.list_conversations_from_elevenlabs(agent_id, cursor)

class GetConversationDetailsFromElevenlabs:
    def __init__(self, repo: ElevenLabsConversationsRepository):
        self.repo = repo
    def execute(self, conversation_id: str) -> Dict[str, Any]:
        return self.repo.get_conversation_from_elevenlabs(conversation_id)

class StreamConversationAudioFromElevenlabs:
    def __init__(self, repo: ElevenLabsConversationsRepository):
        self.repo = repo
    def execute(self, conversation_id: str) -> Tuple[Iterator[bytes], str]:
        return self.repo.stream_conversation_audio_from_elevenlabs(conversation_id)
