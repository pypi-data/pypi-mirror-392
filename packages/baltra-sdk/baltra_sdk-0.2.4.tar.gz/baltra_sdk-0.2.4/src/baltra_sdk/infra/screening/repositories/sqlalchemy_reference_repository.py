from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Mapping

from flask import current_app

from baltra_sdk.domain.screening.entities import ReferenceSnapshot
from baltra_sdk.domain.screening.ports import ReferenceRepository
from baltra_sdk.legacy.dashboards_folder.models import (
    CandidateReferences,
    CompaniesScreening,
    ReferenceMessages,
    db,
)
from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client
from baltra_sdk.shared.utils.screening.sql_utils import (
    save_answer_json,
    store_reference_assessment,
    update_candidate_grade,
)

_logger = logging.getLogger(__name__)


@dataclass
class SqlAlchemyReferenceRepository(ReferenceRepository):
    """SQLAlchemy-backed gateway for reference conversations."""

    session_factory: Callable[[], object] = lambda: db.session  # type: ignore[assignment]
    client_factory: Callable[[], object] = get_openai_client

    def get_or_create(self, wa_id_reference: str) -> ReferenceSnapshot:
        session = self.session_factory()
        reference = self._resolve_reference(session, wa_id_reference)
        latest_message = (
            session.query(ReferenceMessages)
            .filter(ReferenceMessages.reference_id == reference.reference_id)
            .order_by(ReferenceMessages.time_stamp.desc())
            .first()
        )
        thread_id = latest_message.thread_id if latest_message and latest_message.thread_id else self._create_thread_id()

        company = None
        if reference.candidate_id and reference.candidate_id != 9999:
            company = (
                session.query(CompaniesScreening)
                .filter(CompaniesScreening.company_id == reference.candidate.company_id)  # type: ignore[attr-defined]
                .first()
            )

        assistant_id = current_app.config.get("REFERENCE_ASSISTANT_ID", "")
        classifier_id = current_app.config.get("REFERENCE_CLASSIFIER_ASSISTANT_ID", "")

        payload = {
            "wa_id": wa_id_reference,
            "reference_id": reference.reference_id,
            "candidate_id": reference.candidate_id,
            "question_id": reference.question_id,
            "thread_id": thread_id,
            "reference_assistant": assistant_id,
            "reference_classifier": classifier_id,
            "company_name": company.name if company else "",
            "company_context": company.description if company else "",
            "company_phone": (company.phone or "") if company else "",
            "company_benefits": (company.benefits or []) if company else [],
            "interview_address_json": (company.interview_address_json or {}) if company else {},
            "first_name": reference.candidate.name if getattr(reference, "candidate", None) else "",
            "role_context": "Baltra ayuda a las empresas a validar referencias laborales.",
        }
        return ReferenceSnapshot(
            reference_id=reference.reference_id,
            candidate_id=reference.candidate_id,
            wa_id_reference=wa_id_reference,
            question_id=reference.question_id,
            thread_id=thread_id,
            assistant_id=assistant_id,
            classifier_id=classifier_id,
            raw_payload=payload,
        )

    def mark_assessment(self, snapshot: ReferenceSnapshot, classifier_payload: Mapping[str, object]) -> None:
        reference_id = snapshot.reference_id
        candidate_id = snapshot.candidate_id
        if reference_id is None:
            return
        store_reference_assessment(reference_id, classifier_payload)
        if candidate_id:
            save_answer_json(candidate_id, snapshot.question_id, classifier_payload)
            score = classifier_payload.get("recommendation_score")
            update_candidate_grade(candidate_id, score)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _resolve_reference(self, session, wa_id_reference: str) -> CandidateReferences:
        reference = (
            session.query(CandidateReferences)
            .filter(
                CandidateReferences.reference_wa_id == wa_id_reference,
                CandidateReferences.reference_complete.is_(False),
            )
            .order_by(CandidateReferences.reference_id.desc())
            .first()
        )
        if reference:
            return reference

        reference = (
            session.query(CandidateReferences)
            .filter(CandidateReferences.reference_wa_id == wa_id_reference)
            .order_by(CandidateReferences.reference_id.desc())
            .first()
        )
        if reference:
            return reference

        reference = CandidateReferences(
            reference_wa_id=wa_id_reference,
            candidate_id=9999,
            set_id=9999,
            question_id=9999,
        )
        session.add(reference)
        session.commit()
        return reference

    def _create_thread_id(self) -> str:
        client = self.client_factory()
        thread = client.beta.threads.create()
        return thread.id
