from dataclasses import dataclass

@dataclass
class CandidateStatusSummary:
    company_id: int
    screening_in_progress: int
    scheduled_interview: int
    interview_completed: int
    hired: int
    verified: int
    onboarding: int
    rejected: int
    cancelled: int
    missed_interview: int
    expired: int
