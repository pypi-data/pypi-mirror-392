from typing import Dict, Any, Tuple, Optional
from baltra_sdk.domain.document_verification.ports import DocumentVerificationProvider
from baltra_sdk.shared.utils.document_verification.tu_identidad_api import TuIdentidadAPI


class TuIdentidadProvider(DocumentVerificationProvider):
    def __init__(self, api: Optional[TuIdentidadAPI] = None):
        self.api = api or TuIdentidadAPI()

    def verify_rfc(self, rfc: str) -> Tuple[bool, Dict[str, Any]]:
        return self.api.verify_rfc_string(rfc)

    def verify_ine(self, front_url: str, back_url: str) -> Tuple[bool, Dict[str, Any]]:
        return self.api.verify_ine_documents(front_url, back_url)

    def verify_curp_nss(self, curp: str) -> Tuple[bool, Dict[str, Any]]:
        return self.api.verify_curp_nss(curp)

    def format_message(self, result: Dict[str, Any], doc_type: str) -> str:
        return self.api.get_validation_message(result, doc_type)

