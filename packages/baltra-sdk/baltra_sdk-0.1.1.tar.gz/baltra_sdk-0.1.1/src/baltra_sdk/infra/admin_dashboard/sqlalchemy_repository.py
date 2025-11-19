import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any, Set

from sqlalchemy import (
    func,
    exc,
    case,
    cast,
    or_,
    and_,
    Text,
    text, literal,
)
from sqlalchemy.orm import aliased
from sqlalchemy.types import Float
from baltra_sdk.domain.admin_dashboard.ports import AdminDashboardRepository
from baltra_sdk.legacy.dashboards_folder.models import (
    db,
    Candidates,
    CandidateFunnelLog,
    Roles,
    CompaniesScreening,
    ScreeningQuestions,
    ScreeningAnswers,
    ScreeningMessages,
    QuestionSets,
    OnboardingResponses,
    CandidateMedia,
    EligibilityEvaluationLog,
    MessageTemplates,
)

logger = logging.getLogger(__name__)

# ----------------------------- #
#            CONSTANTS          #
# ----------------------------- #
GLOBAL_COMPANY_ID = 9999
IGNORED_QUESTIONS = {"phone_reference"}
SPECIAL_Q_TYPES = {"interactive", "location", "location_critical"}
ORDERED_FUNNEL = [
    "screening_in_progress",
    "scheduled_interview",
    "interview_completed",
    "hired",
    "verified",
    "onboarding",
]
EXTRA_FUNNEL = ["rejected", "cancelled", "missed_interview", "expired"]


class SqlAlchemyAdminDashboardRepository(AdminDashboardRepository):
    # ----------------------------- #
    #        DATE UTILITIES         #
    # ----------------------------- #
    def _parse_date(self, value: str):
        from datetime import datetime

        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.replace(tzinfo=timezone.utc)
            except Exception:
                continue
        raise ValueError("Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY")

    def _month_bounds(self, month: str):
        from datetime import datetime

        y, m = map(int, month.split("-"))
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        end = datetime(y + (m == 12), (m % 12) + 1, 1, tzinfo=timezone.utc)
        return start, end

    def _resolve_bounds(
        self, month: Optional[str], start_date: Optional[str], end_date: Optional[str]
    ):
        if start_date and end_date:
            from datetime import timedelta

            start = self._parse_date(start_date)
            end = self._parse_date(end_date) + timedelta(days=1)
            return start, end
        if month:
            return self._month_bounds(month)
        raise ValueError("Provide either 'month' or both 'start_date' and 'end_date'")

    # ----------------------------- #
    #        SCOPE UTILITIES        #
    # ----------------------------- #
    def _resolve_group_ids(self, company_id: int) -> List[int]:
        try:
            company = (
                db.session.query(
                    CompaniesScreening.company_id, CompaniesScreening.group_id
                )
                .filter(CompaniesScreening.company_id == company_id)
                .one_or_none()
            )
            if not company or company.group_id is None:
                return [company_id]
            ids = [
                cid
                for (cid,) in db.session.query(CompaniesScreening.company_id)
                .filter(CompaniesScreening.group_id == company.group_id)
                .all()
            ]
            return ids or [company_id]
        except Exception:
            return [company_id]

    def _resolve_group_id(self, company_id: int) -> Optional[int]:
        try:
            return (
                db.session.query(CompaniesScreening.group_id)
                .filter(CompaniesScreening.company_id == company_id)
                .scalar()
            )
        except Exception:
            return None

    def _build_scope(
        self,
        company_id: int,
        company_ids: Optional[List[int]],
        scope_all: bool,
    ) -> Tuple[List[int], List[int], Optional[int], Any, List[int]]:
        """
        Returns:
          filter_ids, group_companies, group_id, company_pred, per_company_ids_for_sets
        """
        filter_ids = (
            company_ids
            if company_ids
            else (self._resolve_group_ids(company_id) if scope_all else [company_id])
        )
        group_companies = self._resolve_group_ids(company_id)
        group_id = self._resolve_group_id(company_id)

        if len(filter_ids) < len(group_companies):
            company_pred = Candidates.company_id.in_(filter_ids)
            per_company_ids_for_sets = filter_ids
        else:
            company_pred = or_(
                Candidates.company_id.in_(filter_ids),
                Candidates.company_group_id == group_id,
            )
            per_company_ids_for_sets = group_companies

        return filter_ids, group_companies, group_id, company_pred, per_company_ids_for_sets

    def _prepare_funnel_context(
        self,
        company_id: int,
        month: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
        company_ids: Optional[List[int]],
        scope_all: bool,
        include_state_windows: bool = False,
    ) -> Dict[str, Any]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, group_companies, group_id, company_pred, per_company_ids_for_sets = self._build_scope(
            company_id, company_ids, scope_all
        )
        cohort_q = self._cohort_union_any_and_reentry(company_pred, start, end)

        ctx: Dict[str, Any] = {
            "start": start,
            "end": end,
            "filter_ids": filter_ids,
            "group_companies": group_companies,
            "group_id": group_id,
            "company_pred": company_pred,
            "per_company_ids_for_sets": per_company_ids_for_sets,
            "cohort": cohort_q,
        }

        if include_state_windows:
            stage_idx_case = case(
                *[(CandidateFunnelLog.new_funnel_state == s, i) for i, s in enumerate(ORDERED_FUNNEL)],
                else_=-1,
            )
            ranked_logs = (
                db.session.query(
                    CandidateFunnelLog.candidate_id.label("candidate_id"),
                    stage_idx_case.label("stage_idx"),
                    CandidateFunnelLog.new_funnel_state.label("new_state"),
                    CandidateFunnelLog.previous_funnel_state.label("prev_state"),
                    func.row_number()
                    .over(
                        partition_by=CandidateFunnelLog.candidate_id,
                        order_by=CandidateFunnelLog.changed_at.desc(),
                    )
                    .label("rn"),
                )
                .join(cohort_q, cohort_q.c.candidate_id == CandidateFunnelLog.candidate_id)
                .cte("ranked_funnel_logs")
            )
            latest_states = (
                db.session.query(
                    ranked_logs.c.candidate_id.label("candidate_id"),
                    func.max(ranked_logs.c.stage_idx).label("max_idx"),
                    func.max(
                        case((ranked_logs.c.rn == 1, ranked_logs.c.new_state), else_=None)
                    ).label("last_state"),
                    func.max(
                        case((ranked_logs.c.rn == 1, ranked_logs.c.prev_state), else_=None)
                    ).label("last_prev"),
                    func.max(
                        case((ranked_logs.c.rn == 2, ranked_logs.c.new_state), else_=None)
                    ).label("prev2_state"),
                    func.max(
                        case((ranked_logs.c.rn == 2, ranked_logs.c.prev_state), else_=None)
                    ).label("prev2_prev"),
                )
                .group_by(ranked_logs.c.candidate_id)
                .cte("latest_funnel_states")
            )
            ctx.update({"ranked_logs": ranked_logs, "latest_states": latest_states})

        return ctx

    def _cohort_union_any_and_reentry(self, company_pred, start, end):
        first_change = func.min(CandidateFunnelLog.changed_at)
        sub_any = (
            db.session.query(
                CandidateFunnelLog.candidate_id.label("candidate_id"),
                first_change.label("first_changed_at"),
            )
            .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
            .filter(company_pred)
            .group_by(CandidateFunnelLog.candidate_id)
            .having(first_change >= start)
            .having(first_change < end)
        )
        sub_reentry = (
            db.session.query(
                CandidateFunnelLog.candidate_id.label("candidate_id"),
                func.min(CandidateFunnelLog.changed_at).label("first_changed_at"),
            )
            .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
            .filter(company_pred)
            .filter(CandidateFunnelLog.previous_funnel_state == "expired")
            .filter(
                CandidateFunnelLog.new_funnel_state == "screening_in_progress",
                CandidateFunnelLog.changed_at >= start,
                CandidateFunnelLog.changed_at < end,
            )
            .group_by(CandidateFunnelLog.candidate_id)
        )
        unioned = sub_any.union_all(sub_reentry).subquery("u")
        return db.session.query(func.distinct(unioned.c.candidate_id).label("candidate_id")).subquery(
            "cohort"
        )

    def _latest_two_logs_view(self, cohort_q):
        rn = func.row_number().over(
            partition_by=CandidateFunnelLog.candidate_id,
            order_by=CandidateFunnelLog.changed_at.desc(),
        ).label("rn")

        ranked_logs = (
            db.session.query(
                CandidateFunnelLog.candidate_id.label("candidate_id"),
                CandidateFunnelLog.new_funnel_state.label("new_state"),
                CandidateFunnelLog.previous_funnel_state.label("prev_state"),
                CandidateFunnelLog.changed_at.label("changed_at"),
                rn,
            )
            .join(cohort_q, cohort_q.c.candidate_id == CandidateFunnelLog.candidate_id)
        ).subquery()

        return aliased(ranked_logs), aliased(ranked_logs)

    @staticmethod
    def _calc_avg_median(values: List[float]) -> Tuple[float, float]:
        if not values:
            return 0.0, 0.0
        s = sorted(values)
        n = len(s)
        avg = sum(s) / n
        med = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
        return round(avg, 2), round(med, 2)

    # ----------------------------- #
    #            FUNNEL             #
    # ----------------------------- #
    def get_funnel_buckets(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        _, group_companies, group_id, company_pred, _ = self._build_scope(
            company_id, company_ids, scope_all
        )

        try:
            first_stage = ORDERED_FUNNEL[0]

            if company_pred.compare(Candidates.company_id.in_(self._resolve_group_ids(company_id))):
                query = (
                    db.session.query(func.distinct(CandidateFunnelLog.candidate_id))
                    .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                    .filter(company_pred)
                    .filter(CandidateFunnelLog.new_funnel_state == first_stage)
                    .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                )
            else:
                query = (
                    db.session.query(func.distinct(CandidateFunnelLog.candidate_id))
                    .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                    .filter(
                        or_(
                            company_pred,
                            Candidates.company_group_id == self._resolve_group_id(company_id),
                        )
                    )
                    .filter(CandidateFunnelLog.new_funnel_state == first_stage)
                    .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                )

            candidate_ids = [cid for (cid,) in query.all()]

            counts = {s: 0 for s in ORDERED_FUNNEL}
            if candidate_ids:
                stage_index = case(
                    *[
                        (CandidateFunnelLog.new_funnel_state == s, i)
                        for i, s in enumerate(ORDERED_FUNNEL)
                    ],
                    else_=-1,
                )
                latest_stage_per_candidate = (
                    db.session.query(
                        CandidateFunnelLog.candidate_id,
                        func.max(stage_index).label("max_stage_index"),
                    )
                    .filter(CandidateFunnelLog.candidate_id.in_(candidate_ids))
                    .filter(
                        CandidateFunnelLog.changed_at >= start,
                        CandidateFunnelLog.changed_at < end,
                    )
                    .group_by(CandidateFunnelLog.candidate_id)
                    .all()
                )
                for _, idx in latest_stage_per_candidate:
                    if idx != -1:
                        for i in range(idx + 1):
                            counts[ORDERED_FUNNEL[i]] += 1

            data = [{"state": st, "count": counts.get(st, 0)} for st in ORDERED_FUNNEL] + [
                {"state": st, "count": 0} for st in ["rejected", "cancelled", "missed_interview", "expired"]
            ]
            return data

        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing funnel buckets for company={company_id}: {e}")
            raise

    def get_time_to_hire(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        ctx = self._prepare_funnel_context(
            company_id, month, start_date, end_date, company_ids, scope_all, include_state_windows=False
        )
        start = ctx["start"]
        end = ctx["end"]
        cohort_q = ctx["cohort"]
        try:
            screening_first = (
                db.session.query(
                    CandidateFunnelLog.candidate_id.label("candidate_id"),
                    func.min(CandidateFunnelLog.changed_at).label("started_at"),
                )
                .join(cohort_q, cohort_q.c.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(CandidateFunnelLog.new_funnel_state == "screening_in_progress")
                .group_by(CandidateFunnelLog.candidate_id)
                .subquery()
            )
            hired_first = (
                db.session.query(
                    CandidateFunnelLog.candidate_id.label("candidate_id"),
                    func.min(CandidateFunnelLog.changed_at).label("hired_at"),
                )
                .join(cohort_q, cohort_q.c.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(CandidateFunnelLog.new_funnel_state == "hired")
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                .group_by(CandidateFunnelLog.candidate_id)
                .subquery()
            )
            diffs = (
                db.session.query(
                    func.extract("epoch", hired_first.c.hired_at - screening_first.c.started_at) / 3600.0
                )
                .join(screening_first, screening_first.c.candidate_id == hired_first.c.candidate_id)
                .all()
            )
            values = [float(v[0]) for v in diffs if v[0] is not None and v[0] >= 0]
            avg_hours, median_hours = self._calc_avg_median(values)
            return {"samples": len(values), "avg_hours": avg_hours, "median_hours": median_hours}
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing time to hire for company={company_id}: {e}")
            raise

    def get_hires_by_role(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict]:
        ctx = self._prepare_funnel_context(
            company_id, month, start_date, end_date, company_ids, scope_all, include_state_windows=False
        )
        start = ctx["start"]
        end = ctx["end"]
        company_pred = ctx["company_pred"]
        cohort_q = ctx["cohort"]
        try:
            hires_subquery = (
                db.session.query(CandidateFunnelLog.candidate_id.label("candidate_id"))
                .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                .join(cohort_q, cohort_q.c.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(company_pred)
                .filter(CandidateFunnelLog.new_funnel_state == "hired")
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                .group_by(CandidateFunnelLog.candidate_id)
                .subquery()
            )

            rows = (
                db.session.query(
                    Roles.role_id.label("role_id"),
                    func.coalesce(Roles.role_name, literal("Sin rol")).label("role_name"),
                    func.count().label("cnt"),
                    func.array_agg(func.distinct(hires_subquery.c.candidate_id)).label("candidate_ids"),
                )
                .select_from(Candidates)
                .outerjoin(Roles, Candidates.role_id == Roles.role_id)
                .join(hires_subquery, hires_subquery.c.candidate_id == Candidates.candidate_id)
                .group_by(Roles.role_id, func.coalesce(Roles.role_name, literal("Sin rol")))
                .order_by(func.count().desc())
                .all()
            )

            all_hired_ids: Set[int] = set()

            for r in rows:
                cleaned_ids: List[int] = []
                if r.candidate_ids:
                    try:
                        cleaned_ids = [int(cid) for cid in r.candidate_ids if cid is not None]
                    except Exception:
                        cleaned_ids = []
                cleaned_ids_sorted = sorted(set(cleaned_ids))
                if cleaned_ids_sorted:
                    all_hired_ids.update(cleaned_ids_sorted)
                candidate_ids_compact = (
                    f"[{','.join(str(cid) for cid in cleaned_ids_sorted)}]" if cleaned_ids_sorted else "[]"
                )
                # logger.info(
                #     "[HIRES_BY_ROLE] role_id=%s role_name=%s count=%s all_candidates_hired=%s",
                #     r.role_id,
                #     r.role_name,
                #     int(r.cnt),
                #     candidate_ids_compact,
                # )

            all_hired_compact = (
                f"[{','.join(str(cid) for cid in sorted(all_hired_ids))}]"
                if all_hired_ids
                else "[]"
            )
            # logger.info("[HIRES_BY_ROLE] all_candidates_hired=%s", all_hired_compact)

            return [{"role_id": r.role_id, "role_name": r.role_name, "count": int(r.cnt)} for r in rows]
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing hires by role for company={company_id}: {e}")
            raise

    # ----------------------------- #
    #        SOURCES / ORIGINS      #
    # ----------------------------- #
    def get_sources(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            rows = (
                db.session.query(func.coalesce(Candidates.source, "unknown"), func.count())
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(Candidates.created_at >= start, Candidates.created_at < end)
                .group_by(func.coalesce(Candidates.source, "unknown"))
                .order_by(func.count().desc())
                .all()
            )
            return [{"source": r[0], "count": int(r[1])} for r in rows]
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing sources for company={company_id}: {e}")
            raise

    def get_origins_evaluated(
            self,
            company_id: int,
            month: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            company_ids: Optional[List[int]] = None,
            scope_all: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Cuenta "evaluados" con base en el PRIMER estado del funnel dentro del rango de fechas.
        - Con company_id: devuelve counts por source (normalizado).
        - Sin company_id: devuelve un renglón agregado 'no_company'.
        """

        MIN_START_DATE = datetime(2025, 10, 17, tzinfo=timezone.utc)

        start, end = self._resolve_bounds(month, start_date, end_date)

        if start_date:
            user_start = (
                self._parse_date(start_date)
                if isinstance(start_date, str)
                else start_date
            )

            # 1) Validación mínima primero
            if user_start < MIN_START_DATE:
                logging.warning(
                    "start_date (%s) es anterior a la mínima permitida (%s). Usando MIN_START_DATE.",
                    user_start, MIN_START_DATE
                )
                user_start = MIN_START_DATE

            # 2) Regla correcta: si el usuario envía start_date válido, se usa SIEMPRE
            #    (ya no depende de si es anterior o posterior al inicio del mes)
            start = user_start

        # Defensivo: evita rango invertido
        if end and end < start:
            logging.warning("end (%s) es anterior a start (%s). Ajustando end = start.", end, start)
            end = start

        # Reutiliza el mismo scope que usas en get_funnel_buckets
        # _build_scope(...) suele regresar: (filter_ids, group_companies, group_id, company_pred, user_pred)
        filter_ids, _, group_id, company_pred, _ = self._build_scope(
            company_id, company_ids, scope_all
        )

        try:
            first_stage = ORDERED_FUNNEL[0]

            # Construye el conjunto base de "evaluados" = entraron al primer estado en el rango
            # Usa la misma ramificación que en tu get_funnel_buckets para company_pred
            # NOTA: comparamos el "company_pred" con el predicado directo sobre los filter_ids calculados
            should_limit_to_ids = company_pred.compare(Candidates.company_id.in_(filter_ids))

            base_q = (
                db.session.query(func.distinct(CandidateFunnelLog.candidate_id))
                .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(CandidateFunnelLog.new_funnel_state == first_stage)
                .filter(
                    CandidateFunnelLog.changed_at >= start,
                    CandidateFunnelLog.changed_at < end,
                )
            )

            if should_limit_to_ids:
                # Caso 1: limitar estrictamente a las company_ids resueltas
                base_q = base_q.filter(company_pred)
            else:
                # Caso 2: alcance por predicado O por el group_id del company_id base
                base_q = base_q.filter(
                    or_(
                        company_pred,
                        Candidates.company_group_id == group_id,
                    )
                )

            candidate_ids = [cid for (cid,) in base_q.all()]
            if not candidate_ids:
                # No hay evaluados en el rango
                return [{"source": "no_company", "evaluated": 0}]

            # Normaliza el source SOLO para los que sí tienen company
            norm_source = func.coalesce(
                func.nullif(func.trim(Candidates.source), ""), "unknown"
            ).label("source")

            # --- A) Con company: counts por source ---
            with_company_rows = (
                db.session.query(
                    norm_source,
                    func.count(func.distinct(Candidates.candidate_id)).label("evaluated"),
                )
                .filter(Candidates.candidate_id.in_(candidate_ids))
                .filter(Candidates.company_id.isnot(None))
                .group_by(norm_source)
                .order_by(func.count(func.distinct(Candidates.candidate_id)).desc(), norm_source)
                .all()
            )

            data = [
                {"source": r.source, "evaluated": int(r.evaluated)}
                for r in with_company_rows
            ]

            # --- B) Sin company: agregado global (no tiene source) ---
            no_company_total = (
                    db.session.query(func.count(func.distinct(Candidates.candidate_id)))
                    .filter(Candidates.candidate_id.in_(candidate_ids))
                    .filter(Candidates.company_id.is_(None))
                    .scalar()
                    or 0
            )

            # Añadimos la fila especial
            data.append({"source": "no_company", "evaluated": int(no_company_total)})

            return data

        except exc.SQLAlchemyError as e:
            logger.error(
                f"DB error computing origins-evaluated (funnel-based) for company_id={company_id}: {e}"
            )
            raise

    # ----------------------------- #
    #         REJECTIONS            #
    # ----------------------------- #
    def get_rejections(
        self,
        company_id: int,
        source: str,
        month=None,
        start_date=None,
        end_date=None,
        company_ids=None,
        scope_all: bool = False,
    ) -> List[Dict]:
        split = self.get_rejections_split(
            company_id, month, start_date, end_date, company_ids, scope_all
        )
        if source == "chat":
            return split.get("chat", [])
        if source == "manual":
            return split.get("manual", [])
        raise ValueError("'source' must be 'chat' or 'manual'")

    def get_rejections_split(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict[str, List[Dict[str, int]]]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, group_companies, group_id, company_pred, _ = self._build_scope(
            company_id, company_ids, scope_all
        )
        logger.info(
            f"[REJ] bounds={start}->{end} scope_all={scope_all} ids={filter_ids} group_id={group_id}"
        )

        cohort_q = self._cohort_union_any_and_reentry(company_pred, start, end)
        logger.info(
            f"[REJ] cohort_size={db.session.query(func.count()).select_from(cohort_q).scalar() or 0}"
        )

        last1, last2 = self._latest_two_logs_view(cohort_q)
        eff_last = case((last1.c.new_state == "expired", last2.c.new_state), else_=last1.c.new_state)

        rejected_ids = (
            db.session.query(last1.c.candidate_id.label("candidate_id"))
            .join(last2, and_(last2.c.candidate_id == last1.c.candidate_id, last2.c.rn == 2), isouter=True)
            .filter(last1.c.rn == 1)
            .filter(eff_last == "rejected")
            .subquery()
        )
        logger.info(
            f"[REJ] rejected_size={db.session.query(func.count()).select_from(rejected_ids).scalar() or 0}"
        )

        trim_chat = func.nullif(func.trim(func.coalesce(Candidates.screening_rejected_reason, "")), "")
        trim_manual = func.nullif(func.trim(func.coalesce(Candidates.rejected_reason, "")), "")
        is_screening_flag = func.lower(func.coalesce(Candidates.rejected_reason, "")) == "screening"

        is_chat = or_(is_screening_flag, trim_chat.isnot(None))
        is_manual = and_(trim_manual.isnot(None), func.lower(trim_manual) != "screening")

        chat_reason = func.coalesce(trim_chat, "unknown")
        chat_rows_all = (
            db.session.query(chat_reason.label("reason"), func.count().label("cnt"))
            .select_from(Candidates)
            .join(rejected_ids, rejected_ids.c.candidate_id == Candidates.candidate_id)
            .filter(is_chat)
            .group_by(chat_reason)
            .order_by(func.count().desc())
            .all()
        )
        chat = [
            {"reason": str(r.reason), "count": int(r.cnt)}
            for r in chat_rows_all
            if str(r.reason) != "unknown"
        ]
        chat.sort(key=lambda x: x["count"], reverse=True)

        manual_rows = (
            db.session.query(trim_manual.label("reason"), func.count().label("cnt"))
            .select_from(Candidates)
            .join(rejected_ids, rejected_ids.c.candidate_id == Candidates.candidate_id)
            .filter(is_manual)
            .group_by(trim_manual)
            .order_by(func.count().desc())
            .all()
        )
        manual = [{"reason": str(r.reason), "count": int(r.cnt)} for r in manual_rows]
        manual.sort(key=lambda x: x["count"], reverse=True)

        return {"chat": chat, "manual": manual}

    # ----------------------------- #
    #          ONBOARDING           #
    # ----------------------------- #
    def _onboarding_yes_agg(self, filter_ids, start, end, survey_name: str) -> List[Dict]:
        q_text = func.coalesce(OnboardingResponses.question, "")
        a_text = func.coalesce(OnboardingResponses.answer, "")
        q_lower = func.lower(q_text)
        a_trim = func.btrim(a_text)
        a_lower_trim = func.lower(a_trim)
        is_comment_q = q_lower.like("%comentario%")
        has_text = func.length(a_trim) > 0
        yes_case = case(
            (is_comment_q & has_text, 1),
            (a_lower_trim.in_(["si", "sí", "yes", "true", "1"]), 1),
            else_=0,
        )
        rows = (
            db.session.query(
                OnboardingResponses.question.label("question"),
                func.count().label("total"),
                func.sum(yes_case).label("yes"),
            )
            .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
            .filter(Candidates.company_id.in_(filter_ids))
            .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
            .filter(OnboardingResponses.survey == survey_name)
            .group_by(OnboardingResponses.question)
            .order_by(OnboardingResponses.question.asc())
            .all()
        )
        out: List[Dict] = []
        for r in rows:
            total = int(r.total or 0)
            yes = int(r.yes or 0)
            percentage = round((yes / total * 100.0), 2) if total > 0 else 0.0
            out.append({"question": r.question, "yes": yes, "total": total, "percentage": percentage})
        return out

    def get_onboarding_summary(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            onboarding_count = (
                db.session.query(func.count(func.distinct(CandidateFunnelLog.candidate_id)))
                .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(CandidateFunnelLog.new_funnel_state == "onboarding")
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
            ).scalar() or 0

            cl1_emps = (
                db.session.query(func.count(func.distinct(OnboardingResponses.candidate_id)))
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(OnboardingResponses.survey == "checklist_1")
            ).scalar() or 0
            cl2_emps = (
                db.session.query(func.count(func.distinct(OnboardingResponses.candidate_id)))
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(OnboardingResponses.survey == "checklist_2")
            ).scalar() or 0

            denom = onboarding_count or 1
            cl1_completion = round(100.0 * cl1_emps / denom, 2) if onboarding_count else 0.0
            cl2_completion = round(100.0 * cl2_emps / denom, 2) if onboarding_count else 0.0

            vals = (
                db.session.query(OnboardingResponses.answer)
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(OnboardingResponses.survey == "pulse")
            ).all()
            nums: List[float] = []
            for (ans,) in vals:
                try:
                    nums.append(float(ans))
                except Exception:
                    continue
            avg = round(sum(nums) / len(nums), 2) if nums else 0.0
            return {
                "employees_in_onboarding": int(onboarding_count),
                "checklist1_completion": cl1_completion,
                "checklist1_employees": int(cl1_emps),
                "checklist2_completion": cl2_completion,
                "checklist2_employees": int(cl2_emps),
                "average_satisfaction": avg,
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing onboarding summary for company={company_id}: {e}")
            raise

    def get_onboarding_checklists(
        self,
        company_id: int,
        checklist: Optional[int],
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            if checklist in (1, 2):
                survey = f"checklist_{checklist}"
                return self._onboarding_yes_agg(filter_ids, start, end, survey)
            return {
                "checklist_1": self._onboarding_yes_agg(filter_ids, start, end, "checklist_1"),
                "checklist_2": self._onboarding_yes_agg(filter_ids, start, end, "checklist_2"),
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing onboarding checklists for company={company_id}: {e}")
            raise

    def get_onboarding_satisfaction(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            vals = (
                db.session.query(OnboardingResponses.answer)
                .join(Candidates, Candidates.candidate_id == OnboardingResponses.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(OnboardingResponses.created_at >= start, OnboardingResponses.created_at < end)
                .filter(OnboardingResponses.survey == "pulse")
            ).all()
            nums = []
            for (ans,) in vals:
                try:
                    nums.append(float(ans))
                except Exception:
                    continue
            avg, _ = self._calc_avg_median(nums)
            return {"average": avg, "change": 0.0, "samples": len(nums)}
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing onboarding satisfaction for company={company_id}: {e}")
            raise

    # ----------------------------- #
    #           DOCUMENTS           #
    # ----------------------------- #
    def get_documents_summary(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            rows = (
                db.session.query(
                    func.coalesce(CandidateMedia.media_subtype, "unknown").label("subtype"),
                    func.count().label("total"),
                    func.sum(case((CandidateMedia.verified.is_(True), 1), else_=0)).label("verified"),
                )
                .join(Candidates, Candidates.candidate_id == CandidateMedia.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(CandidateMedia.upload_timestamp >= start, CandidateMedia.upload_timestamp < end)
                .group_by("subtype")
                .order_by(func.count().desc())
                .all()
            )
            return {
                "items": [
                    {"subtype": r[0], "total": int(r[1]), "verified": int(r[2] or 0)} for r in rows
                ]
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing documents summary for company={company_id}: {e}")
            raise

    def get_documents_by_type(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)
        try:
            pending_case = case(
                (
                    and_(
                        CandidateMedia.media_subtype == "NSS",
                        CandidateMedia.verified.is_(False),
                        and_(
                            CandidateMedia.verification_result.isnot(None),
                            cast(CandidateMedia.verification_result, Text).like('%"verificationId"%'),
                        ),
                    ),
                    1,
                ),
                else_=0,
            )

            rows = (
                db.session.query(
                    func.coalesce(CandidateMedia.media_subtype, "unknown").label("subtype"),
                    func.count().label("total"),
                    func.sum(case((CandidateMedia.verified.is_(True), 1), else_=0)).label("verified"),
                    func.sum(pending_case).label("pending"),
                )
                .join(Candidates, Candidates.candidate_id == CandidateMedia.candidate_id)
                .filter(Candidates.company_id.in_(filter_ids))
                .filter(CandidateMedia.upload_timestamp >= start, CandidateMedia.upload_timestamp < end)
                .group_by("subtype")
                .order_by(func.count().desc())
                .all()
            )
            result = []
            for subtype, total, verified, pending in rows:
                total_i = int(total or 0)
                verified_i = int(verified or 0)
                pending_i = int(pending or 0)
                rejected_i = max(0, total_i - verified_i - pending_i)
                result.append(
                    {
                        "type": subtype,
                        "total": total_i,
                        "verified": verified_i,
                        "waiting": pending_i,
                        "rejected": rejected_i,
                    }
                )
            return result
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing documents by type for company={company_id}: {e}")
            raise

    # ----------------------------- #
    #     STORES / TOGGLING         #
    # ----------------------------- #
    def list_stores(
        self,
        company_id: int,
        search: Optional[str] = None,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        start = end = None
        if month or (start_date and end_date):
            start, end = self._resolve_bounds(month, start_date, end_date)

        try:
            filter_ids, _, _, _, _ = self._build_scope(company_id, company_ids, scope_all)

            has_customer_id = "customer_id" in CompaniesScreening.__table__.c.keys()
            if has_customer_id:
                stores_q = db.session.query(
                    CompaniesScreening.company_id,
                    CompaniesScreening.customer_id,
                    CompaniesScreening.name,
                    CompaniesScreening.address,
                ).filter(CompaniesScreening.company_id.in_(filter_ids))
            else:
                stores_q = db.session.query(
                    CompaniesScreening.company_id,
                    CompaniesScreening.name,
                    CompaniesScreening.address,
                ).filter(CompaniesScreening.company_id.in_(filter_ids))

            if search:
                stores_q = stores_q.filter(CompaniesScreening.name.ilike(f"%{search}%"))
            stores = stores_q.all()
            if not stores:
                return {"items": [], "meta": {"total": 0}}

            if has_customer_id:
                ids = [cid for (cid, _cust, _name, _addr) in stores]
            else:
                ids = [cid for (cid, _name, _addr) in stores]

            roles_rows = (
                db.session.query(
                    Roles.company_id, func.sum(case((Roles.active.is_(True), 1), else_=0)).label("cnt")
                )
                .filter(Roles.company_id.in_(ids))
                .group_by(Roles.company_id)
                .all()
            )
            roles_active_map = {cid: int(cnt) > 0 for cid, cnt in roles_rows}

            qsets_rows = (
                db.session.query(
                    QuestionSets.company_id,
                    func.sum(case((QuestionSets.is_active.is_(True), 1), else_=0)).label("cnt"),
                )
                .filter(QuestionSets.company_id.in_(ids))
                .group_by(QuestionSets.company_id)
                .all()
            )
            qsets_active_map = {cid: int(cnt) > 0 for cid, cnt in qsets_rows}

            def compute_is_active(cid: int) -> bool:
                return bool(roles_active_map.get(cid, False) or qsets_active_map.get(cid, False))

            if start is None or end is None:
                if has_customer_id:
                    items = [
                        {
                            "company_id": cid,
                            "name": f"{cust}-{name}" if cust else name,
                            "address": address,
                            "is_active": compute_is_active(cid),
                        }
                        for (cid, cust, name, address) in stores
                    ]
                else:
                    items = [
                        {"company_id": cid, "name": name, "address": address, "is_active": compute_is_active(cid)}
                        for (cid, name, address) in stores
                    ]
                return {"items": items, "meta": {"total": len(items)}}

            hired = (
                db.session.query(
                    Candidates.company_id,
                    func.count(func.distinct(CandidateFunnelLog.candidate_id)).label("cnt"),
                )
                .join(CandidateFunnelLog, CandidateFunnelLog.candidate_id == Candidates.candidate_id)
                .filter(Candidates.company_id.in_(ids))
                .filter(CandidateFunnelLog.new_funnel_state == "hired")
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                .group_by(Candidates.company_id)
            ).all()
            hired_map = {cid: int(cnt) for cid, cnt in hired}

            active = (
                db.session.query(
                    Candidates.company_id,
                    func.count(func.distinct(CandidateFunnelLog.candidate_id)).label("cnt"),
                )
                .join(CandidateFunnelLog, CandidateFunnelLog.candidate_id == Candidates.candidate_id)
                .filter(Candidates.company_id.in_(ids))
                .filter(CandidateFunnelLog.new_funnel_state == "screening_in_progress")
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                .group_by(Candidates.company_id)
            ).all()
            active_map = {cid: int(cnt) for cid, cnt in active}

            leads = (
                db.session.query(Candidates.company_id, func.count(Candidates.candidate_id).label("cnt"))
                .filter(Candidates.company_id.in_(ids))
                .filter(Candidates.created_at >= start, Candidates.created_at < end)
                .group_by(Candidates.company_id)
            ).all()
            leads_map = {cid: int(cnt) for cid, cnt in leads}

            items = []
            if has_customer_id:
                for cid, customer_id, name, address in stores:
                    h = hired_map.get(cid, 0)
                    a = active_map.get(cid, 0)
                    l = leads_map.get(cid, 0)
                    conv = round(100.0 * h / l, 2) if l else 0.0
                    display_name = f"{customer_id}-{name}" if customer_id else name
                    items.append(
                        {
                            "company_id": cid,
                            "name": display_name,
                            "address": address,
                            "hires": h,
                            "active_recruitment": a,
                            "conversion_rate": conv,
                            "is_active": compute_is_active(cid),
                        }
                    )
            else:
                for cid, name, address in stores:
                    h = hired_map.get(cid, 0)
                    a = active_map.get(cid, 0)
                    l = leads_map.get(cid, 0)
                    conv = round(100.0 * h / l, 2) if l else 0.0
                    items.append(
                        {
                            "company_id": cid,
                            "name": name,
                            "address": address,
                            "hires": h,
                            "active_recruitment": a,
                            "conversion_rate": conv,
                            "is_active": compute_is_active(cid),
                        }
                    )
            return {"items": items, "meta": {"total": len(items)}}
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error listing stores for company={company_id}: {e}")
            raise

    def toggle_store_active(self, company_id: int, store_id: int, is_active: bool) -> bool:
        try:
            origin = (
                db.session.query(CompaniesScreening.company_id, CompaniesScreening.group_id)
                .filter(CompaniesScreening.company_id == company_id)
                .one_or_none()
            )
            target = (
                db.session.query(CompaniesScreening.company_id, CompaniesScreening.group_id)
                .filter(CompaniesScreening.company_id == store_id)
                .one_or_none()
            )
            if not target:
                return False

            if store_id != company_id:
                if not origin or origin.group_id is None or target.group_id is None or origin.group_id != target.group_id:
                    return False

            db.session.query(Roles).filter(Roles.company_id == store_id).update(
                {Roles.active: bool(is_active)}, synchronize_session=False
            )
            db.session.query(QuestionSets).filter(QuestionSets.company_id == store_id).update(
                {QuestionSets.is_active: bool(is_active)}, synchronize_session=False
            )
            db.session.commit()
            return True
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(
                f"DB error toggling store active for company={company_id}, store={store_id}: {e}"
            )
            raise

    # ----------------------------- #
    #   CANDIDATE STATUS SUMMARY    #
    # ----------------------------- #
    def get_candidate_status_summary(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict]:
        start, end = self._resolve_bounds(month, start_date, end_date)
        _, _, _, company_pred, _ = self._build_scope(company_id, company_ids, scope_all)

        try:
            latest_log_subquery = (
                db.session.query(
                    CandidateFunnelLog.candidate_id,
                    func.max(CandidateFunnelLog.changed_at).label("max_changed_at"),
                )
                .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                .filter(company_pred)
                .filter(CandidateFunnelLog.changed_at >= start, CandidateFunnelLog.changed_at < end)
                .group_by(CandidateFunnelLog.candidate_id)
                .subquery()
            )

            results = (
                db.session.query(
                    CandidateFunnelLog.new_funnel_state,
                    Candidates.company_id,
                    func.count(Candidates.candidate_id).label("status_count"),
                )
                .join(
                    latest_log_subquery,
                    and_(
                        CandidateFunnelLog.candidate_id == latest_log_subquery.c.candidate_id,
                        CandidateFunnelLog.changed_at == latest_log_subquery.c.max_changed_at,
                    ),
                )
                .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
                .group_by(CandidateFunnelLog.new_funnel_state, Candidates.company_id)
                .all()
            )

            summary_by_status: Dict[str, Dict[str, Any]] = {}
            for status, company_id_res, count in results:
                if status not in summary_by_status:
                    summary_by_status[status] = {"status_name": status, "companies": []}
                summary_by_status[status]["companies"].append(
                    {"id": company_id_res, "count": int(count)}
                )
            return list(summary_by_status.values())

        except exc.SQLAlchemyError as e:
            logger.error(f"DB error computing candidate status summary for company={company_id}: {e}")
            raise

    # ----------------------------- #
    #  SCREENING Q/TEMPLATES I/O    #
    # ----------------------------- #
    def _question_to_dict(self, q: ScreeningQuestions) -> Dict:
        return {
            "id": q.question_id,
            "set_id": q.set_id,
            "position": q.position,
            "question": q.question,
            "response_type": q.response_type,
            "is_active": q.is_active,
            "question_metadata": q.question_metadata,
            "end_interview_answer": q.end_interview_answer,
            "example_answer": q.example_answer,
        }

    def _template_to_dict(self, t: MessageTemplates) -> Dict:
        editable = t.company_id != GLOBAL_COMPANY_ID
        options = []
        if t.interactive_type == "button":
            options = t.button_keys if t.button_keys is not None else []
        return {
            "id": t.id,
            "keyword": t.keyword,
            "text": t.text,
            "company_id": t.company_id,
            "options": options,
            "editable": editable,
        }

    def find_question_by_id(self, question_id: int) -> Optional[Dict]:
        try:
            question = db.session.query(ScreeningQuestions).get(question_id)
            return self._question_to_dict(question) if question else None
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error finding question by id={question_id}: {e}")
            raise

    def find_template_by_id(self, template_id: int) -> Optional[Dict]:
        try:
            template = db.session.query(MessageTemplates).get(template_id)
            return self._template_to_dict(template) if template else None
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error finding template by id={template_id}: {e}")
            raise

    def find_template_by_keyword(self, keyword: str, company_id: int) -> Optional[Dict]:
        try:
            filter_ids = self._resolve_group_ids(company_id)
            pref_weight = case((MessageTemplates.company_id.in_(filter_ids), 0), else_=1)
            template = (
                db.session.query(MessageTemplates)
                .filter(MessageTemplates.keyword == keyword)
                .filter(
                    or_(
                        MessageTemplates.company_id.in_(filter_ids),
                        MessageTemplates.company_id.is_(None),
                    )
                )
                .order_by(pref_weight, MessageTemplates.id.desc())
                .first()
            )
            return self._template_to_dict(template) if template else None
        except exc.SQLAlchemyError as e:
            logger.error(f"DB error finding template by keyword={keyword}: {e}")
            raise

    def update_screening_question(self, question_id: int, data: Dict) -> Optional[Dict]:
        try:
            question = db.session.query(ScreeningQuestions).get(question_id)
            if not question:
                return None

            for key, value in data.items():
                if key != "full_question" and hasattr(question, key):
                    setattr(question, key, value)

            if "full_question" in data:
                if question.response_type == "text":
                    question.question = data["full_question"]
                elif question.response_type in SPECIAL_Q_TYPES:
                    keyword = question.question
                    template = (
                        db.session.query(MessageTemplates)
                        .filter(func.lower(func.trim(MessageTemplates.keyword)) == func.lower(func.trim(keyword)))
                        .first()
                    )
                    if template:
                        template.text = data["full_question"]

            db.session.commit()
            return self._question_to_dict(question)
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"DB error updating question id={question_id}: {e}")
            raise

    def update_message_template(self, template_id: int, data: Dict) -> Optional[Dict]:
        try:
            template = db.session.query(MessageTemplates).get(template_id)
            if not template:
                return None

            if "text" in data:
                template.text = data["text"]
            if "options" in data:
                template.list_options = data["options"]
                template.button_keys = [opt.get("id") for opt in data["options"]]

            db.session.commit()
            return self._template_to_dict(template)
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"DB error updating template id={template_id}: {e}")
            raise

    # ----------------------------- #
    #  FUNNEL STATUS BY COMPANY     #
    # ----------------------------- #
    def get_funnel_status_by_company_formatted(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> List[Dict[str, Any]]:
        ctx = self._prepare_funnel_context(
            company_id, month, start_date, end_date, company_ids, scope_all, include_state_windows=True
        )
        cohort_q = ctx["cohort"]
        latest_states = ctx["latest_states"]

        total_cohort = db.session.query(func.count()).select_from(cohort_q).scalar() or 0
        logger.info(f"[FUNNEL] Total cohort count: {total_cohort}")

        needs_update_case = case(
            (
                and_(
                    latest_states.c.last_state == "scheduled_interview",
                    Candidates.interview_date_time.isnot(None),
                    Candidates.interview_date_time < (func.now() - text("interval '1 day'")),
                ),
                1,
            ),
            else_=0,
        )

        rows = (
            db.session.query(
                Candidates.company_id.label("company_id"),
                latest_states.c.max_idx.label("max_idx"),
                latest_states.c.last_state.label("last_state"),
                latest_states.c.last_prev.label("last_prev"),
                latest_states.c.prev2_state.label("prev2_state"),
                latest_states.c.prev2_prev.label("prev2_prev"),
                Candidates.rejected_reason.label("rejected_reason"),
                func.array_agg(func.distinct(latest_states.c.candidate_id)).label("candidate_ids"),
                func.sum(needs_update_case).label("upd_required"),
                func.count().label("cnt"),
            )
            .join(latest_states, latest_states.c.candidate_id == Candidates.candidate_id)
            .group_by(
                Candidates.company_id,
                latest_states.c.max_idx,
                latest_states.c.last_state,
                latest_states.c.last_prev,
                latest_states.c.prev2_state,
                latest_states.c.prev2_prev,
                Candidates.rejected_reason,
            )
            .all()
        )

        def _state_obj():
            return {"state": "", "percent": 0.0, "count": 0, "companies": []}

        by_status: Dict[str, Dict[str, Any]] = {s: {"state": s, "percent": 0.0, "count": 0, "companies": []} for s in ORDERED_FUNNEL}

        def _comp_bucket():
            return {
                "id": None,
                "label": None,
                "count": 0,
                "rejected_count": 0,
                "missed_interview_count": 0,
                "cancelled_count": 0,
                "updated_required_count": 0,
                "no_verified_count": 0,
            }

        companies_acc: Dict[str, Dict[str, Dict[str, Any]]] = {s: {} for s in by_status.keys()}

        def key_for(company_id_opt: Optional[int], label: Optional[str]) -> str:
            return f"id:{company_id_opt}" if label is None else f"label:{label}"

        expired = {"expired"}

        def resolve_target(
            last_state,
            last_prev,
            prev2_state,
            prev2_prev,
            rejected_reason=None,
            max_idx: Optional[int] = None,
        ):
            eff_last = last_state
            eff_prev = last_prev
            if last_state in expired:
                eff_last = prev2_state
                eff_prev = prev2_prev

            def first_ordered(*states):
                for st in states:
                    if st in ORDERED_FUNNEL:
                        return st
                return None

            def ordered_from_max():
                if max_idx is None:
                    return None
                if 0 <= max_idx < len(ORDERED_FUNNEL):
                    return ORDERED_FUNNEL[max_idx]
                return None

            history_target = first_ordered(eff_prev, prev2_state, prev2_prev)

            if eff_last in ORDERED_FUNNEL:
                return eff_last, None

            if eff_last == "rejected":
                # NUEVO: rechazado inmediatamente después de haber estado en hired
                if eff_prev == "hired":
                    # Lo contabilizamos EN hired y marcamos no_verified_count
                    return "hired", "no_verified_count"
                if eff_prev == "screening_in_progress":
                    return "screening_in_progress", "rejected_screening"
                if eff_prev == "scheduled_interview":
                    rr = (rejected_reason or "").lower()
                    if rr == "abscense":
                        return "scheduled_interview", "missed_interview_count"
                    return "interview_completed", "rejected_count"
                if eff_prev == "missed_interview":
                    fallback = first_ordered(prev2_state, prev2_prev)
                    if fallback == "scheduled_interview":
                        return "scheduled_interview", "missed_interview_count"
                    if fallback:
                        return fallback, "rejected_count"
                if eff_prev in ORDERED_FUNNEL:
                    return eff_prev, "rejected_count"
                if history_target:
                    return history_target, "rejected_count"
                idx_target = ordered_from_max()
                if idx_target is not None:
                    return idx_target, "rejected_count"
                return None, None

            if eff_last == "missed_interview" and eff_prev == "scheduled_interview":
                return "scheduled_interview", "missed_interview_count"

            if eff_last == "missed_interview":
                if history_target:
                    return history_target, "missed_interview_count"
                idx_target = ordered_from_max()
                if idx_target is not None:
                    return idx_target, "missed_interview_count"
                return None, None

            if eff_last == "cancelled" and eff_prev == "scheduled_interview":
                return "scheduled_interview", "cancelled_count"

            if eff_last == "cancelled":
                if history_target:
                    return history_target, "cancelled_count"
                idx_target = ordered_from_max()
                if idx_target is not None:
                    return idx_target, "cancelled_count"
                return None, None

            return None, None

        hired_candidates_total: Set[int] = set()
        onboarding_candidates_total: Set[int] = set()

        for (
            company_id_res,
            max_idx,
            last_state,
            last_prev,
            prev2_state,
            prev2_prev,
            rejected_reason,
            candidate_ids,
            upd_required,
            cnt,
        ) in rows:
            cnt = int(cnt)
            upd_required_val = int(upd_required or 0)
            cleaned_ids: List[int] = []
            if candidate_ids:
                try:
                    cleaned_ids = [int(cid) for cid in candidate_ids if cid is not None]
                except Exception:
                    cleaned_ids = []
            cleaned_ids_sorted = sorted(set(cleaned_ids))
            candidate_ids_compact = (
                f"[{','.join(str(cid) for cid in cleaned_ids_sorted)}]" if cleaned_ids_sorted else "[]"
            )
            if max_idx is None or max_idx < 0:
                logger.info(f"[FUNNEL] Skipped (no stage): last_state={last_state} last_prev={last_prev} cnt={cnt}")
                continue

            target_state, counter = resolve_target(
                last_state, last_prev, prev2_state, prev2_prev, rejected_reason, max_idx
            )
            if target_state in {"hired", "onboarding"}:
                if target_state == "hired" and cleaned_ids_sorted:
                    hired_candidates_total.update(cleaned_ids_sorted)
                if target_state == "onboarding" and cleaned_ids_sorted:
                    onboarding_candidates_total.update(cleaned_ids_sorted)
                # logger.info(
                #     "[FUNNEL][STATE_%s] company_id=%s all_candidates_%s=%s last_state=%s last_prev=%s prev2_state=%s prev2_prev=%s cnt=%s",
                #     target_state.upper(),
                #     company_id_res,
                #     target_state,
                #     candidate_ids_compact,
                #     last_state,
                #     last_prev,
                #     prev2_state,
                #     prev2_prev,
                #     cnt,
                # )
            if not target_state:
                logger.info(
                    "[FUNNEL] Fallback to screening_in_progress: last_state='%s' last_prev='%s' prev2_state='%s' prev2_prev='%s' cnt=%s company_id=%s",
                    last_state,
                    last_prev,
                    prev2_state,
                    prev2_prev,
                    cnt,
                    company_id_res,
                )
                target_state = "screening_in_progress"

            if target_state not in by_status:
                by_status[target_state] = _state_obj()
                by_status[target_state]["state"] = target_state
                companies_acc[target_state] = {}

            label = None
            cid = company_id_res

            if counter == "rejected_screening":
                label = "Sin tienda cerca"
                cid = None

            k = key_for(cid, label)
            if k not in companies_acc[target_state]:
                companies_acc[target_state][k] = _comp_bucket()
                companies_acc[target_state][k]["id"] = cid
                companies_acc[target_state][k]["label"] = label

            by_status[target_state]["count"] += cnt
            companies_acc[target_state][k]["count"] += cnt

            if counter == "rejected_count":
                companies_acc[target_state][k]["rejected_count"] += cnt
            elif counter == "missed_interview_count":
                companies_acc[target_state][k]["missed_interview_count"] += cnt
            elif counter == "cancelled_count":
                companies_acc[target_state][k]["cancelled_count"] += cnt
            elif counter == "no_verified_count":  # NUEVO
                companies_acc[target_state][k]["no_verified_count"] += cnt

            if target_state == "scheduled_interview" and upd_required_val:
                companies_acc[target_state][k]["updated_required_count"] += upd_required_val

        all_hired_compact = (
            f"[{','.join(str(cid) for cid in sorted(hired_candidates_total))}]"
            if hired_candidates_total
            else "[]"
        )
        # logger.info("[FUNNEL][ALL_HIRED] all_candidates_hired=%s", all_hired_compact)

        all_onboarding_compact = (
            f"[{','.join(str(cid) for cid in sorted(onboarding_candidates_total))}]"
            if onboarding_candidates_total
            else "[]"
        )
        # logger.info("[FUNNEL][ALL_ONBOARDING] all_candidates_onboarding=%s", all_onboarding_compact)

        for st, comp_map in companies_acc.items():
            items = list(comp_map.values())

            def sort_key(it):
                if it["label"] is None:
                    return (0, it["id"] if it["id"] is not None else 10**12, "")
                return (1, 10**12, it["label"])

            items.sort(key=sort_key)

            cleaned = []
            for it in items:
                obj: Dict[str, Any] = {"count": it["count"]}
                if it["id"] is None and it["label"] is None and st == "screening_in_progress":
                    obj["id"] = "Sin elección"
                elif it["id"] is not None:
                    obj["id"] = it["id"]
                elif it["label"] is not None:
                    obj["id"] = it["label"]

                if it["rejected_count"]:
                    obj["rejected_count"] = it["rejected_count"]
                if it["missed_interview_count"]:
                    obj["missed_interview_count"] = it["missed_interview_count"]
                if it["cancelled_count"]:
                    obj["cancelled_count"] = it["cancelled_count"]
                if it["updated_required_count"]:
                    obj["updated_required_count"] = it["updated_required_count"]
                if it["no_verified_count"]:  # NUEVO
                    obj["no_verified_count"] = it["no_verified_count"]
                cleaned.append(obj)

            by_status[st]["companies"] = cleaned

        if total_cohort > 0:
            for s in by_status.values():
                s["percent"] = round((s["count"] / total_cohort) * 100, 2)

        base_keys = ORDERED_FUNNEL
        dynamic = [k for k in by_status.keys() if k not in base_keys]
        dynamic.sort()
        result = [by_status[k] for k in base_keys] + [by_status[k] for k in dynamic]
        logger.info(f"[FUNNEL] Final states={len(result)}")
        return result

    # ----------------------------- #
    #  SCREENING QUESTIONS SUMMARY  #
    # ----------------------------- #
    def _templates_ranked_first(self, keywords: List[str], per_company_ids_for_sets: List[int]) -> Dict[str, dict]:
        if not keywords:
            return {}
        pref_weight = case((MessageTemplates.company_id.in_(per_company_ids_for_sets), 0), else_=1)
        ranked = (
            db.session.query(
                MessageTemplates.keyword.label("keyword"),
                MessageTemplates.text.label("template_text"),
                MessageTemplates.company_id.label("template_company_id"),
                MessageTemplates.interactive_type.label("interactive_type"),
                MessageTemplates.button_keys.label("button_keys"),
                func.row_number()
                .over(partition_by=MessageTemplates.keyword, order_by=(pref_weight, MessageTemplates.id.desc()))
                .label("rnk"),
            )
            .filter(MessageTemplates.keyword.in_(keywords))
            .filter(
                or_(
                    MessageTemplates.company_id.in_(per_company_ids_for_sets),
                    MessageTemplates.company_id == GLOBAL_COMPANY_ID,
                )
            )
            .subquery()
        )
        rows = (
            db.session.query(
                ranked.c.keyword,
                ranked.c.template_text,
                ranked.c.template_company_id,
                ranked.c.interactive_type,
                ranked.c.button_keys,
            )
            .filter(ranked.c.rnk == 1)
            .all()
        )
        out: Dict[str, dict] = {}
        for kw, t_text, t_company, i_type, b_keys in rows:
            out[str(kw)] = {
                "text": t_text,
                "company_id": t_company,
                "interactive_type": i_type,
                "button_keys": b_keys,
            }
        return out

    @staticmethod
    def _consolidate_questions(raw_items: List[dict]) -> Tuple[List[dict], Dict[str, int]]:
        def _merge_unique(a, b):
            seen, out = set(), []
            for x in (a or []):
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            for x in (b or []):
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        buckets: Dict[str, dict] = {}
        for it in raw_items:
            key = (it.get("keyword") or "").strip()
            if not key:
                continue
            if key not in buckets:
                buckets[key] = {
                    "id": int(it["id"]),
                    "keyword": key,
                    "short_title": it.get("resolved_text") or key,
                    "full_question": it.get("resolved_text") or key,
                    "response_type": it.get("response_type"),
                    "total_responses": int(it.get("total_responses", 0)),
                    "step_index": int(it.get("step_index", 0)),
                    "src": it.get("src"),
                    "src_order": int(it.get("src_order", 9)),
                    "editable": bool(it.get("editable", False)),
                    "options": list(it.get("options") or []),
                }
                continue

            b = buckets[key]
            b["total_responses"] += int(it.get("total_responses", 0))
            b["step_index"] = min(b["step_index"], int(it.get("step_index", 0)))
            b["options"] = _merge_unique(b.get("options"), it.get("options"))
            b["editable"] = bool(b["editable"] or it.get("editable", False))

            prefer = False
            it_so, b_so = int(it.get("src_order", 9)), int(b.get("src_order", 9))
            if it_so < b_so:
                prefer = True
            elif it_so == b_so:
                it_st, b_st = int(it.get("step_index", 0)), int(b.get("step_index", 0))
                if it_st < b_st:
                    prefer = True
                elif it_st == b_st and int(it.get("id", 10**12)) < int(b.get("id", 10**12)):
                    prefer = True
            if prefer:
                b["id"] = int(it["id"])
                b["short_title"] = it.get("resolved_text") or b["short_title"]
                b["full_question"] = it.get("resolved_text") or b["full_question"]
                b["response_type"] = it.get("response_type") or b.get("response_type")
                b["src"] = it.get("src")
                b["src_order"] = it_so

        items = list(buckets.values())
        items.sort(key=lambda x: (x.get("src_order", 9), x.get("step_index", 0), x.get("id", 0)))
        for i, it in enumerate(items, start=1):
            it["final_position"] = i

        tbg = {"group": 0, "general": 0, "role": 0}
        for it in items:
            s = it.get("src")
            if s in tbg:
                tbg[s] += int(it.get("total_responses", 0))
        return items, tbg

    def get_screening_questions_summary(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
        include_answers_only: bool = False,
    ) -> Dict:
        start, end = self._resolve_bounds(month, start_date, end_date)
        filter_ids, group_companies, group_id, company_pred, per_company_ids_for_sets = self._build_scope(
            company_id, company_ids, scope_all
        )

        group_ids = [
            gid
            for (gid,) in db.session.query(func.distinct(CompaniesScreening.group_id))
            .filter(CompaniesScreening.company_id.in_(group_companies))
            .all()
            if gid is not None
        ] if (len(filter_ids) >= len(group_companies)) else []
        group_set_ids = (
            [sid for (sid,) in db.session.query(func.distinct(QuestionSets.set_id)).filter(QuestionSets.group_id.in_(group_ids)).all()]
            if group_ids
            else []
        )

        general_set_ids = [
            sid
            for (sid,) in db.session.query(func.distinct(QuestionSets.set_id))
            .filter(
                QuestionSets.general_set.is_(True),
                or_(QuestionSets.company_id.in_(per_company_ids_for_sets), QuestionSets.company_id == GLOBAL_COMPANY_ID),
            )
            .all()
        ]

        role_set_ids = [
            sid
            for (sid,) in (
                db.session.query(func.distinct(Roles.set_id))
                .join(QuestionSets, QuestionSets.set_id == Roles.set_id)
                .filter(
                    Roles.company_id.in_(per_company_ids_for_sets),
                    Roles.set_id.isnot(None),
                    Roles.active.is_(True),
                    QuestionSets.is_active.is_(True),
                )
            ).all()
        ]

        def _fetch_rows(set_ids):
            if not set_ids:
                return []
            return (
                db.session.query(
                    ScreeningQuestions.question_id,
                    ScreeningQuestions.set_id,
                    ScreeningQuestions.position,
                    ScreeningQuestions.question,
                    ScreeningQuestions.response_type,
                )
                .filter(
                    ScreeningQuestions.set_id.in_(set_ids),
                    ScreeningQuestions.is_active.is_(True),
                    ~ScreeningQuestions.question.in_(IGNORED_QUESTIONS),
                )
                .order_by(ScreeningQuestions.position.asc(), ScreeningQuestions.question_id.asc())
                .all()
            )

        group_rows = _fetch_rows(group_set_ids)
        general_rows = _fetch_rows(general_set_ids)
        role_rows = []
        if role_set_ids:
            role_rows = (
                db.session.query(
                    ScreeningQuestions.question_id,
                    ScreeningQuestions.set_id,
                    ScreeningQuestions.position,
                    ScreeningQuestions.question,
                    ScreeningQuestions.response_type,
                )
                .join(Roles, Roles.set_id == ScreeningQuestions.set_id)
                .filter(
                    ScreeningQuestions.set_id.in_(role_set_ids),
                    ScreeningQuestions.is_active.is_(True),
                    Roles.company_id.in_(per_company_ids_for_sets),
                    Roles.active.is_(True),
                    ~ScreeningQuestions.question.in_(IGNORED_QUESTIONS),
                )
                .order_by(ScreeningQuestions.position.asc(), ScreeningQuestions.question_id.asc())
                .all()
            )

        all_qids = [r.question_id for r in group_rows] + [r.question_id for r in general_rows] + [
            r.question_id for r in role_rows
        ]
        counts_map: Dict[int, int] = {}
        if all_qids:
            counts = (
                db.session.query(
                    ScreeningAnswers.question_id.label("qid"),
                    func.count(ScreeningAnswers.question_id).label("cnt"),
                )
                .join(Candidates, Candidates.candidate_id == ScreeningAnswers.candidate_id)
                .filter(
                    company_pred,
                    ScreeningAnswers.created_at >= start,
                    ScreeningAnswers.created_at < end,
                    ScreeningAnswers.question_id.in_(all_qids),
                )
                .group_by(ScreeningAnswers.question_id)
                .all()
            )
            counts_map = {int(qid): int(cnt) for qid, cnt in counts}

        keywords_group = {str(r.question).strip() for r in group_rows}
        keywords_general = {str(r.question).strip() for r in general_rows}
        keywords_role = {str(r.question).strip() for r in role_rows}
        tpl_group = self._templates_ranked_first(list(keywords_group), per_company_ids_for_sets)
        tpl_general = self._templates_ranked_first(list(keywords_general), per_company_ids_for_sets)
        tpl_role = self._templates_ranked_first(list(keywords_role), per_company_ids_for_sets)

        raw_items: List[Dict] = []

        def _append(rows, src_name: str, src_order: int, tpl_map: Dict[str, dict]):
            for r in rows:
                keyword = (r.question or "").strip()
                if not keyword:
                    continue
                tpl = tpl_map.get(keyword)
                resolved_text = (tpl.get("text") if tpl else keyword) if r.response_type in SPECIAL_Q_TYPES else keyword
                options = tpl.get("button_keys") if (tpl and tpl.get("interactive_type") == "button") else []
                total = counts_map.get(int(r.question_id), 0)
                raw_items.append(
                    {
                        "id": int(r.question_id),
                        "keyword": keyword,
                        "resolved_text": resolved_text,
                        "response_type": r.response_type,
                        "total_responses": total,
                        "step_index": int(r.position or 0),
                        "src": src_name,
                        "src_order": src_order,
                        "editable": bool(
                            r.response_type in SPECIAL_Q_TYPES and tpl is not None and tpl.get("company_id") is not None
                        ),
                        "options": options or [],
                    }
                )

        if group_rows:
            _append(group_rows, "group", 1, tpl_group)
        _append(general_rows, "general", 2, tpl_general)
        if role_rows:
            _append(role_rows, "role", 3, tpl_role)

        if include_answers_only and counts_map:
            known_qids = set(all_qids)
            extra_qids = [qid for qid in counts_map.keys() if qid not in known_qids]
            if extra_qids:
                missing_rows = (
                    db.session.query(
                        ScreeningQuestions.question_id,
                        ScreeningQuestions.set_id,
                        ScreeningQuestions.position,
                        ScreeningQuestions.question,
                        ScreeningQuestions.response_type,
                    )
                    .filter(ScreeningQuestions.question_id.in_(extra_qids))
                    .all()
                )
                for r in missing_rows:
                    kw = (r.question or "").strip()
                    if kw in IGNORED_QUESTIONS:
                        continue
                    raw_items.append(
                        {
                            "id": int(r.question_id),
                            "keyword": kw or f"question_{r.question_id}",
                            "resolved_text": kw if r.response_type not in SPECIAL_Q_TYPES else kw,
                            "response_type": r.response_type,
                            "total_responses": counts_map.get(int(r.question_id), 0),
                            "step_index": int(r.position or 0),
                            "src": "answers_only",
                            "src_order": 9,
                            "editable": False,
                            "options": [],
                        }
                    )

        items, _ = self._consolidate_questions(raw_items)

        set_ids_scope = set(group_set_ids) | set(general_set_ids) | set(role_set_ids)
        initial_qids = []
        if set_ids_scope:
            initial_qids = [
                qid
                for (qid,) in db.session.query(ScreeningQuestions.question_id)
                .filter(
                    ScreeningQuestions.set_id.in_(list(set_ids_scope)),
                    ScreeningQuestions.position == 1,
                    ScreeningQuestions.is_active.is_(True),
                    ~ScreeningQuestions.question.in_(IGNORED_QUESTIONS),
                )
                .all()
            ]

        total_initial = 0
        if initial_qids:
            total_initial = (
                db.session.query(func.count())
                .select_from(ScreeningAnswers)
                .join(Candidates, Candidates.candidate_id == ScreeningAnswers.candidate_id)
                .filter(
                    company_pred,
                    ScreeningAnswers.created_at >= start,
                    ScreeningAnswers.created_at < end,
                    ScreeningAnswers.question_id.in_(initial_qids),
                )
            ).scalar() or 0

        last_messages_subq = (
            db.session.query(
                ScreeningMessages.candidate_id,
                func.max(ScreeningMessages.message_serial).label("last_serial"),
            )
            .join(Candidates, Candidates.candidate_id == ScreeningMessages.candidate_id)
            .filter(
                company_pred,
                Candidates.funnel_state == "screening_in_progress",
                ScreeningMessages.time_stamp >= start,
                ScreeningMessages.time_stamp < end,
            )
            .group_by(ScreeningMessages.candidate_id)
            .subquery()
        )
        last_questions_subq = (
            db.session.query(
                ScreeningMessages.candidate_id,
                ScreeningMessages.question_id,
            )
            .join(
                last_messages_subq,
                and_(
                    ScreeningMessages.candidate_id == last_messages_subq.c.candidate_id,
                    ScreeningMessages.message_serial == last_messages_subq.c.last_serial,
                ),
            )
            .subquery()
        )
        resolved_text_expr = case(
            (ScreeningQuestions.response_type.in_(list(SPECIAL_Q_TYPES)), func.coalesce(MessageTemplates.text, ScreeningQuestions.question)),
            else_=ScreeningQuestions.question,
        )
        churn_rows = (
            db.session.query(
                func.substr(resolved_text_expr, 1, 100).label("question"),
                func.count(last_questions_subq.c.candidate_id).label("churn_count"),
            )
            .join(ScreeningQuestions, ScreeningQuestions.question_id == last_questions_subq.c.question_id)
            .outerjoin(MessageTemplates, MessageTemplates.keyword == ScreeningQuestions.question)
            .filter(ScreeningQuestions.is_active.is_(True))
            .group_by(func.substr(resolved_text_expr, 1, 100))
            .order_by(func.count(last_questions_subq.c.candidate_id).desc())
            .all()
        )
        churn_map = {q: int(c) for q, c in churn_rows}

        return {
            "items": items,
            "meta": {"total_initial_responses": int(total_initial)},
            "churn_by_question": churn_map,
        }

    def get_screening_questions_summary2(
        self,
        company_id: int,
        month: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        company_ids: Optional[List[int]] = None,
        scope_all: bool = False,
    ) -> Dict:
        return self.get_screening_questions_summary(
            company_id=company_id,
            month=month,
            start_date=start_date,
            end_date=end_date,
            company_ids=company_ids,
            scope_all=scope_all,
            include_answers_only=False,
        )
