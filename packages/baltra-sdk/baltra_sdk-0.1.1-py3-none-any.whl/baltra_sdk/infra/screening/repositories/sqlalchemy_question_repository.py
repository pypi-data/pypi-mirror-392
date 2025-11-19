from __future__ import annotations

import logging

from baltra_sdk.domain.screening.entities import CandidateSnapshot, QuestionPrompt
from baltra_sdk.domain.screening.ports import QuestionRepository
from baltra_sdk.legacy.dashboards_folder.models import (
    QuestionSets,
    ScreeningQuestions,
    db,
)
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_keyword_response_from_db


class SqlAlchemyQuestionRepository(QuestionRepository):
    """Fetches questions/prompts from the legacy DB using SQLAlchemy."""

    def build_prompt(self, candidate: CandidateSnapshot) -> QuestionPrompt:
        session = db.session
        candidate_data = dict(candidate.raw_payload)

        keyword = self._resolve_keyword(session, candidate, candidate_data)
        logging.debug(
            "[SOLID 4.1] SqlAlchemyQuestionRepository.build_prompt candidate=%s company=%s keyword=%s first_question=%s",
            candidate.candidate_id,
            candidate.raw_payload.get("company_id"),
            keyword,
            candidate.first_question_flag,
        )
        text_response, whatsapp_payload = get_keyword_response_from_db(
            session=session,
            keyword=keyword,
            candidate_data=candidate_data,
        )

        if text_response is None and whatsapp_payload is None:
            logging.warning(
                "[SOLID 4.1] No template found for keyword=%s (candidate=%s company=%s); falling back to text payload.",
                keyword,
                candidate.candidate_id,
                candidate.raw_payload.get("company_id"),
            )
            text_response = keyword or "Hola"

        return QuestionPrompt(
            keyword=keyword,
            text_response=text_response,
            whatsapp_payload=whatsapp_payload,
        )

    def _resolve_keyword(
        self,
        session,
        candidate: CandidateSnapshot,
        candidate_data: dict,
    ) -> str:
        if candidate.first_question_flag:
            keyword = candidate_data.get("current_question")
        else:
            keyword = candidate_data.get("next_question") or candidate_data.get("current_question")

        if keyword:
            return keyword

        question = self._get_first_question(session, candidate)
        candidate_data["current_question"] = question.question
        return question.question

    def _get_first_question(self, session, candidate: CandidateSnapshot) -> ScreeningQuestions:
        company_id = candidate.raw_payload.get("company_id")
        general_set = (
            session.query(QuestionSets)
            .filter(
                QuestionSets.company_id == company_id,
                QuestionSets.general_set.is_(True),
                QuestionSets.is_active.is_(True),
            )
            .order_by(QuestionSets.created_at.desc())
            .first()
        )
        if general_set is None:
            raise ValueError(f"No general set configured for company_id={company_id}")

        question = (
            session.query(ScreeningQuestions)
            .filter(
                ScreeningQuestions.set_id == general_set.set_id,
                ScreeningQuestions.position == 1,
                ScreeningQuestions.is_active.is_(True),
            )
            .first()
        )
        if question is None:
            raise ValueError("General set does not contain a valid first question.")

        logging.debug("Resolved first question %s for candidate %s", question.question_id, candidate.candidate_id)
        return question
