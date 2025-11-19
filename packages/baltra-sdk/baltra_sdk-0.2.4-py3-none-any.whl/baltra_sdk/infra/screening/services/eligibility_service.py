from __future__ import annotations

import logging
import json
from dataclasses import dataclass
from threading import Thread
from typing import Callable, Mapping

from baltra_sdk.domain.screening.entities import CandidateSnapshot
from baltra_sdk.domain.screening.ports import EligibilityEvaluator
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.shared.utils.screening.openai_utils import (
    add_msg_to_thread,
    evaluate_role_eligibility,
    get_openai_client,
)
from baltra_sdk.shared.utils.screening.sql_utils import (
    apply_candidate_updates,
    get_company_roles_with_criteria,
    get_eligibility_questions_and_answers,
    update_candidate_eligible_roles,
    update_funnel_state,
    update_screening_rejection,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import (
    get_keyword_response_from_db,
    get_text_message_input,
)
from baltra_sdk.shared.utils.screening.whatsapp_utils import send_message
from baltra_sdk.infra.screening.services.message_store import store_message


_logger = logging.getLogger(__name__)
_ERROR_MESSAGE = "Disculpa, ocurrió un error técnico"
_NO_ROLES_MESSAGE = (
    "Después de revisar tus respuestas, lamentablemente no calificas para ninguno de los puestos disponibles en "
    "este momento. Te agradecemos tu interés y te animamos a aplicar nuevamente en el futuro."
)


@dataclass
class ThreadedEligibilityEvaluator(EligibilityEvaluator):
    """Reimplements the legacy eligibility thread using SOLID dependencies."""

    context_factory: Callable[[], object]

    def evaluate(self, candidate: CandidateSnapshot) -> None:
        thread = Thread(
            target=self._run_in_context,
            args=(candidate,),
            name=f"eligibility-{candidate.candidate_id}",
            daemon=True,
        )
        thread.start()

    def _run_in_context(self, candidate: CandidateSnapshot) -> None:
        with self.context_factory():
            try:
                self._run(candidate)
            except Exception:  # noqa: BLE001
                _logger.exception("Eligibility evaluation failed for candidate %s", candidate.candidate_id)

    def _run(self, candidate: CandidateSnapshot) -> None:
        candidate_data = dict(candidate.raw_payload or {})
        candidate_id = candidate_data.get("candidate_id")
        company_id = candidate_data.get("company_id")
        wa_id_user = candidate_data.get("wa_id")
        wa_id_system = candidate_data.get("wa_id_system")
        thread_id = candidate_data.get("thread_id")
        if candidate_id is None or company_id is None or not wa_id_user or not wa_id_system or not thread_id:
            _logger.warning(
                "Missing identifiers to run eligibility (candidate_id=%s company_id=%s wa_id=%s wa_id_system=%s thread_id=%s)",
                candidate_id,
                company_id,
                wa_id_user,
                wa_id_system,
                thread_id,
            )
            return

        client = get_openai_client()

        if not update_candidate_eligible_roles(candidate_id, ["run_in_progress"]):
            _logger.error("Failed to mark eligibility run in progress for candidate %s", candidate_id)
            return

        roles = get_company_roles_with_criteria(company_id) or []
        if not roles:
            _logger.warning("No active roles configured for company %s during eligibility run.", company_id)
            self._send_text(candidate_data, wa_id_system, client, _ERROR_MESSAGE)
            update_candidate_eligible_roles(candidate_id, [])
            return

        eligible_role_ids: list[int] = []
        for role in roles:
            q_and_a = get_eligibility_questions_and_answers(candidate_id, company_id, role)
            if not q_and_a:
                _logger.warning(
                    "No eligibility questions for candidate=%s company=%s role_id=%s",
                    candidate_id,
                    company_id,
                    role.get("role_id"),
                )
                continue
            try:
                is_eligible = evaluate_role_eligibility(
                    client=client,
                    role_data=role,
                    questions_and_answers=q_and_a,
                    candidate_id=candidate_id,
                    company_id=company_id,
                )
            except Exception:  # noqa: BLE001
                _logger.exception("Eligibility assistant failed for candidate=%s role=%s", candidate_id, role.get("role_id"))
                continue

            if is_eligible:
                eligible_role_ids.append(role["role_id"])

        if not update_candidate_eligible_roles(candidate_id, eligible_role_ids):
            _logger.error("Failed to persist eligible roles for candidate %s", candidate_id)
            self._send_text(candidate_data, wa_id_system, client, _ERROR_MESSAGE)
            update_candidate_eligible_roles(candidate_id, [])
            return

        if eligible_role_ids:
            if self._send_role_selection(candidate_data, wa_id_system, client):
                _logger.info(
                    "Eligibility evaluation completed for candidate %s (eligible roles=%s)",
                    candidate_id,
                    eligible_role_ids,
                )
                return
            _logger.warning("Role selection template missing for candidate %s", candidate_id)
            self._send_text(
                candidate_data,
                wa_id_system,
                client,
                "Encontramos roles compatibles y te enviaremos los detalles en breve.",
            )
            return

        if candidate_data.get("funnel_state") == "screening_in_progress":
            try:
                update_funnel_state(candidate_id, "rejected")
                update_screening_rejection(candidate_id, "No califica para ningún puesto")
                candidate_data["funnel_state"] = "rejected"
            except Exception:  # noqa: BLE001
                _logger.exception("Failed to update rejection state for candidate %s", candidate_id)
        self._send_text(candidate_data, wa_id_system, client, _NO_ROLES_MESSAGE)

    def _send_role_selection(self, candidate_data: Mapping[str, object], wa_id_system: str, client) -> bool:
        candidate_id = candidate_data.get("candidate_id")
        keyword = candidate_data.get("next_question") or candidate_data.get("current_question")
        if not keyword:
            _logger.error("Cannot send role selection without keyword (candidate %s)", candidate_id)
            return False

        try:
            text_response, whatsapp_payload = get_keyword_response_from_db(
                session=db.session,
                keyword=keyword,
                candidate_data=candidate_data,
            )
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to load role selection template for candidate %s", candidate_id)
            return False

        if whatsapp_payload is None or text_response is None:
            _logger.warning("Role selection template missing for keyword %s (candidate %s)", keyword, candidate_id)
            return False

        try:
            updated_question_id = candidate_data.get("next_question_id")
            if updated_question_id:
                apply_candidate_updates(candidate_id, [{"question_id": updated_question_id}])
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to persist question cursor for candidate %s", candidate_id)

        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], text_response, "assistant", client)
        store_message(message_id, candidate_data, sent_by, text_response, "")
        send_message(whatsapp_payload, wa_id_system)
        return True

    def _send_text(self, candidate_data: Mapping[str, object], wa_id_system: str, client, message: str) -> None:
        wa_id_user = candidate_data.get("wa_id")
        if not isinstance(wa_id_user, str):
            return
        payload = get_text_message_input(wa_id_user, message)
        send_message(payload, wa_id_system)
        try:
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], message, "assistant", client)
            store_message(message_id, candidate_data, sent_by, message, "")
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to store eligibility message for candidate %s", candidate_data.get("candidate_id"))
