from __future__ import annotations
from typing import Protocol, List, Dict, Optional


class OnboardingRepository(Protocol):
    """Port for fetching onboarding-related data for candidates."""

    def get_candidate_info(self, company_id: int, candidate_id: int) -> Optional[Dict]:
        """Return candidate basic info (id, name, phone, role_name) or None if not found."""
        ...

    def get_responses(self, candidate_id: int, survey: Optional[str] = None) -> List[Dict]:
        """Return a list of response dicts from onboarding_responses, optionally filtered by survey."""
        ...

    def get_responses_paginated(self, candidate_id: int, survey: Optional[str], page: int, per_page: int) -> Dict:
        """Return paginated responses with metadata: {items, page, per_page, total}."""
        ...

    def search_candidates(self, company_id: int, q: str, search_type: str = "name", limit: int = 10) -> List[Dict]:
        """Search candidates by name (ILIKE), RFC, or CURP. Returns list of {candidate_id, name, phone, role_name}."""
        ...

    # Stats
    def get_kpis(self, company_id: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None) -> Dict:
        """Return KPI aggregates filtered by either month (YYYY-MM) or a date range (start_date/end_date in YYYY-MM-DD or DD-MM-YYYY).

        Expected keys: employees_in_onboarding, checklist_1_completed, checklist_2_completed, avg_satisfaction.
        """
        ...

    def get_checklist_yes_by_question(self, company_id: int, checklist_number: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[Dict]:
        """Return per-question aggregation for checklist {1|2}, filtered by month or date range."""
        ...

    def get_pulse_weekly_stats(self, company_id: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None, by_question: bool = False) -> List[Dict]:
        """Return weekly pulse averages filtered by month or date range.

        - When by_question=False: list of {week: 'YYYY-Www', avg: float, responses: int}
        - When by_question=True: list of {question: str, series: [ {week, avg, responses} ]}
        """
        ...
