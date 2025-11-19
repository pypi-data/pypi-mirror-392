from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from baltra_sdk.domain.screening.entities import CandidateSnapshot
from baltra_sdk.domain.screening.ports import ConversationProgression
from baltra_sdk.legacy.dashboards_folder.models import (
    ScreeningAnswers,
    ScreeningQuestions,
    db,
)


@dataclass
class SqlAlchemyConversationProgression(ConversationProgression):
    """Stores candidate answers and advances the question cursor."""

    logger: logging.Logger = logging.getLogger(__name__)

    def advance(self, candidate: CandidateSnapshot, answer_text: str) -> CandidateSnapshot | None:
        if not answer_text:
            raise ValueError("Cannot advance conversation without an answer.")

        question_id = candidate.raw_payload.get("question_id")
        if not question_id:
            raise ValueError("Candidate snapshot is missing current question metadata.")

        session = db.session
        question = (
            session.query(ScreeningQuestions)
            .filter(ScreeningQuestions.question_id == question_id)
            .first()
        )
        if question is None:
            raise ValueError(f"Question {question_id} not found.")

        self._store_answer(session, candidate.candidate_id, question.question_id, answer_text)
        self.logger.debug(
            "[SOLID 3.2] Stored answer candidate=%s question_id=%s",
            candidate.candidate_id,
            question.question_id,
        )

        next_row, consumed_next_set = self._determine_next_question(session, candidate.raw_payload, question)
        if next_row is None:
            self.logger.info("Candidate %s completed all questions.", candidate.candidate_id)
            return None

        payload = dict(candidate.raw_payload)
        payload.update(
            {
                "set_id": next_row.set_id,
                "question_id": next_row.question_id,
                "current_question": next_row.question,
                "current_response_type": next_row.response_type,
                "current_position": next_row.position,
                "first_question_flag": False,
            }
        )
        if consumed_next_set:
            # We consumed the precomputed next set metadata; clear it to avoid reusing stale data
            payload["next_set_id"] = None
            payload["next_set_first_question"] = None
            payload["next_set_first_question_id"] = None
            payload["next_set_first_question_type"] = None

        follow_up = self._lookup_follow_up(session, payload, next_row)
        payload["next_question"] = follow_up.question if follow_up else None
        payload["next_question_id"] = follow_up.question_id if follow_up else None
        payload["next_question_response_type"] = follow_up.response_type if follow_up else None

        snapshot = CandidateSnapshot(
            candidate_id=candidate.candidate_id,
            wa_id_user=candidate.wa_id_user,
            wa_id_system=candidate.wa_id_system,
            funnel_state=payload.get("funnel_state", candidate.funnel_state),
            current_question=payload.get("current_question"),
            next_question=payload.get("next_question"),
            first_question_flag=False,
            raw_payload=payload,
        )
        self.logger.debug(
            "[SOLID 3.3] Advance result candidate=%s current_question=%s next_question=%s",
            candidate.candidate_id,
            snapshot.current_question,
            snapshot.next_question,
        )
        return snapshot

    def _store_answer(
        self,
        session,
        candidate_id: Optional[int],
        question_id: int,
        answer_text: str,
    ) -> None:
        if candidate_id is None:
            raise ValueError("Candidate ID is required to store an answer.")

        existing = (
            session.query(ScreeningAnswers)
            .filter(
                ScreeningAnswers.candidate_id == candidate_id,
                ScreeningAnswers.question_id == question_id,
            )
            .first()
        )
        if existing:
            existing.answer_raw = answer_text
            existing.created_at = datetime.utcnow()
        else:
            session.add(
                ScreeningAnswers(
                    candidate_id=candidate_id,
                    question_id=question_id,
                    answer_raw=answer_text,
                    created_at=datetime.utcnow(),
                )
            )
        session.commit()

    def _determine_next_question(
        self,
        session,
        payload: dict,
        current_question: ScreeningQuestions,
    ) -> Tuple[Optional[ScreeningQuestions], bool]:
        """Return the next question row and whether a precomputed next set was consumed."""
        next_question_id = payload.get("next_question_id")
        consumed_next_set = False

        if next_question_id is None:
            next_question_id = payload.get("next_set_first_question_id")
            if next_question_id is not None:
                consumed_next_set = True

        if next_question_id is None:
            return None, consumed_next_set

        next_row = (
            session.query(ScreeningQuestions)
            .filter(ScreeningQuestions.question_id == next_question_id)
            .first()
        )

        return next_row, consumed_next_set

    def _lookup_follow_up(
        self,
        session,
        payload: dict,
        current_question: ScreeningQuestions,
    ) -> Optional[ScreeningQuestions]:
        """Find the next question preview after the provided current question."""
        follow_up = (
            session.query(ScreeningQuestions)
            .filter(
                ScreeningQuestions.set_id == current_question.set_id,
                ScreeningQuestions.position == current_question.position + 1,
                ScreeningQuestions.is_active.is_(True),
            )
            .first()
        )
        if follow_up:
            return follow_up

        # No more questions in this set; fall back to already-computed next set metadata.
        next_set_first_id = payload.get("next_set_first_question_id")
        if next_set_first_id:
            return (
                session.query(ScreeningQuestions)
                .filter(ScreeningQuestions.question_id == next_set_first_id)
                .first()
            )
        return None
