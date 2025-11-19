from __future__ import annotations

from baltra_sdk.domain.screening.entities import CandidateSnapshot, QuestionPrompt
from baltra_sdk.domain.screening.ports import QuestionRepository
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_keyword_response_from_db


class LegacyQuestionRepository(QuestionRepository):
    """Question repository backed by legacy templates."""

    def build_prompt(self, candidate: CandidateSnapshot) -> QuestionPrompt:
        keyword = (
            candidate.current_question
            if candidate.first_question_flag
            else candidate.next_question
        )
        if not keyword:
            keyword = "default_welcome"

        text_response, whatsapp_payload = get_keyword_response_from_db(
            session=db.session,
            keyword=keyword,
            candidate_data=candidate.raw_payload,
        )
        return QuestionPrompt(
            keyword=keyword,
            text_response=text_response,
            whatsapp_payload=whatsapp_payload,
        )

