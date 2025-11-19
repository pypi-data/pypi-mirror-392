from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional


class DocumentVerificationProvider(ABC):
    @abstractmethod
    def verify_rfc(self, rfc: str) -> Tuple[bool, Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def verify_ine(self, front_url: str, back_url: str) -> Tuple[bool, Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def verify_curp_nss(self, curp: str) -> Tuple[bool, Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def format_message(self, result: Dict[str, Any], doc_type: str) -> str:
        raise NotImplementedError


class CandidateMediaRepository(ABC):
    @abstractmethod
    def create_text_media(self, candidate_id: int, company_id: int, subtype: str, value: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def update_verification(self, media_id: int, verified: bool, result: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_media_s3_url(self, media_id: int) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def get_candidate_company_id(self, candidate_id: int) -> int:
        raise NotImplementedError

