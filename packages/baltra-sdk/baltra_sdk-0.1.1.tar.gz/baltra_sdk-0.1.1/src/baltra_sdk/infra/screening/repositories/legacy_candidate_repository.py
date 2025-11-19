from __future__ import annotations

from dataclasses import asdict

from baltra_sdk.domain.screening.entities import CandidateSnapshot
from baltra_sdk.domain.screening.ports import CandidateRepository
from baltra_sdk.shared.utils.screening.candidate_data import CandidateDataFetcher
from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client


class LegacyCandidateRepository(CandidateRepository):
    """Candidate repository backed by CandidateDataFetcher (legacy logic)."""

    def get_or_create(self, wa_id_user: str, wa_id_system: str) -> CandidateSnapshot:
        client = get_openai_client()
        data = CandidateDataFetcher(
            wa_id_user=wa_id_user,
            client=client,
            wa_id_system=wa_id_system,
        ).get_data()

        if not data:
            raise RuntimeError("Candidate data could not be fetched.")

        return CandidateSnapshot(
            candidate_id=data.get("candidate_id"),
            wa_id_user=wa_id_user,
            wa_id_system=wa_id_system,
            funnel_state=data.get("funnel_state", "screening_in_progress"),
            current_question=data.get("current_question"),
            next_question=data.get("next_question"),
            first_question_flag=bool(data.get("first_question_flag")),
            raw_payload=data,
        )
