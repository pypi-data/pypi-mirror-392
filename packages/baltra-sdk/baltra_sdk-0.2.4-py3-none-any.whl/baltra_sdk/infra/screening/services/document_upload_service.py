from __future__ import annotations

import copy
import logging
import threading
import time
from contextlib import nullcontext
from typing import Any, Callable, Mapping, MutableMapping, Optional

from flask import current_app, has_app_context

from baltra_sdk.infra.screening.services.candidate_state_service import CandidateStateService
from baltra_sdk.shared.utils.screening.media_handler import ScreeningMediaHandler

_logger = logging.getLogger(__name__)


class DocumentUploadService:
    """Processes WhatsApp Flow document payloads through SOLID services."""

    def __init__(
        self,
        candidate_state: CandidateStateService | None = None,
        media_handler_factory: Callable[[], ScreeningMediaHandler] | None = None,
        background_runner: Callable[[Callable[[], None]], None] | None = None,
        context_factory: Callable[[], Any] | None = None,
        processing_delay: float = 2.0,
    ) -> None:
        self.state = candidate_state or CandidateStateService()
        self.media_handler_factory = media_handler_factory or ScreeningMediaHandler
        self.background_runner = background_runner or self._run_in_thread
        self.context_factory = context_factory
        self.processing_delay = max(processing_delay, 0.0)

    # ------------------------------------------------------------------
    def handle_flow_submission(
        self,
        candidate_payload: Mapping[str, Any],
        flow_payload: Mapping[str, Any],
        whatsapp_msg_id: str | None = None,
    ) -> str:
        """Acknowledges a flow document submission and kicks off background processing."""
        total = self._count_documents(flow_payload)
        ack = f"📄 Recibí {total} documento(s). Los estoy verificando, esto puede tomar unos segundos..."
        payload_copy = copy.deepcopy(dict(candidate_payload))
        flow_copy = copy.deepcopy(dict(flow_payload))
        self.background_runner(
            lambda: self._process_async(payload_copy, flow_copy, whatsapp_msg_id)
        )
        return ack

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _process_async(
        self,
        candidate_payload: MutableMapping[str, Any],
        flow_payload: MutableMapping[str, Any],
        whatsapp_msg_id: str | None,
    ) -> None:
        try:
            with self._app_context():
                if self.processing_delay:
                    time.sleep(self.processing_delay)
                handler = self.media_handler_factory()
                results = handler.process_flow_media(candidate_payload, flow_payload)
                answer_text, json_data = self._build_answer_payload(flow_payload, results)
                persisted = self.state.store_document_answer(candidate_payload, answer_text, json_data)
                if not persisted:
                    _logger.warning(
                        "Document upload answer not persisted for candidate %s",
                        candidate_payload.get("candidate_id"),
                    )
        except Exception:  # noqa: BLE001
            _logger.exception(
                "Error processing documents for candidate %s",
                candidate_payload.get("candidate_id"),
            )
            error_answer = "Error procesando documentos: ocurrió un problema inesperado"
            error_json = {
                "processing_status": "error",
                "error_message": "unexpected_failure",
                "flow_token": flow_payload.get("flow_token", "request_documents"),
                "s3_processed": False,
            }
            self.state.store_document_answer(candidate_payload, error_answer, error_json)

    def _build_answer_payload(
        self,
        flow_payload: Mapping[str, Any],
        results: Mapping[str, Any],
    ) -> tuple[str, dict]:
        processed = int(results.get("processed_count", 0) or 0)
        failed = int(results.get("failed_count", 0) or 0)
        flow_token = flow_payload.get("flow_token", "request_documents")

        if processed > 0:
            text = f"Documentos procesados: {processed} archivo(s) subidos exitosamente a S3"
            if failed:
                text += f" ({failed} fallaron)"
            payload = {
                "media_count": processed,
                "media_ids": results.get("media_ids", []),
                "flow_token": flow_token,
                "processing_status": "completed",
                "failed_count": failed,
                "errors": results.get("errors", []),
                "s3_processed": True,
            }
        else:
            text = "Error procesando documentos: todos los archivos fallaron"
            payload = {
                "media_count": 0,
                "flow_token": flow_token,
                "processing_status": "failed",
                "errors": results.get("errors", []),
                "s3_processed": False,
            }
        return text, payload

    def _count_documents(self, flow_payload: Mapping[str, Any]) -> int:
        images = flow_payload.get("images") or []
        documents = flow_payload.get("documents") or []
        return len(images) + len(documents)

    def _run_in_thread(self, func: Callable[[], None]) -> None:
        thread = threading.Thread(target=func, daemon=True)
        thread.start()

    def _app_context(self):
        factory = self.context_factory
        if factory:
            return factory()
        if has_app_context():
            return current_app.app_context()
        return nullcontext()
