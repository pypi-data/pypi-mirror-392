# Python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict

class StorageRepository(ABC):
    """
    Port: Storage contract for the Application layer.
    """

    @abstractmethod
    def upload_bytes(
        self,
        bucket: str,
        key: str,
        content: bytes,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        server_side_encryption: Optional[str] = "AES256",
    ) -> Optional[str]:
        """
        Uploads bytes and returns an accessible URL (public or presigned).
        Returns None on failure.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> bool:
        """Deletes an object. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    def generate_public_url(self, bucket: str, key: str) -> str:
        """Generates a public URL (depends on bucket policy)."""
        raise NotImplementedError

    def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> Optional[str]:
        """Optional: presigned GET URL."""
        return None