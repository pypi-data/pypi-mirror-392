import logging
from sqlalchemy import func
from baltra_sdk.legacy.dashboards_folder.models import (
    Candidates, db, ScreeningMessages, ScreeningQuestions, CompaniesScreening
)

class ScreeningAnalytics:
    """Service to fetch screening churn analytics for a given company"""

    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
        self.company_id = company_id

    def get_churn_by_question(self, start_date=None, end_date=None) -> dict:
        """
        Returns a dict mapping truncated question text (max 100 chars)
        to the number of candidates who churned on that question.

        Optionally filters candidates by created_at date range if start_date and/or end_date
        (datetime.date or datetime.datetime) are provided.

        Only considers candidates with funnel_state = 'screening_in_progress'.
        """
        try:
            # Base filter for candidates
            candidate_filter = [
                Candidates.company_id == self.company_id,
                Candidates.funnel_state == 'screening_in_progress'
            ]

            # Add date filtering if provided
            if start_date:
                candidate_filter.append(Candidates.created_at >= start_date)
            if end_date:
                candidate_filter.append(Candidates.created_at <= end_date)

            last_messages_subq = (
                db.session.query(
                    ScreeningMessages.candidate_id,
                    func.max(ScreeningMessages.message_serial).label("last_serial")
                )
                .join(Candidates, Candidates.candidate_id == ScreeningMessages.candidate_id)
                .filter(*candidate_filter)
                .group_by(ScreeningMessages.candidate_id)
                .subquery()
            )

            last_questions_subq = (
                db.session.query(
                    ScreeningMessages.candidate_id,
                    ScreeningMessages.question_id
                )
                .join(
                    last_messages_subq,
                    (ScreeningMessages.candidate_id == last_messages_subq.c.candidate_id) &
                    (ScreeningMessages.message_serial == last_messages_subq.c.last_serial)
                )
                .subquery()
            )

            query = (
                db.session.query(
                    func.substr(ScreeningQuestions.question, 1, 100).label("question"),
                    func.count(last_questions_subq.c.candidate_id).label("churn_count")
                )
                .join(ScreeningQuestions, ScreeningQuestions.question_id == last_questions_subq.c.question_id)
                .group_by(func.substr(ScreeningQuestions.question, 1, 100))
                .order_by(func.count(last_questions_subq.c.candidate_id).desc())
            )

            result = query.all()
            return {row.question: row.churn_count for row in result}

        except Exception as e:
            logging.error(f"Error fetching churn data for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching churn analytics") from e
    
    def get_screening_rejections_by_reason(self, start_date=None, end_date=None) -> dict:
        """
        Returns a dict mapping truncated screening_rejected_reason (max 100 chars)
        to the count of candidates rejected during screening.

        Optionally filters by created_at date range.
        """
        try:
            candidate_filter = [
                Candidates.company_id == self.company_id,
                Candidates.funnel_state == 'rejected',
                Candidates.rejected_reason == 'screening',
                Candidates.screening_rejected_reason.isnot(None),
                Candidates.screening_rejected_reason != ''
            ]

            if start_date:
                candidate_filter.append(Candidates.created_at >= start_date)
            if end_date:
                candidate_filter.append(Candidates.created_at <= end_date)

            query = (
                db.session.query(
                    func.substr(Candidates.screening_rejected_reason, 1, 100).label("reason"),
                    func.count(Candidates.candidate_id).label("count")
                )
                .filter(*candidate_filter)
                .group_by(func.substr(Candidates.screening_rejected_reason, 1, 100))
                .order_by(func.count(Candidates.candidate_id).desc())
            )

            result = query.all()
            logging.info(f"Screening rejections query result for company {self.company_id}: {[(row.reason, row.count) for row in result]}")
            return {row.reason: row.count for row in result}

        except Exception as e:
            logging.error(f"Error fetching screening rejections for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching screening rejection reasons") from e

    def get_manual_rejections_by_reason(self, start_date=None, end_date=None) -> dict:
        """
        Returns a dict mapping truncated rejected_reason (max 100 chars)
        to the count of candidates rejected manually (not during screening).

        Optionally filters by created_at date range.
        """
        try:
            candidate_filter = [
                Candidates.company_id == self.company_id,
                Candidates.rejected_reason.isnot(None),
                Candidates.rejected_reason != '',
                Candidates.rejected_reason != 'screening'
            ]

            if start_date:
                candidate_filter.append(Candidates.created_at >= start_date)
            if end_date:
                candidate_filter.append(Candidates.created_at <= end_date)

            query = (
                db.session.query(
                    func.substr(Candidates.rejected_reason, 1, 100).label("reason"),
                    func.count(Candidates.candidate_id).label("count")
                )
                .filter(*candidate_filter)
                .group_by(func.substr(Candidates.rejected_reason, 1, 100))
                .order_by(func.count(Candidates.candidate_id).desc())
            )

            result = query.all()
            logging.info(f"Manual rejections query result for company {self.company_id}: {[(row.reason, row.count) for row in result]}")
            return {row.reason: row.count for row in result}

        except Exception as e:
            logging.error(f"Error fetching manual rejections for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching manual rejection reasons") from e

    def get_all_rejections_by_type(self, start_date=None, end_date=None) -> dict:
        """
        Returns a dict containing both screening and manual rejections,
        separated by type for easier frontend consumption.
        """
        try:
            screening_rejections = self.get_screening_rejections_by_reason(start_date, end_date)
            manual_rejections = self.get_manual_rejections_by_reason(start_date, end_date)
            
            return {
                "screening_rejections": screening_rejections,
                "manual_rejections": manual_rejections
            }

        except Exception as e:
            logging.error(f"Error fetching all rejections for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching rejection data") from e

    def get_multi_user_screenings_stats(self, start_date=None, end_date=None) -> dict:
        """
        Returns the number of candidates in screening_in_progress who sent 2+ messages,
        along with the total number of candidates in screening_in_progress during the period.
        """
        try:
            if not isinstance(self.company_id, int) or self.company_id <= 0:
                raise ValueError("Invalid company ID")

            candidate_filter = [
                Candidates.company_id == self.company_id,
            ]
            if start_date:
                candidate_filter.append(Candidates.created_at >= start_date)
            if end_date:
                candidate_filter.append(Candidates.created_at <= end_date)

            # Subquery to count user messages per candidate
            user_msg_counts = (
                db.session.query(
                    ScreeningMessages.candidate_id,
                    func.count(ScreeningMessages.message_id).label("user_msg_count")
                )
                .join(Candidates, Candidates.candidate_id == ScreeningMessages.candidate_id)
                .filter(*candidate_filter)
                .filter(ScreeningMessages.sent_by == 'user')
                .group_by(ScreeningMessages.candidate_id)
                .subquery()
            )

            # Query count of candidates with 2 or more user messages
            multi_user_count = (
                db.session.query(func.count(user_msg_counts.c.candidate_id))
                .filter(user_msg_counts.c.user_msg_count >= 2)
                .scalar()
            )

            # Total candidates in screening_in_progress
            total_candidates = (
                db.session.query(func.count(Candidates.candidate_id))
                .filter(*candidate_filter)
                .scalar()
            )

            return {
                "multi_user_message_candidates": multi_user_count,
                "total_screening_candidates": total_candidates
            }

        except Exception as e:
            logging.error(f"Error fetching multi-user screening stats for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching multi-user screening stats") from e
   
    def get_candidates_reached_via_ad(self, start_date=None, end_date=None) -> dict:
        """
        Returns counts of candidates who reached out with messages containing the
        company's ad_trigger_phrase and those who didn't, filtered by date range.
        """
        try:
            # Fetch the company's ad_trigger_phrase
            company = db.session.query(CompaniesScreening).filter_by(company_id=self.company_id).one_or_none()
            if not company:
                raise RuntimeError(f"Company not found for company_id {self.company_id}")

            if not company.ad_trigger_phrase:
                logging.info(f"No ad_trigger_phrase set for company {self.company_id}, skipping ad reach stats.")
                return {
                    "total_candidates": 0,
                    "candidates_reached_via_ad": 0,
                    "candidates_not_reached_via_ad": 0,
                    "ad_trigger_phrase": ""
                }

            phrase = company.ad_trigger_phrase

            # Build base candidate filter with date range
            candidate_filter = [Candidates.company_id == self.company_id]
            if start_date:
                candidate_filter.append(Candidates.created_at >= start_date)
            if end_date:
                candidate_filter.append(Candidates.created_at <= end_date)


            # Total candidates in the period
            total_candidates = db.session.query(func.count(Candidates.candidate_id)).filter(*candidate_filter).scalar()

            # Get distinct candidates who sent messages containing the phrase
            candidates_with_phrase = (
                db.session.query(ScreeningMessages.candidate_id.distinct().label('candidate_id'))
                .filter(
                    ScreeningMessages.company_id == self.company_id,
                    ScreeningMessages.message_body.ilike(f"%{phrase}%")
                )
                .subquery()
            )

            # Count how many of these candidates are in our filtered date range
            candidates_reached_count = (
                db.session.query(func.count(Candidates.candidate_id.distinct()))
                .join(candidates_with_phrase, Candidates.candidate_id == candidates_with_phrase.c.candidate_id)
                .filter(*candidate_filter)
                .scalar()
            )

            candidates_not_reached_count = total_candidates - candidates_reached_count

            return {
                "total_candidates": total_candidates,
                "candidates_reached_via_ad": candidates_reached_count,
                "candidates_not_reached_via_ad": candidates_not_reached_count,
                "ad_trigger_phrase": phrase
            }

        except Exception as e:
            logging.error(f"Error fetching ad reach stats for company {self.company_id}: {e}")
            raise RuntimeError("Database error fetching candidates reached via ad") from e
          