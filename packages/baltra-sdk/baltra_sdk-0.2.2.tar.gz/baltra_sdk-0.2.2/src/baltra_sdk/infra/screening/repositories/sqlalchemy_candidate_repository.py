from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from flask import current_app

from baltra_sdk.domain.screening.entities import CandidateSnapshot
from baltra_sdk.domain.screening.ports import CandidateRepository
from baltra_sdk.legacy.dashboards_folder.models import (
    CandidateFunnelLog,
    Candidates,
    CompaniesScreening,
    CompanyGroups,
    QuestionSets,
    Roles,
    ScreeningMessages,
    ScreeningQuestions,
    db,
)
from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client


class SqlAlchemyCandidateRepository(CandidateRepository):
    """SQLAlchemy-backed repository that mirrors the legacy CandidateDataFetcher behavior."""

    def get_or_create(self, wa_id_user: str, wa_id_system: str) -> CandidateSnapshot:
        session = db.session
        candidate, first_question_flag, latest_message = self._bootstrap_candidate(session, wa_id_user, wa_id_system)
        logging.debug(
            "[SOLID 2.1] SqlAlchemyCandidateRepository.get_or_create candidate_id=%s first_question_flag=%s company_id=%s group_id=%s",
            getattr(candidate, "candidate_id", None),
            first_question_flag,
            getattr(candidate, "company_id", None),
            getattr(candidate, "company_group_id", None),
        )

        thread_id = self._resolve_thread_id(latest_message)
        set_id, question_id = self._resolve_question_cursor(session, candidate, latest_message)
        (
            current_question,
            current_response_type,
            current_position,
            end_interview_answer,
            example_answer,
            next_question,
            next_question_response_type,
            next_question_id,
        ) = self._get_current_and_next_question(session, set_id, question_id)
        (
            next_set_id,
            next_set_first_question,
            next_set_first_question_id,
            next_set_first_question_type,
            role_candidate,
        ) = self._get_next_set_data(session, candidate, set_id)
        (
            company_name,
            company_description,
            company_address,
            company_benefits,
            company_general_faq,
            classifier_assistant_id,
            general_purpose_assistant_id,
            maps_link_json,
            interview_address_json,
            interview_days,
            interview_hours,
            hr_contact,
        ) = self._get_company_context(session, candidate)
        role_context = self._get_role_context(session, candidate)

        payload = self._build_payload(
            candidate=candidate,
            wa_id_user=wa_id_user,
            wa_id_system=wa_id_system,
            thread_id=thread_id,
            first_question_flag=first_question_flag,
            set_id=set_id,
            question_id=question_id,
            current_question=current_question,
            current_response_type=current_response_type,
            current_position=current_position,
            end_interview_answer=end_interview_answer,
            example_answer=example_answer,
            next_question=next_question,
            next_question_response_type=next_question_response_type,
            next_question_id=next_question_id,
            next_set_id=next_set_id,
            next_set_first_question=next_set_first_question,
            next_set_first_question_id=next_set_first_question_id,
            next_set_first_question_type=next_set_first_question_type,
            role_candidate=role_candidate,
            role_context=role_context,
            company_name=company_name,
            company_description=company_description,
            company_address=company_address,
            company_benefits=company_benefits,
            company_general_faq=company_general_faq,
            classifier_assistant_id=classifier_assistant_id,
            general_purpose_assistant_id=general_purpose_assistant_id,
            maps_link_json=maps_link_json,
            interview_address_json=interview_address_json,
            interview_days=interview_days,
            interview_hours=interview_hours,
            hr_contact=hr_contact,
        )

        return CandidateSnapshot(
            candidate_id=candidate.candidate_id,
            wa_id_user=wa_id_user,
            wa_id_system=wa_id_system,
            funnel_state=payload.get("funnel_state", "screening_in_progress"),
            current_question=payload.get("current_question"),
            next_question=payload.get("next_question"),
            first_question_flag=payload.get("first_question_flag", False),
            raw_payload=payload,
        )

    # ---------------------------------------------------------------------#
    # Candidate bootstrap helpers
    # ---------------------------------------------------------------------#
    def _bootstrap_candidate(
        self,
        session,
        wa_id_user: str,
        wa_id_system: str,
    ) -> Tuple[Candidates, bool, Optional[ScreeningMessages]]:
        company_group = (
            session.query(CompanyGroups)
            .filter(CompanyGroups.wa_id == wa_id_system)
            .first()
        )
        company: Optional[CompaniesScreening] = None
        candidate: Optional[Candidates] = None

        if company_group:
            candidate = (
                session.query(Candidates)
                .filter(
                    Candidates.phone == wa_id_user,
                    Candidates.company_group_id == company_group.group_id,
                )
                .order_by(Candidates.created_at.desc())
                .first()
            )
            logging.debug(
                "[SOLID 2.2] Bootstrap lookup by group_id=%s found=%s",
                company_group.group_id,
                bool(candidate),
            )
        else:
            company = (
                session.query(CompaniesScreening)
                .filter(CompaniesScreening.wa_id == wa_id_system)
                .first()
            )
            if company is None:
                raise ValueError(f"No company configured for wa_id_system={wa_id_system}")
            candidate = (
                session.query(Candidates)
                .filter(
                    Candidates.phone == wa_id_user,
                    Candidates.company_id == company.company_id,
                )
                .order_by(Candidates.created_at.desc())
                .first()
            )
            logging.debug(
                "[SOLID 2.3] Bootstrap lookup by company_id=%s found=%s",
                company.company_id,
                bool(candidate),
            )

        first_question_flag = False
        latest_message: Optional[ScreeningMessages] = None

        if candidate is None:
            candidate = self._create_candidate(session, wa_id_user, company=company, company_group=company_group)
            first_question_flag = True
        else:
            latest_message = self._get_latest_message(session, candidate)
            if self._is_candidate_expired(latest_message):
                self._mark_candidate_expired(session, candidate)
                candidate = self._create_candidate(session, wa_id_user, company=candidate.company or company, company_group=company_group)
                latest_message = None
                first_question_flag = True

        return candidate, first_question_flag, latest_message

    def _create_candidate(
        self,
        session,
        wa_id_user: str,
        company: Optional[CompaniesScreening],
        company_group: Optional[CompanyGroups],
    ) -> Candidates:
        if company is None and company_group is None:
            raise ValueError("Cannot create candidate without a company or company group binding.")
        candidate = Candidates(
            phone=wa_id_user,
            company_id=company.company_id if company else None,
            company_group_id=company_group.group_id if company_group else None,
            name="",
            funnel_state="screening_in_progress",
            flow_state="respuesta",
            created_at=datetime.utcnow(),
        )
        session.add(candidate)
        session.commit()
        logging.info(
            "[SOLID 2.4] Created new candidate id=%s for wa_id=%s (company_id=%s, group_id=%s)",
            candidate.candidate_id,
            wa_id_user,
            candidate.company_id,
            candidate.company_group_id,
        )
        return candidate

    def _get_latest_message(self, session, candidate: Candidates) -> Optional[ScreeningMessages]:
        return (
            session.query(ScreeningMessages)
            .filter(ScreeningMessages.candidate_id == candidate.candidate_id)
            .order_by(ScreeningMessages.time_stamp.desc())
            .first()
        )

    def _is_candidate_expired(self, latest_message: Optional[ScreeningMessages]) -> bool:
        if latest_message is None or latest_message.time_stamp is None:
            return False
        expiration_days = int(current_app.config.get("SCREENING_EXPIRATION_DAYS", 21))
        return datetime.utcnow() - latest_message.time_stamp > timedelta(days=expiration_days)

    def _mark_candidate_expired(self, session, candidate: Candidates) -> None:
        previous_state = candidate.funnel_state or ""
        if previous_state != "expired":
            try:
                log_entry = CandidateFunnelLog(
                    candidate_id=candidate.candidate_id,
                    previous_funnel_state=previous_state,
                    new_funnel_state="expired",
                    changed_at=datetime.utcnow(),
                )
                session.add(log_entry)
                session.commit()
                logging.info("Logged funnel state change for candidate %s: %s -> expired", candidate.candidate_id, previous_state)
            except Exception:
                session.rollback()
                logging.error("Failed to log funnel state change for candidate %s", candidate.candidate_id, exc_info=True)

        candidate.funnel_state = "expired"
        try:
            session.commit()
        except Exception:
            session.rollback()
            logging.error("Failed to persist expired state for candidate %s", candidate.candidate_id, exc_info=True)

    # ---------------------------------------------------------------------#
    # Question cursor helpers
    # ---------------------------------------------------------------------#
    def _resolve_thread_id(self, latest_message: Optional[ScreeningMessages]) -> str:
        if latest_message and latest_message.thread_id:
            return latest_message.thread_id
        return self._create_thread_id()

    def _resolve_question_cursor(
        self,
        session,
        candidate: Candidates,
        latest_message: Optional[ScreeningMessages],
    ) -> Tuple[int, int]:
        if latest_message and latest_message.set_id and latest_message.question_id:
            return latest_message.set_id, latest_message.question_id

        if candidate.company_id:
            set_obj = (
                session.query(QuestionSets)
                .filter(
                    QuestionSets.company_id == candidate.company_id,
                    QuestionSets.general_set.is_(True),
                    QuestionSets.is_active.is_(True),
                )
                .order_by(QuestionSets.created_at.desc())
                .first()
            )
        elif candidate.company_group_id:
            set_obj = (
                session.query(QuestionSets)
                .filter(
                    QuestionSets.group_id == candidate.company_group_id,
                    QuestionSets.is_active.is_(True),
                )
                .order_by(QuestionSets.created_at.desc())
                .first()
            )
        else:
            set_obj = None

        if not set_obj:
            raise ValueError(f"No active question set configured for candidate {candidate.candidate_id}")

        question = (
            session.query(ScreeningQuestions)
            .filter(
                ScreeningQuestions.set_id == set_obj.set_id,
                ScreeningQuestions.position == 1,
                ScreeningQuestions.is_active.is_(True),
            )
            .first()
        )
        if question is None:
            raise ValueError(f"Question set {set_obj.set_id} does not contain a valid first question.")
        return set_obj.set_id, question.question_id

    def _get_current_and_next_question(
        self,
        session,
        set_id: int,
        question_id: int,
    ) -> Tuple[
        Optional[str],
        Optional[str],
        int,
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[int],
    ]:
        current = session.query(ScreeningQuestions).filter(ScreeningQuestions.question_id == question_id).first()
        if current is None:
            logging.warning("No question found with ID %s inside set %s", question_id, set_id)
            return None, None, 1, None, None, None, None, None

        next_q = (
            session.query(ScreeningQuestions)
            .filter(
                ScreeningQuestions.set_id == set_id,
                ScreeningQuestions.position == current.position + 1,
                ScreeningQuestions.is_active.is_(True),
            )
            .first()
        )

        return (
            current.question,
            current.response_type,
            current.position or 1,
            current.end_interview_answer,
            current.example_answer,
            next_q.question if next_q else None,
            next_q.response_type if next_q else None,
            next_q.question_id if next_q else None,
        )

    def _get_next_set_data(
        self,
        session,
        candidate: Candidates,
        set_id: int,
    ) -> Tuple[Optional[int], Optional[str], Optional[int], Optional[str], Optional[Roles]]:
        current_set_obj = session.query(QuestionSets).filter(QuestionSets.set_id == set_id).first()
        if (
            current_set_obj
            and current_set_obj.group_id
            and not current_set_obj.company_id
            and candidate.company_id
        ):
            general_set_obj = (
                session.query(QuestionSets)
                .filter(
                    QuestionSets.company_id == candidate.company_id,
                    QuestionSets.general_set.is_(True),
                )
                .first()
            )
            if general_set_obj:
                first_question = (
                    session.query(ScreeningQuestions)
                    .filter(
                        ScreeningQuestions.set_id == general_set_obj.set_id,
                        ScreeningQuestions.position == 1,
                        ScreeningQuestions.is_active.is_(True),
                    )
                    .first()
                )
                if first_question:
                    return (
                        first_question.set_id,
                        first_question.question,
                        first_question.question_id,
                        first_question.response_type,
                        None,
                    )

        is_general_set = session.query(QuestionSets.general_set).filter(QuestionSets.set_id == set_id).scalar()
        if is_general_set is False:
            return None, None, None, None, None

        role: Optional[Roles] = None
        if candidate.role_id:
            role = session.query(Roles).filter(Roles.role_id == candidate.role_id).first()
        elif candidate.company_id:
            role = (
                session.query(Roles)
                .filter(
                    Roles.company_id == candidate.company_id,
                    Roles.default_role.is_(True),
                )
                .first()
            )

        if role and role.set_id:
            first_question = (
                session.query(ScreeningQuestions)
                .filter(
                    ScreeningQuestions.set_id == role.set_id,
                    ScreeningQuestions.position == 1,
                    ScreeningQuestions.is_active.is_(True),
                )
                .first()
            )
            if first_question:
                return (
                    role.set_id,
                    first_question.question,
                    first_question.question_id,
                    first_question.response_type,
                    role,
                )

        return None, None, None, None, role

    # ---------------------------------------------------------------------#
    # Context builders
    # ---------------------------------------------------------------------#
    def _get_company_context(
        self,
        session,
        candidate: Candidates,
    ) -> Tuple[str, str, str, Any, Any, str, str, Dict[str, Any], Dict[str, Any], Any, Any, Optional[str]]:
        if candidate.company_id:
            company = session.query(CompaniesScreening).filter(CompaniesScreening.company_id == candidate.company_id).first()
            if company:
                return (
                    company.name or "",
                    company.description or "",
                    company.address or "",
                    company.benefits or [],
                    company.general_faq or {},
                    company.classifier_assistant_id or "",
                    company.general_purpose_assistant_id or "",
                    company.maps_link_json or {},
                    company.interview_address_json or {},
                    company.interview_days,
                    company.interview_hours,
                    company.hr_contact,
                )

        if candidate.company_group_id:
            group = session.query(CompanyGroups).filter(CompanyGroups.group_id == candidate.company_group_id).first()
            if group:
                return (
                    group.name or "",
                    group.description or "",
                    "",
                    [],
                    {},
                    "asst_iBUlpF7FISkh3oY8Pr3bmVUb",
                    "asst_drleBzh2ufZ79J7MHeocfp5X",
                    {},
                    {},
                    None,
                    None,
                    None,
                )

        return "", "", "", [], {}, "", "", {}, {}, None, None, None

    def _get_role_context(self, session, candidate: Candidates) -> str:
        if candidate.role_id:
            role = session.query(Roles).filter(Roles.role_id == candidate.role_id).first()
            if role:
                role_info = str(role.role_info) if role.role_info else "Sin información adicional"
                return f"- {role.role_name}: {role_info}"
            return "No se encontró información del rol asignado"

        if candidate.company_id:
            roles = session.query(Roles).filter(Roles.company_id == candidate.company_id).all()
            if roles:
                lines = []
                for role in roles:
                    info = str(role.role_info) if role.role_info else "Sin información adicional"
                    lines.append(f"- {role.role_name}: {info}")
                return "El candidato aún no ha seleccionado un rol. A continuación se muestra información de todos los roles disponibles en la empresa:\n" + "\n".join(lines)

        return "No se encontraron roles para esta empresa"

    def _build_payload(
        self,
        candidate: Candidates,
        wa_id_user: str,
        wa_id_system: str,
        thread_id: str,
        first_question_flag: bool,
        set_id: int,
        question_id: int,
        current_question: Optional[str],
        current_response_type: Optional[str],
        current_position: int,
        end_interview_answer: Optional[str],
        example_answer: Optional[str],
        next_question: Optional[str],
        next_question_response_type: Optional[str],
        next_question_id: Optional[int],
        next_set_id: Optional[int],
        next_set_first_question: Optional[str],
        next_set_first_question_id: Optional[int],
        next_set_first_question_type: Optional[str],
        role_candidate: Optional[Roles],
        role_context: str,
        company_name: str,
        company_description: str,
        company_address: str,
        company_benefits,
        company_general_faq,
        classifier_assistant_id: str,
        general_purpose_assistant_id: str,
        maps_link_json: Dict[str, Any],
        interview_address_json: Dict[str, Any],
        interview_days,
        interview_hours,
        hr_contact: Optional[str],
    ) -> Dict[str, Any]:
        interview_date_str = (
            candidate.interview_date_time.strftime("%d/%m/%Y %I:%M %p")
            if candidate.interview_date_time
            else ""
        )

        company_context = {
            "Descripción": company_description,
            "Ubicación_Vacante": company_address,
            "Beneficios": company_benefits,
            "Preguntas_Frecuentes": company_general_faq,
            "Dias_Entrevista": interview_days,
            "Horarios_Entrevista": interview_hours,
            "hr_contact": hr_contact if candidate.funnel_state == "scheduled_interview" else None,
        }

        payload = {
            "wa_id": wa_id_user,
            "wa_id_system": wa_id_system,
            "candidate_id": candidate.candidate_id,
            "first_name": candidate.name,
            "flow_state": candidate.flow_state or "respuesta",
            "first_question_flag": first_question_flag,
            "company_group_id": candidate.company_group_id,
            "company_id": candidate.company_id,
            "company_name": company_name,
            "thread_id": thread_id,
            "classifier_assistant_id": classifier_assistant_id,
            "general_purpose_assistant_id": general_purpose_assistant_id,
            "set_id": set_id,
            "next_set_id": next_set_id,
            "question_id": question_id,
            "current_question": current_question,
            "current_response_type": current_response_type,
            "current_position": current_position,
            "end_interview_answer": end_interview_answer,
            "example_answer": example_answer,
            "next_question": next_question,
            "next_question_response_type": next_question_response_type,
            "next_question_id": next_question_id,
            "next_set_first_question": next_set_first_question,
            "next_set_first_question_id": next_set_first_question_id,
            "next_set_first_question_type": next_set_first_question_type,
            "company_context": json.dumps(company_context, ensure_ascii=False),
            "role": role_candidate.role_name if role_candidate else (candidate.role.role_name if candidate.role else None),
            "role_context": role_context,
            "travel_time_minutes": candidate.travel_time_minutes,
            "funnel_state": candidate.funnel_state or "screening_in_progress",
            "end_flow_rejected": bool(candidate.end_flow_rejected),
            "interview_date": interview_date_str,
            "interview_address": candidate.interview_address,
            "eligible_roles": candidate.eligible_roles or [],
            "maps_link_json": maps_link_json or {},
            "interview_address_json": interview_address_json or {},
        }
        return payload

    def _create_thread_id(self) -> str:
        client = get_openai_client()
        thread = client.beta.threads.create()
        return thread.id
