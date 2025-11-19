from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError

from baltra_sdk.legacy.dashboards_folder.models import (
    Candidates,
    ScreeningAnswers,
    db,
)
from baltra_sdk.infra.screening.services.funnel_state_service import FunnelStateService

_logger = logging.getLogger(__name__)


class CandidateStateService:
    """Encapsulates screening-specific state mutations for the SOLID flow."""

    def __init__(self, session=None, funnel_state: FunnelStateService | None = None) -> None:
        self.session = session or db.session
        self.funnel = funnel_state or FunnelStateService(session=self.session)

    # ------------------------------------------------------------------
    # Screening answers
    # ------------------------------------------------------------------
    def store_location_answer(
        self,
        candidate_payload: Dict[str, any],
        message_body: str,
        json_data: Optional[Dict[str, any]],
    ) -> bool:
        candidate_id = candidate_payload.get("candidate_id")
        question_id = candidate_payload.get("question_id")
        if not candidate_id or not question_id:
            _logger.warning("store_location_answer missing candidate/question id")
            return False
        try:
            answer = (
                self.session.query(ScreeningAnswers)
                .filter_by(candidate_id=candidate_id, question_id=question_id)
                .first()
            )
            if answer:
                answer.answer_raw = message_body
                answer.answer_json = json_data
                answer.created_at = datetime.utcnow()
            else:
                answer = ScreeningAnswers(
                    candidate_id=candidate_id,
                    question_id=question_id,
                    answer_raw=message_body,
                    answer_json=json_data,
                    created_at=datetime.utcnow(),
                )
                self.session.add(answer)

            if json_data and "duration_minutes" in json_data:
                candidate = (
                    self.session.query(Candidates)
                    .filter_by(candidate_id=candidate_id)
                    .first()
                )
                if candidate:
                    candidate.travel_time_minutes = json_data["duration_minutes"]

            self.session.commit()
            return True
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("Failed to store location answer for candidate %s", candidate_id)
            return False

    def store_document_answer(
        self,
        candidate_payload: Dict[str, Any],
        message_body: str,
        json_data: Optional[Dict[str, Any]],
    ) -> bool:
        candidate_id = candidate_payload.get("candidate_id")
        question_id = candidate_payload.get("question_id")
        if not candidate_id or not question_id:
            _logger.warning("store_document_answer missing candidate/question id")
            return False
        try:
            answer = (
                self.session.query(ScreeningAnswers)
                .filter_by(candidate_id=candidate_id, question_id=question_id)
                .first()
            )
            if answer:
                answer.answer_raw = message_body
                answer.answer_json = json_data
                answer.created_at = datetime.utcnow()
            else:
                answer = ScreeningAnswers(
                    candidate_id=candidate_id,
                    question_id=question_id,
                    answer_raw=message_body,
                    answer_json=json_data,
                    created_at=datetime.utcnow(),
                )
                self.session.add(answer)
            self.session.commit()
            return True
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("Failed to store document upload answer for candidate %s", candidate_id)
            return False

    # ------------------------------------------------------------------
    # Funnel / rejection helpers
    # ------------------------------------------------------------------
    def mark_flow_rejected(self, candidate_id: int, reason: str) -> bool:
        candidate = (
            self.session.query(Candidates)
            .filter_by(candidate_id=candidate_id)
            .first()
        )
        if not candidate:
            _logger.warning("mark_flow_rejected: candidate %s not found", candidate_id)
            return False
        try:
            previous_state = candidate.funnel_state or ""
            if previous_state != "rejected":
                self.funnel.log_state_change(candidate_id, previous_state, "rejected")
            candidate.funnel_state = "rejected"
            candidate.end_flow_rejected = True
            candidate.rejected_reason = "screening"
            candidate.screening_rejected_reason = reason
            self.session.commit()
            self.funnel.track_state(candidate_id, candidate.company_id, "rejected", reason=reason)
            return True
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("mark_flow_rejected failed for candidate %s", candidate_id)
            return False

    def update_eligible_roles(self, candidate_id: int, role_ids: List[int]) -> bool:
        return self._update_array(candidate_id, "eligible_roles", role_ids)

    def update_eligible_companies(self, candidate_id: int, company_ids: List[int]) -> bool:
        return self._update_array(candidate_id, "eligible_companies", company_ids)

    def update_flow_state(self, candidate_payload: Dict[str, Any], new_state: str) -> bool:
        """Updates the conversational flow_state (respuesta, aclaracion, etc.) for the candidate."""
        candidate_id = candidate_payload.get("candidate_id") if isinstance(candidate_payload, dict) else None
        if not candidate_id:
            _logger.warning("update_flow_state: missing candidate_id")
            return False
        candidate = (
            self.session.query(Candidates)
            .filter_by(candidate_id=candidate_id)
            .first()
        )
        if not candidate:
            _logger.warning("update_flow_state: candidate %s not found", candidate_id)
            return False
        try:
            candidate.flow_state = new_state
            self.session.commit()
            if isinstance(candidate_payload, dict):
                candidate_payload["flow_state"] = new_state
            _logger.debug(
                "[SOLID 6.2] CandidateStateService.update_flow_state candidate=%s flow_state=%s",
                candidate_id,
                new_state,
            )
            return True
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("Failed updating flow_state for candidate %s", candidate_id)
            return False

    def update_funnel_state(self, candidate_payload: Dict[str, Any], new_state: str, *, reason: str | None = None) -> bool:
        """Proxy to the funnel service when the actual funnel_state must change."""
        return self.funnel.update_flow_state(candidate_payload, new_state, reason=reason)

    def apply_candidate_updates(self, candidate_id: int, updates: List[Dict[str, Any]]) -> bool:
        if not updates:
            return False
        candidate = (
            self.session.query(Candidates)
            .filter_by(candidate_id=candidate_id)
            .first()
        )
        if not candidate:
            _logger.warning("apply_candidate_updates: candidate %s not found", candidate_id)
            return False
        allowed_fields = {column.name for column in Candidates.__table__.columns}
        updated = False
        for update in updates:
            for field, value in update.items():
                if field in allowed_fields and value is not None:
                    setattr(candidate, field, value)
                    updated = True
        if not updated:
            return False
        try:
            self.session.commit()
            return True
        except SQLAlchemyError:
            self.session.rollback()
            _logger.exception("apply_candidate_updates failed for candidate %s", candidate_id)
            return False

    # ------------------------------------------------------------------
    def _update_array(self, candidate_id: int, attr: str, values: List[int]) -> bool:
        candidate = (
            self.session.query(Candidates)
            .filter_by(candidate_id=candidate_id)
            .first()
        )
        if not candidate:
            _logger.warning("%s: candidate %s not found", attr, candidate_id)
            return False
        try:
            setattr(candidate, attr, values)
            self.session.commit()
            return True
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("Failed updating %s for candidate %s", attr, candidate_id)
            return False
