import logging
from typing import List, Dict, Optional

from sqlalchemy import exc, func, case, cast
from sqlalchemy.types import Float

from baltra_sdk.domain.onboarding.ports import OnboardingRepository
from baltra_sdk.legacy.dashboards_folder.models import db, Candidates, OnboardingResponses, Roles, CandidateMedia


logger = logging.getLogger(__name__)


class SqlAlchemyOnboardingRepository(OnboardingRepository):
    """SQLAlchemy-based implementation of the OnboardingRepository port."""

    def get_candidate_info(self, company_id: int, candidate_id: int) -> Optional[dict]:
        try:
            base_query = (
                db.session.query(
                    Candidates.candidate_id,
                    Candidates.company_id,
                    Candidates.name,
                    Candidates.phone,
                    Roles.role_name,
                )
                .outerjoin(Roles, Roles.role_id == Candidates.role_id)
            )

            # Primary: enforce company filter
            row = (
                base_query
                .filter(Candidates.candidate_id == candidate_id, Candidates.company_id == company_id)
                .first()
            )

            # Fallback: fetch by candidate_id only, in case frontend uses mismatched company_id
            if not row:
                row = (
                    base_query
                    .filter(Candidates.candidate_id == candidate_id)
                    .first()
                )

            if not row:
                return None

            return {
                "candidate_id": row[0],
                "company_id": row[1],
                "name": row[2],
                "phone": row[3],
                "role_name": row[4],
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error fetching candidate info {candidate_id}: {e}")
            raise

    def get_responses(self, candidate_id: int, survey: Optional[str] = None) -> List[Dict]:
        try:
            query = db.session.query(OnboardingResponses).filter(OnboardingResponses.candidate_id == candidate_id)
            if survey:
                query = query.filter(OnboardingResponses.survey == survey)
            query = query.order_by(OnboardingResponses.created_at.asc())
            rows = query.all() or []
            return [self._row_to_dict(r) for r in rows]
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error fetching onboarding responses (candidate={candidate_id}, survey={survey}): {e}")
            raise

    def _row_to_dict(self, row: OnboardingResponses) -> Dict:
        return {
            "id": row.id,
            "candidate_id": row.candidate_id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "question": row.question,
            "answer": row.answer,
            "survey": row.survey,
        }

    def search_candidates(self, company_id: int, q: str, search_type: str = "name", limit: int = 10) -> List[Dict]:
        try:
            limit = max(1, min(limit, 50))
            # Default dropdown: when q is empty, return top recent candidates for company
            if not q:
                rows = (
                    db.session.query(
                        Candidates.candidate_id,
                        Candidates.name,
                    )
                    .filter(Candidates.company_id == company_id)
                    .filter(Candidates.funnel_state == 'hired')
                    .order_by(Candidates.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [{"candidate_id": r[0], "name": r[1]} for r in rows]

            if search_type == "name":
                # Prefix search on lower(name) to leverage index
                like = f"{q.lower()}%"
                rows = (
                    db.session.query(
                        Candidates.candidate_id,
                        Candidates.name,
                    )
                    .filter(Candidates.company_id == company_id)
                    .filter(Candidates.funnel_state == 'hired')
                    .filter(func.lower(Candidates.name).like(like))
                    .order_by(Candidates.created_at.desc())
                    .limit(limit)
                    .all()
                )
            else:
                # For RFC or CURP stored in CandidateMedia.string_submission with media_subtype RFC|CURP
                subtype = "RFC" if search_type.lower() == "rfc" else "CURP"
                rows = (
                    db.session.query(
                        Candidates.candidate_id,
                        Candidates.name,
                    )
                    .join(CandidateMedia, CandidateMedia.candidate_id == Candidates.candidate_id)
                    .filter(Candidates.company_id == company_id)
                    .filter(Candidates.funnel_state == 'hired')
                    .filter(CandidateMedia.media_subtype == subtype)
                    .filter(func.lower(CandidateMedia.string_submission).like(f"{q.lower()}%"))
                    .order_by(Candidates.created_at.desc())
                    .limit(limit)
                    .all()
                )

            return [{"candidate_id": r[0], "name": r[1]} for r in rows]
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error searching candidates (type={search_type}, q={q}): {e}")
            raise

    def get_responses_paginated(self, candidate_id: int, survey: Optional[str], page: int, per_page: int) -> Dict:
        try:
            page = max(page, 1)
            per_page = max(1, min(per_page, 100))
            q = db.session.query(OnboardingResponses).filter(OnboardingResponses.candidate_id == candidate_id)
            if survey:
                q = q.filter(OnboardingResponses.survey == survey)

            # total count
            total = q.count()

            # page slice
            items_rows = (
                q.order_by(OnboardingResponses.created_at.desc())
                 .offset((page - 1) * per_page)
                 .limit(per_page)
                 .all()
            )

            return {
                "items": [self._row_to_dict(r) for r in items_rows],
                "page": page,
                "per_page": per_page,
                "total": total,
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error paginating responses (candidate={candidate_id}, survey={survey}): {e}")
            raise

    # ----- Stats helpers -----
    def _month_bounds(self, month: str):
        """Return (start_dt, end_dt) for month string YYYY-MM."""
        try:
            year, mon = month.split('-')
            y = int(year)
            m = int(mon)
            if m < 1 or m > 12:
                raise ValueError
        except Exception:
            raise ValueError("month must be in format YYYY-MM")
        # Compute first day and first of next month using SQL to avoid tz issues
        # But we can return Python datetimes; DB compares fine.
        from datetime import datetime
        from calendar import monthrange
        start = datetime(y, m, 1)
        last_day = monthrange(y, m)[1]
        # end is exclusive
        if m == 12:
            end = datetime(y + 1, 1, 1)
        else:
            end = datetime(y, m + 1, 1)
        return start, end

    def _parse_date(self, value: str):
        from datetime import datetime
        # Accept YYYY-MM-DD or DD-MM-YYYY
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        raise ValueError("Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY")

    def _resolve_bounds(self, month: str | None, start_date: str | None, end_date: str | None):
        if month:
            return self._month_bounds(month)
        if start_date and end_date:
            start = self._parse_date(start_date)
            end_d = self._parse_date(end_date)
            # end exclusive: add one day
            from datetime import timedelta
            end = end_d + timedelta(days=1)
            return start, end
        raise ValueError("Provide either 'month' (YYYY-MM) or both 'start_date' and 'end_date' (YYYY-MM-DD or DD-MM-YYYY)")

    def get_kpis(self, company_id: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        try:
            # Distinct candidates with any onboarding response in month for this company
            sub = (
                db.session.query(OnboardingResponses.candidate_id)
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .distinct()
                .subquery()
            )
            employees_in_onboarding = db.session.query(func.count()).select_from(sub).scalar() or 0

            # Candidates with at least one checklist_1 in month
            sub_cl1 = (
                db.session.query(OnboardingResponses.candidate_id)
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.survey == 'checklist_1')
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .distinct()
                .subquery()
            )
            checklist_1_completed = db.session.query(func.count()).select_from(sub_cl1).scalar() or 0

            # Candidates with at least one checklist_2 in month
            sub_cl2 = (
                db.session.query(OnboardingResponses.candidate_id)
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.survey == 'checklist_2')
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .distinct()
                .subquery()
            )
            checklist_2_completed = db.session.query(func.count()).select_from(sub_cl2).scalar() or 0

            # Avg satisfaction: average of numeric pulse answers 1-5 in month
            # Filter numeric answers using a regex (Postgres) and cast to float
            numeric_filter = OnboardingResponses.answer.op('~')(r'^[0-9]+(\.[0-9]+)?$')
            avg_row = (
                db.session.query(func.avg(cast(OnboardingResponses.answer, Float)))
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.survey == 'pulse')
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(numeric_filter)
                .first()
            )
            avg_satisfaction = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0

            return {
                'employees_in_onboarding': int(employees_in_onboarding),
                'checklist_1_completed': int(checklist_1_completed),
                'checklist_2_completed': int(checklist_2_completed),
                'avg_satisfaction': round(avg_satisfaction, 2),
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing KPIs for company={company_id}: {e}")
            raise

    def get_checklist_yes_by_question(self, company_id: int, checklist_number: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[Dict]:
        if checklist_number not in (1, 2):
            raise ValueError("checklist_number must be 1 or 2")
        start, end = self._resolve_bounds(month, start_date, end_date)
        survey = f'checklist_{checklist_number}'
        try:
            # Normalize fields
            q_text = func.coalesce(OnboardingResponses.question, '')
            a_text = func.coalesce(OnboardingResponses.answer, '')
            q_lower = func.lower(q_text)
            a_trim = func.btrim(a_text)
            a_lower_trim = func.lower(a_trim)
            # Detect comment-type questions (e.g., "Deja un comentario")
            is_comment_q = q_lower.like('%comentario%')
            # Non-empty answer check (after trim)
            has_text = func.length(a_trim) > 0
            # Count "yes" for yes/no; for comment questions, count non-empty answers as yes
            yes_case = case(
                (is_comment_q & has_text, 1),
                (a_lower_trim.in_(['si', 'sí', 'yes', 'true', '1']), 1),
                else_=0,
            )
            rows = (
                db.session.query(
                    OnboardingResponses.question.label('question'),
                    func.count().label('total'),
                    func.sum(yes_case).label('yes'),
                )
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.survey == survey)
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .group_by(OnboardingResponses.question)
                .order_by(OnboardingResponses.question.asc())
                .all()
            )
            out = []
            for r in rows:
                total = int(r.total or 0)
                yes = int(r.yes or 0)
                percentage = round((yes / total * 100.0), 2) if total > 0 else 0.0
                out.append({
                    'question': r.question,
                    'yes': yes,
                    'total': total,
                    'percentage': percentage,
                })
            return out
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing checklist stats for company={company_id}, survey={survey}: {e}")
            raise

    def get_pulse_weekly_stats(self, company_id: int, month: str | None = None, start_date: str | None = None, end_date: str | None = None, by_question: bool = False) -> List[Dict]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        try:
            # Only include numeric answers 1-5
            numeric_filter = OnboardingResponses.answer.op('~')(r'^[0-9]+(\.[0-9]+)?$')
            week_label = func.to_char(func.date_trunc('week', OnboardingResponses.created_at), 'IYYY-"W"IW')
            base = (
                db.session.query(
                    week_label.label('week'),
                    func.avg(cast(OnboardingResponses.answer, Float)).label('avg'),
                    func.count().label('responses'),
                )
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id == company_id)
                .filter(OnboardingResponses.survey == 'pulse')
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(numeric_filter)
            )
            if not by_question:
                rows = (
                    base
                    .group_by(week_label)
                    .order_by(week_label.asc())
                    .all()
                )
                return [
                    {
                        'week': r.week,
                        'avg': round(float(r.avg), 2) if r.avg is not None else 0.0,
                        'responses': int(r.responses or 0),
                    }
                    for r in rows
                ]
            else:
                # Group by question and week
                q_field = func.coalesce(OnboardingResponses.question, '')
                rows = (
                    base.add_columns(q_field.label('question'))
                        .group_by(q_field, week_label)
                        .order_by(q_field.asc(), week_label.asc())
                        .all()
                )
                # Build series per question
                series_map: Dict[str, List[Dict]] = {}
                for r in rows:
                    # row order matches selected columns: week, avg, responses, question
                    week, avg_v, responses_v, question = r
                    entry = {
                        'week': week,
                        'avg': round(float(avg_v), 2) if avg_v is not None else 0.0,
                        'responses': int(responses_v or 0),
                    }
                    series_map.setdefault(question, []).append(entry)
                return [
                    { 'question': q, 'series': pts }
                    for q, pts in series_map.items()
                ]
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing pulse weekly stats for company={company_id}: {e}")
            raise
