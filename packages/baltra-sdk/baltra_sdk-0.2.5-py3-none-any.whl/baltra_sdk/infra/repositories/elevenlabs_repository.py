import requests
from typing import Optional, Dict, Any, Iterator, Tuple
from flask import current_app

class ElevenlabsRepository:
    def _base(self) -> str:
        base = (current_app.config.get("ELEVEN_BASE_URL") or "https://api.elevenlabs.io").rstrip("/")
        return base
    def _key(self) -> str:
        k = current_app.config.get("ELEVEN_API_KEY")
        if not k:
            raise RuntimeError("ELEVEN_API_KEY is required")
        return k
    def _timeout(self) -> int:
        return int(current_app.config.get("REQUEST_TIMEOUT", 60))

    def _json(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        r = requests.request(method, url, timeout=self._timeout(), **kwargs)
        if not (200 <= r.status_code < 300):
            raise requests.HTTPError(f"{r.status_code} {r.reason}", response=r)
        return r.json()

    def list_conversations_from_elevenlabs(self, agent_id: Optional[str], cursor: Optional[str]) -> Dict[str, Any]:
        url = f"{self._base()}/v1/convai/conversations"
        headers = {"xi-api-key": self._key(), "Accept": "application/json"}
        params: Dict[str, str] = {}
        if agent_id:
            params["agent_id"] = agent_id
        if cursor:
            params["cursor"] = cursor
        return self._json("GET", url, headers=headers, params=params)

    def get_conversation_from_elevenlabs(self, conversation_id: str) -> Dict[str, Any]:
        url = f"{self._base()}/v1/convai/conversations/{conversation_id}"
        headers = {"xi-api-key": self._key(), "Accept": "application/json"}
        return self._json("GET", url, headers=headers)

    def stream_conversation_audio_from_elevenlabs(self, conversation_id: str) -> Tuple[Iterator[bytes], str]:
        url = f"{self._base()}/v1/convai/conversations/{conversation_id}/audio"
        headers = {"xi-api-key": self._key()}
        r = requests.get(url, headers=headers, timeout=self._timeout(), stream=True)
        if not (200 <= r.status_code < 300):
            raise requests.HTTPError(f"{r.status_code} {r.reason}", response=r)
        ctype = r.headers.get("Content-Type", "application/octet-stream")
        def gen():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return gen(), ctype
