from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable, Mapping

from flask import current_app
from sqlalchemy.exc import IntegrityError

from baltra_sdk.infra.screening.repositories.sqlalchemy_reference_repository import (
    SqlAlchemyReferenceRepository,
)
from baltra_sdk.infra.screening.services.message_store import store_message_reference
from baltra_sdk.infra.screening.services.solid_template_renderer import SolidTemplateRenderer
from baltra_sdk.legacy.dashboards_folder.models import CandidateReferences, db
from baltra_sdk.shared.utils.screening.openai_utils import add_msg_to_thread, get_openai_client
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input
from baltra_sdk.shared.utils.whatsapp_utils import send_message

_logger = logging.getLogger(__name__)


class ReferenceContactService:
    """Handles candidate-provided references using SOLID repositories."""

    def __init__(
        self,
        session=None,
        template_renderer: SolidTemplateRenderer | None = None,
        reference_repository: SqlAlchemyReferenceRepository | None = None,
        send_message_fn: Callable[[Any, str, str | None], Any] | None = None,
        message_store_fn: Callable[[str, Mapping[str, Any], str, str, str], None] | None = None,
        client_factory: Callable[[], Any] | None = None,
        owner_wa_id: str | None = None,
    ) -> None:
        self.session = session or db.session
        self.renderer = template_renderer or SolidTemplateRenderer()
        self.reference_repository = reference_repository or SqlAlchemyReferenceRepository()
        self.send_message_fn = send_message_fn or send_message
        self.message_store_fn = message_store_fn or store_message_reference
        self.client_factory = client_factory or get_openai_client
        self.owner_wa_id = owner_wa_id

    # ------------------------------------------------------------------
    def handle_reference_submission(self, candidate_payload: Mapping[str, Any], raw_input: str) -> bool:
        reference_wa_id = self._normalize_wa_id(raw_input)
        if not reference_wa_id:
            _logger.warning("Invalid reference payload provided by candidate %s", candidate_payload.get("candidate_id"))
            return False

        if not self._store_reference_contact(candidate_payload, reference_wa_id):
            return False

        snapshot = self.reference_repository.get_or_create(reference_wa_id)
        if not snapshot:
            _logger.error("Reference repository failed to build snapshot for %s", reference_wa_id)
            return False

        reference_data = dict(snapshot.raw_payload)
        reference_data.setdefault("first_name", candidate_payload.get("first_name"))
        reference_data.setdefault("role_context", "Baltra ayuda a las empresas a validar referencias laborales.")
        return self._notify_reference(reference_data)

    # ------------------------------------------------------------------
    def _store_reference_contact(self, candidate_payload: Mapping[str, Any], reference_wa_id: str) -> bool:
        candidate_id = candidate_payload.get("candidate_id")
        set_id = candidate_payload.get("set_id")
        question_id = candidate_payload.get("question_id")
        if not all([candidate_id, set_id, question_id]):
            _logger.warning("Reference contact missing identifiers; candidate=%s", candidate_id)
            return False

        try:
            reference = (
                self.session.query(CandidateReferences)
                .filter_by(candidate_id=candidate_id, set_id=set_id, question_id=question_id)
                .first()
            )
            if reference:
                reference.reference_wa_id = reference_wa_id
            else:
                reference = CandidateReferences(
                    candidate_id=candidate_id,
                    set_id=set_id,
                    question_id=question_id,
                    reference_wa_id=reference_wa_id,
                )
                self.session.add(reference)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            _logger.exception("Failed to store reference contact for candidate %s", candidate_id)
            return False
        except Exception:
            self.session.rollback()
            _logger.exception("Unexpected error storing reference contact for candidate %s", candidate_id)
            return False

    def _notify_reference(self, reference_data: Mapping[str, Any]) -> bool:
        owner_wa_id = self.owner_wa_id or current_app.config.get("wa_id_ID_owner")
        if not owner_wa_id:
            _logger.warning("Owner WhatsApp ID missing; cannot send reference notification.")
            return False

        rendered = self.renderer.render("contact_reference", reference_data)
        payload = rendered.payload or get_text_message_input(reference_data.get("wa_id"), rendered.text or "")
        if not payload:
            _logger.warning("No payload rendered for contact_reference template.")
            return False

        client = self.client_factory()
        message_text = rendered.text or "Contacto de referencia recibido."
        message_id, sent_by = add_msg_to_thread(reference_data["thread_id"], message_text, "assistant", client)
        response = self.send_message_fn(payload, owner_wa_id, "reference_check")

        whatsapp_msg_id = self._extract_outbound_id(response)
        try:
            self.message_store_fn(message_id, reference_data, sent_by, message_text, whatsapp_msg_id or "")
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to store reference notification for reference_id=%s", reference_data.get("reference_id"))
        return getattr(response, "status_code", None) == 200

    @staticmethod
    def _extract_outbound_id(response: Any) -> str | None:
        if not response or getattr(response, "status_code", None) != 200:
            return None
        try:
            payload = json.loads(response.text)
            return payload["messages"][0]["id"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def _normalize_wa_id(raw_input: str) -> str | None:
        digits = re.sub(r"[^0-9]", "", raw_input or "")
        if not digits:
            return None
        if digits.startswith("521") and len(digits) == 13:
            return digits
        if digits.startswith("52") and len(digits) == 12:
            return "521" + digits[2:]
        if len(digits) == 10:
            return "521" + digits
        if digits.startswith("1") and len(digits) == 11:
            return "52" + digits
        if not digits.startswith("521"):
            return "521" + digits
        return digits
