import logging
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from baltra_sdk.legacy.dashboards_folder.models import (
    Candidates, Roles, db, ScreeningMessages, 
    CompaniesScreening, ScreeningAnswers, CandidateReferences,
    CandidateMedia, CandidateFunnelLog, ReferenceMessages,
    EligibilityEvaluationLog, PhoneInterviews, OnboardingResponses
)
from sqlalchemy import or_, func, and_
from baltra_sdk.shared.utils.screening.reminders import send_message_template_to_candidate
from flask import current_app

from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from baltra_sdk.shared.mixpanel.metrics_screening import send_funnel_state_mixpanel
from baltra_sdk.shared.utils.screening.sql_utils import log_funnel_state_change


logger = logging.getLogger(__name__)

class CandidatesService:
    """Service for managing candidate data with efficient queries and error handling"""
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
        self.company_id = company_id
    
    def get_all_candidates(self) -> List[Dict]:
        """Retrieve all candidates for the company with role information"""
        try:
            candidates = db.session.query(Candidates, Roles.role_name).outerjoin(
                Roles, Candidates.role_id == Roles.role_id
            ).filter(
                Candidates.company_id == self.company_id
            ).order_by(Candidates.created_at.desc()).all()
            
            return [self._format_candidate_data(candidate, role_name) for candidate, role_name in candidates]
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching candidates: {str(e)}")
            raise RuntimeError("Error retrieving candidates from database")
    
    def _format_candidate_data(self, candidate: Candidates, role_name: Optional[str]) -> Dict:
        """Format candidate data for frontend display"""
        # Get all media URLs for this candidate
        media_urls = self._get_candidate_media_urls(candidate.candidate_id)
        
        # Get the previous funnel state from logs (useful for expired candidates)
        previous_state = self._get_previous_funnel_state(candidate.candidate_id, candidate.funnel_state)
        
        return {
            "id": candidate.candidate_id,
            "name": candidate.name or "Nombre por definir",
            "created_at": candidate.created_at.strftime("%b %d, %Y") if candidate.created_at else "N/A",
            "role": role_name or "N/A",
            "phone": candidate.phone,
            "screening_date": candidate.created_at.strftime("%b %d, %Y") if candidate.created_at else "N/A",
            "interview_date": candidate.interview_date_time if candidate.interview_date_time else None,
            "recommendation": self._get_recommendation_status(candidate.funnel_state, candidate.grade),
            "score": f"{candidate.grade}%" if candidate.grade is not None else "N/A",
            "funnel_state": self._get_funnel_status(candidate.funnel_state),
            "previous_funnel_state": self._get_funnel_status(previous_state) if previous_state else None,
            "travel_time_minutes": candidate.travel_time_minutes if candidate.travel_time_minutes is not None else "N/A",
            "interview_address": candidate.interview_address,
            "interview_map_link": candidate.interview_map_link,
            "media_urls": media_urls,
            "rejected_reason":  candidate.rejected_reason, 
            "rescheduled": candidate.reschedule_sent,
            "worked_here": candidate.worked_here,
        }
    
    def _get_recommendation_status(self, funnel_state: Optional[str], grade: Optional[int]) -> str:
        """Map grade to recommendation status, with special handling for rejected candidates"""
        # If explicitly rejected, always return "Rejected"
        if funnel_state == "rejected":
            return "Rechazado"
        
        # If no grade available, return TBD
        if grade is None:
            return "TBD"
        
        # Convert grade to decimal (assuming grade is stored as percentage 0-100)
        grade_decimal = grade / 100.0
        
        if grade_decimal < 0.6:
            return "No Recomendado"
        elif grade_decimal <= 0.8:
            return "Recomendado"
        else:
            return "Muy Recomendado"
    
    def _get_funnel_status(self, funnel_state: Optional[str]) -> str:
        """Map funnel state to action status"""
        action_map = {
            "rejected": "Rechazado",
            "scheduled_interview": "Entrevista Agendada", 
            "screening_in_progress": "En Progreso",
            "hired": "Contratado",
            "missed_interview" : "Faltó a Entrevista",
            "document_verification": "Verificación de Documentos",
            "verified": "Verificado",
            "expired": "Expirado",
            "onboarding": "Contratado",
        }
        return action_map.get(funnel_state, "En Progreso")
    
    def change_funnel_state(self, candidate_id: int, new_state: str, reason: str = None, start_date: Optional[str] = None) -> None:
        """Change the funnel state of a candidate"""
        states = [
            "screening_in_progress", 

            "phone_interview_cited",
            "phone_interview",
            "phone_interview_demo",
            "phone_interview_passed",

            "scheduled_interview", 

            "rejected", 
            "hired", 
            "missed_interview", 
            "cancelled", 
            "document_verification",
        ]
        if new_state not in states:
            new_state = "screening_in_progress"
            
        try:
            candidate = Candidates.query.filter_by(
                candidate_id=candidate_id,
                company_id=self.company_id
            ).first()
            
            if not candidate:
                raise ValueError(f"Candidate with ID {candidate_id} not found")
            
            # Parse start_date if provided (expects YYYY-MM-DD)
            parsed_start_date = None
            if start_date:
                try:
                    parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                except Exception:
                    # Ignore parsing errors and fallback to default behavior
                    parsed_start_date = None
            
            # Regular funnel state change for all candidates
            self._transition_funnel_state(candidate, candidate_id, new_state, reason, parsed_start_date)
            
            if new_state == "missed_interview":
                # Send reschedule message if not already sent
                if not candidate.reschedule_sent:
                    # Determine which message template to use based on company ID
                    template_keyword = "reschedule_interview" #TODO: Add logic to determine which message template to use based on company ID
                    
                    # Send the reschedule message
                    message_sent = send_message_template_to_candidate(
                        template_keyword=template_keyword,
                        candidate_id=candidate_id,
                        current_app=current_app
                    )
                    
                    if message_sent:
                        candidate.reschedule_sent = True
                        logger.info(f"Reschedule message ({template_keyword}) sent to candidate {candidate_id} for company {self.company_id}")
                    else:
                        logger.error(f"Failed to send reschedule message to candidate {candidate_id}")
                else:
                    logger.info(f"Reschedule message already sent to candidate {candidate_id}")
            
            db.session.commit()
            return True
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when changing funnel state: {str(e)}")
            raise RuntimeError("Error changing funnel state in database")
        except ValueError as ve:
            logger.error(str(ve))
            return False
    
    def _transition_funnel_state(self, candidate: Candidates, candidate_id: int, new_state: str, reason: str = None, start_date_value: Optional[date] = None) -> None:
        """Helper method to transition funnel state and log the change"""
        previous_state = candidate.funnel_state
        
        # Log the state change if it's actually changing
        if previous_state != new_state:
            log_funnel_state_change(candidate_id, previous_state, new_state)
        
        # Update the candidate's funnel state
        candidate.funnel_state = new_state
        if new_state == "rejected":
            candidate.rejected_reason = reason
        
        # Send event to mixpanel
        send_funnel_state_mixpanel(candidate_id, new_state, candidate.company_id, reason)
        
        # Set start_date if transitioning to hired
        if new_state == "hired":
            # If provided, use the given date; otherwise default to today
            candidate.start_date = start_date_value or (date.today() + timedelta(days=1))

    def cancel_interview(self, candidate_id: int) -> bool:
        """Cancel a candidate's interview and send cancelar_entrevista template"""
        try:
            candidate = Candidates.query.filter_by(
                candidate_id=candidate_id,
                company_id=self.company_id
            ).first()
            
            if not candidate:
                raise ValueError(f"Candidate with ID {candidate_id} not found")
            
            # Log change of state
            previous_state = candidate.funnel_state
            new_state = "cancelled"
            log_funnel_state_change(candidate_id, previous_state, new_state)
            
            # Update the funnel state to cancelled
            candidate.funnel_state = new_state
            candidate.rejected_reason = "interview_cancelled"
            
            # Send event to mixpanel
            send_funnel_state_mixpanel(candidate_id, new_state, candidate.company_id, "interview_cancelled")
            
            # Send the cancellation message
            template_keyword = "cancelar_entrevista"
            message_sent = send_message_template_to_candidate(
                template_keyword=template_keyword,
                candidate_id=candidate_id,
                current_app=current_app
            )
            
            if message_sent:
                logger.info(f"Cancellation message ({template_keyword}) sent to candidate {candidate_id} for company {self.company_id}")
            else:
                logger.error(f"Failed to send cancellation message to candidate {candidate_id}")
                # Still proceed with cancellation even if message fails
            
            db.session.commit()
            return True
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when cancelling interview: {str(e)}")
            raise RuntimeError("Error cancelling interview in database")
        except ValueError as ve:
            logger.error(str(ve))
            return False
        
    def remove_candidate(self, candidate_id: int) -> bool:
        """Remove a candidate from the database"""
        try:
            logger.info(
                f"[remove_candidate] Starting deletion for candidate_id={candidate_id}, company_id={self.company_id}"
            )
            # First check if candidate exists
            candidate = Candidates.query.filter_by(
                candidate_id=candidate_id,
                company_id=self.company_id
            ).first()
            
            if not candidate:
                raise ValueError(f"Candidate with ID {candidate_id} not found")
            
            # Get the company screening record to get the correct company_id for screening_messages
            # Find the companies_screening record that matches our regular company
            company_screening = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
            logger.info(
                f"[remove_candidate] Matched CompaniesScreening record: {bool(company_screening)}"
            )

            # Pre-delete diagnostics: count dependent rows
            total_screening_msgs = db.session.query(ScreeningMessages).filter_by(candidate_id=candidate_id).count()
            filtered_screening_msgs = (
                db.session.query(ScreeningMessages)
                .filter_by(candidate_id=candidate_id, company_id=company_screening.company_id)
                .count()
                if company_screening else None
            )
            answers_count = db.session.query(ScreeningAnswers).filter_by(candidate_id=candidate_id).count()
            refs_count = db.session.query(CandidateReferences).filter_by(candidate_id=candidate_id).count()
            ref_msgs_count = (
                db.session.query(ReferenceMessages)
                .join(CandidateReferences, ReferenceMessages.reference_id == CandidateReferences.reference_id)
                .filter(CandidateReferences.candidate_id == candidate_id)
                .count()
            )
            media_count = db.session.query(CandidateMedia).filter_by(candidate_id=candidate_id).count()
            funnel_logs_count = db.session.query(CandidateFunnelLog).filter_by(candidate_id=candidate_id).count()
            eligibility_logs_count = db.session.query(EligibilityEvaluationLog).filter_by(candidate_id=candidate_id).count()
            phone_interviews_count = db.session.query(PhoneInterviews).filter_by(candidate_id=candidate_id).count()
            onboarding_responses_count = db.session.query(OnboardingResponses).filter_by(candidate_id=candidate_id).count()

            logger.info(
                f"[remove_candidate] Pre-delete counts -> ScreeningMessages(total={total_screening_msgs}, filtered={filtered_screening_msgs}), "
                f"ScreeningAnswers={answers_count}, CandidateReferences={refs_count}, ReferenceMessages={ref_msgs_count}, "
                f"CandidateMedia={media_count}, CandidateFunnelLog={funnel_logs_count}, EligibilityEvaluationLog={eligibility_logs_count}, "
                f"PhoneInterviews={phone_interviews_count}, OnboardingResponses={onboarding_responses_count}"
            )
            
            # Delete screening messages using the correct company_id reference
            if company_screening:
                deleted_msgs = ScreeningMessages.query.filter_by(
                    candidate_id=candidate_id,
                    company_id=company_screening.company_id  # Use the screening company_id
                ).delete(synchronize_session=False)
                logger.info(f"[remove_candidate] Deleted ScreeningMessages (filtered by company): {deleted_msgs}")
                # Safety net: if there are still messages for this candidate with mismatched company_id, delete them too
                remaining_msgs = db.session.query(ScreeningMessages).filter_by(candidate_id=candidate_id).count()
                if remaining_msgs:
                    deleted_msgs_any = ScreeningMessages.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
                    logger.warning(
                        f"[remove_candidate] Found {remaining_msgs} ScreeningMessages with mismatched company_id. "
                        f"Deleted additional records: {deleted_msgs_any}"
                    )
            else:
                # Fallback: delete all screening messages for this candidate regardless of company
                deleted_msgs = ScreeningMessages.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
                logger.info(f"[remove_candidate] Deleted ScreeningMessages (all companies): {deleted_msgs}")
            
            # Delete screening answers (should cascade automatically, but being explicit)
            deleted_answers = ScreeningAnswers.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted ScreeningAnswers: {deleted_answers}")
            
            # Delete candidate references (should cascade automatically, but being explicit)
            deleted_refs = CandidateReferences.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted CandidateReferences: {deleted_refs}")

            # Explicitly delete candidate media (defensive in case FK cascade is missing)
            deleted_media = CandidateMedia.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted CandidateMedia: {deleted_media}")

            # Explicitly delete candidate funnel logs (defensive)
            deleted_funnel_logs = CandidateFunnelLog.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted CandidateFunnelLog: {deleted_funnel_logs}")

            # Explicitly delete eligibility evaluation logs (defensive)
            deleted_eligibility_logs = EligibilityEvaluationLog.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted EligibilityEvaluationLog: {deleted_eligibility_logs}")

            # Explicitly delete phone interviews (defensive, should cascade but being explicit)
            deleted_phone_interviews = PhoneInterviews.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted PhoneInterviews: {deleted_phone_interviews}")

            # Explicitly delete onboarding responses (defensive, should cascade but being explicit)
            deleted_onboarding_responses = OnboardingResponses.query.filter_by(candidate_id=candidate_id).delete(synchronize_session=False)
            logger.info(f"[remove_candidate] Deleted OnboardingResponses: {deleted_onboarding_responses}")

            # Delete the candidate (this should cascade to other related records)
            db.session.delete(candidate)
            db.session.commit()
            logger.info(f"[remove_candidate] Successfully committed deletion for candidate_id={candidate_id}")
            return True
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"[remove_candidate] Database error when removing candidate_id={candidate_id}: {str(e)}")
            logger.error(f"[remove_candidate] SQLAlchemy error type: {type(e).__name__}")
            # For IntegrityError include orig and params if available
            if isinstance(e, exc.IntegrityError):
                try:
                    logger.error(f"[remove_candidate] IntegrityError.orig: {getattr(e, 'orig', None)}")
                    logger.error(f"[remove_candidate] IntegrityError.params: {getattr(e, 'params', None)}")
                    logger.error(f"[remove_candidate] Statement: {getattr(e, 'statement', None)}")
                except Exception:
                    pass
            raise RuntimeError(f"Error removing candidate from database: {str(e)}")
        except ValueError as ve:
            logger.error(str(ve))
            return False

    def get_available_funnel_states(self) -> List[Dict[str, str]]:
        """Get list of available funnel states for filtering"""
        try:
            # Obtener estados únicos de la base de datos
            db_states = db.session.query(Candidates.funnel_state).filter(
                Candidates.company_id == self.company_id,
                Candidates.funnel_state.isnot(None)
            ).distinct().all()
            
            # Convertir a lista y mapear a estados amigables
            states = []
            for state_tuple in db_states:
                db_state = state_tuple[0]
                if db_state:
                    friendly_state = self._get_funnel_status(db_state)
                    states.append({
                        "value": db_state,  # Valor para el filtro
                        "label": friendly_state,  # Texto para mostrar
                        "display": friendly_state
                    })
            
            # Ordenar por label
            states.sort(key=lambda x: x['label'])
            
            return states
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching funnel states: {str(e)}")
            return []

    def get_funnel_states_summary(self) -> Dict[str, int]:
        """Get count of candidates by funnel state using candidate_funnel_logs"""
        try:
            # Count distinct candidates who have ever been in each funnel state
            states_count = db.session.query(
                CandidateFunnelLog.new_funnel_state,
                func.count(func.distinct(CandidateFunnelLog.candidate_id)).label('count')
            ).join(
                Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
            ).filter(
                Candidates.company_id == self.company_id
            ).group_by(CandidateFunnelLog.new_funnel_state).all()
            
            summary = {}
            for state, count in states_count:
                friendly_state = self._get_funnel_status(state)
                summary[friendly_state] = count
                
            return summary
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching funnel states summary: {str(e)}")
            return {}


    def get_candidates_count_by_interview_address(self, interview_date: Optional[datetime] = None) -> Dict[str, int]:
      """
      Get count of candidates grouped by interview address for a specific date.
      
      Args:
      interview_date: Date to filter interviews. Defaults to today.
      
      Returns:
      Dict with interview addresses as keys and candidate counts as values.
      Candidates without address are grouped under "Sin dirección".
      """
      try:
          if interview_date is None:
            interview_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
          
          # Query to get candidates grouped by interview address for the specified date
          results = db.session.query(
            Candidates.interview_address,
            func.count(Candidates.candidate_id).label('count')
          ).filter(
            Candidates.company_id == self.company_id,
            Candidates.interview_date_time.isnot(None),
            func.date(Candidates.interview_date_time) == interview_date.date()
          ).group_by(Candidates.interview_address).all()
          
          # Convert to dictionary
          address_counts = {}
          for address, count in results:
              if address is None or address.strip() == "":
                  address_counts["none"] = address_counts.get("none", 0) + count
              else:
                  address_counts[address] = count
            
          return address_counts
      
      except exc.SQLAlchemyError as e:
          logger.error(f"Database error when fetching candidates by interview address: {str(e)}")
      return {}
    
    def get_all_candidates_pagination(
      self, 
      page: int = 1, 
      per_page: int = 20, 
      search_query: Optional[str] = None,
      role_filter: Optional[str] = None,
      funnel_state_filter: Optional[str] = None,
      interview_date_filter: Optional[str] = None,  # "upcoming", "completed", or None
      score_filter: Optional[str] = None,           # e.g. "0-59", "60-80", "81-100"
      interview_date_exact: Optional[str] = None,   # Exact date in YYYY-MM-DD format
      interview_address_filter: Optional[str] = None, # Filter by interview address
      reject_phase_filter: Optional[str] = None,   # "pre_screening", "post_screening", or None
      only_hired_onboarding_expired: bool = False,  # Only include expired candidates who were hired/onboarding
      ) -> Dict:
      """
        Retrieve candidates with pagination, search, and interview date filtering.

        Args:
        page: Page number (starts from 1)
        per_page: Number of candidates per page
        search_query: Text to search in candidate name, phone, etc.
        role_filter: Filter by specific role name
        funnel_state_filter: Filter by funnel state (rejected, scheduled_interview, etc.)
        interview_date_filter: "upcoming" (today or future), "completed" (past), or None
        score_filter: Filter by score range as string, e.g. "0-59", "60-80", "81-100"
        interview_date_exact: Exact date in YYYY-MM-DD format
        interview_address_filter: Filter by interview address
        reject_phase_filter: "pre_screening", "post_screening", or None

        Returns:
        Dict with candidates, pagination info, and totals
        """
      try:
        # Base query
        query = db.session.query(Candidates, Roles.role_name).outerjoin(
          Roles, Candidates.role_id == Roles.role_id
        ).filter(
          Candidates.company_id == self.company_id
        )

        # Apply search filter with pg_trgm for fuzzy search on name, phone, and role
        if search_query:
          search_filter = or_(
            # Use pg_trgm similarity for fuzzy search on name
            func.similarity(Candidates.name, search_query) > 0.1,
            # Use pg_trgm similarity for fuzzy search on phone
            func.similarity(Candidates.phone, search_query) > 0.1,
            # Use pg_trgm similarity for fuzzy search on role name
            func.similarity(Roles.role_name, search_query) > 0.1
          )
          query = query.filter(search_filter)
        print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))

        # Apply role filter
        if role_filter:
          query = query.filter(func.lower(Roles.role_name) == func.lower(role_filter))

        # Apply funnel state filter
        if funnel_state_filter:
          normalized_filter = funnel_state_filter.lower()
          state_mapping = {
          "rejected": "rejected",
          "interview scheduled": "scheduled_interview",
          "screening in progress": "screening_in_progress", 
          "hired": "hired",
          "missed interview": "missed_interview",
          "verificación de documentos": "document_verification",
          "verified": "verified",
          "expired": "expired"
          }
          db_state = state_mapping.get(normalized_filter, normalized_filter)
          
          # Special handling for expired state: only include candidates who were hired/onboarding
          # This is only applied when explicitly requested via only_hired_onboarding_expired parameter
          if db_state == "expired" and only_hired_onboarding_expired:
            # Subquery to find expired candidates who have been hired or onboarding
            hired_onboarding_subquery = db.session.query(
              CandidateFunnelLog.candidate_id
            ).filter(
              CandidateFunnelLog.new_funnel_state.in_(['hired', 'onboarding'])
            ).distinct()
            
            query = query.filter(
              Candidates.funnel_state == 'expired',
              Candidates.rejected_reason.is_(None),
              Candidates.candidate_id.in_(hired_onboarding_subquery)
            )
          else:
            query = query.filter(
            or_(
              func.lower(Candidates.funnel_state) == db_state,
              func.lower(Candidates.funnel_state) == normalized_filter
            )
            )

        # Apply screening phase filter
        if reject_phase_filter:
          if reject_phase_filter.lower() == "pre_screening":
            # Pre-screening: rejected with reason "screening" OR screening_in_progress
            query = query.filter(

              Candidates.funnel_state == "rejected",
              Candidates.rejected_reason == "screening"

            )
          elif reject_phase_filter.lower() == "post_screening":
            # Post-screening: scheduled_interview, hired, missed_interview, or rejected with reason != "screening"
            query = query.filter(
              Candidates.funnel_state == "rejected",
              Candidates.rejected_reason != "screening"
            )

        # Apply interview date exact filter (takes priority over date range filter)
        if interview_date_exact:
          try:
            if interview_date_exact.lower() != "none":
                exact_date = datetime.strptime(interview_date_exact, "%Y-%m-%d").date()
                query = query.filter(
                    Candidates.interview_date_time.isnot(None),
                    func.date(Candidates.interview_date_time) == exact_date
                )
            else:
                query = query.filter(Candidates.interview_date_time.is_(None))
          except ValueError:
            pass  # Ignore invalid date format
        # Apply interview date range filter only if no exact date is specified
        elif interview_date_filter in ("upcoming", "completed"):
          today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
          if interview_date_filter == "upcoming":
            # Interview today or in the future
            query = query.filter(
              Candidates.interview_date_time.isnot(None),
              func.date(Candidates.interview_date_time) >= today.date()
            )
          elif interview_date_filter == "completed":
          # Interview in the past
            query = query.filter(
              Candidates.interview_date_time.isnot(None),
              func.date(Candidates.interview_date_time) < today.date()
            )

        # Apply interview address filter
        if interview_address_filter:
          
          if interview_address_filter.lower() != "none":
            
              query = query.filter(
              Candidates.interview_address.isnot(None),
              func.lower(Candidates.interview_address).contains(func.lower(interview_address_filter))
              )
          else:
              query = query.filter(Candidates.interview_address.is_(None))


        # Apply score filter (puntucion)
        if score_filter:
          try:
            score_parts = score_filter.split("-")
            if len(score_parts) == 2:
              min_score = int(score_parts[0])
              max_score = int(score_parts[1])
              query = query.filter(
              Candidates.grade.isnot(None),
              Candidates.grade >= min_score,
              Candidates.grade <= max_score
              )
          except Exception:
            pass  # Ignore invalid score filter

        # Order by relevance if search query is present, otherwise by creation date
        if search_query:
          # Order by highest similarity across all searchable fields
          query = query.order_by(
            func.greatest(
              func.similarity(Candidates.name, search_query),
              func.similarity(Candidates.phone, search_query),
              func.coalesce(func.similarity(Roles.role_name, search_query), 0)
            ).desc(),
            Candidates.created_at.desc()
          )
        else:
          query = query.order_by(Candidates.created_at.desc())


        # Get total count before pagination
        total_count = query.count()
        # Apply pagination
        offset = (page - 1) * per_page
        paginated_results = query.offset(offset).limit(per_page).all()

        # Format candidates
        candidates = [
          self._format_candidate_data(candidate, role_name) 
          for candidate, role_name in paginated_results
        ]

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        # Tabs (taps) summary using candidate_funnel_logs
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        base_query = db.session.query(Candidates).filter(Candidates.company_id == self.company_id)
        
        # Get funnel state counts from logs
        funnel_logs_query = db.session.query(
            CandidateFunnelLog.new_funnel_state,
            func.count(func.distinct(CandidateFunnelLog.candidate_id)).label('count')
        ).join(
            Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
        ).filter(
            Candidates.company_id == self.company_id
        ).group_by(CandidateFunnelLog.new_funnel_state).all()
        
        funnel_counts = {state: count for state, count in funnel_logs_query}
        
        tabs = {
          "upcoming_interviews": base_query.filter(
          Candidates.interview_date_time.isnot(None),
          func.date(Candidates.interview_date_time) >= today.date()
          ).count(),
          "completed_interviews": base_query.filter(
          Candidates.interview_date_time.isnot(None),
          func.date(Candidates.interview_date_time) < today.date()
          ).count(),
          "hired": funnel_counts.get('hired', 0),
          "rejected": funnel_counts.get('rejected', 0),
          "screening_in_progress": funnel_counts.get('screening_in_progress', 0),
          "total_evaluated": base_query.count(),
          "interview_cited": base_query.filter(Candidates.interview_date_time.isnot(None)).count(),
          "missed_interviews": funnel_counts.get('missed_interview', 0),
        }

        return {
          "candidates": candidates,
          "pagination": {
          "current_page": page,
          "per_page": per_page,
          "total_count": total_count,
          "total_pages": total_pages,
          "has_next": has_next,
          "has_prev": has_prev,
          "next_page": page + 1 if has_next else None,
          "prev_page": page - 1 if has_prev else None
          },
          "filters": {
          "search_query": search_query,
          "role_filter": role_filter,
          "funnel_state_filter": funnel_state_filter,
          "interview_date_filter": interview_date_filter,
          "score_filter": score_filter,
          "interview_date_exact": interview_date_exact,
          "interview_address_filter": interview_address_filter,
          "reject_phase_filter": reject_phase_filter,
          },
          "tabs": tabs
        }

      except exc.SQLAlchemyError as e:
        logger.error(f"Database error when fetching candidates: {str(e)}")
        raise RuntimeError("Error retrieving candidates from database")
      
      
    def get_new_candidates_count(self, since: Optional[datetime] = None) -> int:
      """
      Get the count of new candidates for the company.
      Args:
        since: Optional datetime to count candidates created after this date. Defaults to today.
      Returns:
        Integer count of new candidates.
      """
      try:
        if since is None:
          since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = db.session.query(func.count(Candidates.candidate_id)).filter(
          Candidates.company_id == self.company_id,
          Candidates.created_at >= since
        )
        count = query.scalar()
        return count or 0
      except exc.SQLAlchemyError as e:
        logger.error(f"Database error when counting new candidates: {str(e)}")
        return 0
      
    def get_candidates_statistics(self) -> Dict[str, any]:
      """
      Returns statistics for candidates using efficient DB queries based on candidate_funnel_logs.
      """
      try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Base query for this company's candidates
        base_candidates_query = db.session.query(Candidates).filter(Candidates.company_id == self.company_id)

        # Total evaluated - count all candidates for this company
        total_evaluated = base_candidates_query.count()

        # Today new candidates
        today_new_candidates = base_candidates_query.filter(Candidates.created_at >= today).count()

        # Count candidates who have ever been in each funnel state using candidate_funnel_logs
        # Get distinct candidate_ids for each funnel state from the logs
        funnel_logs_query = db.session.query(
            CandidateFunnelLog.new_funnel_state,
            func.count(func.distinct(CandidateFunnelLog.candidate_id)).label('count')
        ).join(
            Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
        ).filter(
            Candidates.company_id == self.company_id
        ).group_by(CandidateFunnelLog.new_funnel_state).all()

        # Create a dictionary of funnel state counts
        funnel_counts = {state: count for state, count in funnel_logs_query}

        phone_interview_cited = funnel_counts.get('phone_interview_cited', 0)
        phone_interview = funnel_counts.get('phone_interview', 0)
        phone_interview_demo = funnel_counts.get('phone_interview_demo', 0)
        phone_interview_passed = funnel_counts.get('phone_interview_passed', 0)

        # Get counts for each state
        # For hired, we need to get candidates who had hired at some point in new_funnel_state
        # Use a subquery with window function to get the latest state per candidate
        hired = (
            db.session.query(func.count(func.distinct(CandidateFunnelLog.candidate_id)))
            .join(Candidates, Candidates.candidate_id == CandidateFunnelLog.candidate_id)
            .filter(
                Candidates.company_id == self.company_id,
                CandidateFunnelLog.new_funnel_state == 'hired',
            )
            .scalar()
        ) or 0

        missed_interviews = funnel_counts.get('missed_interview', 0)
        screening_progress = funnel_counts.get('screening_in_progress', 0)
        
        # For rejected, we need to count distinct candidates who have ever been rejected
        rejected_candidates = db.session.query(
            func.count(func.distinct(CandidateFunnelLog.candidate_id))
        ).join(
            Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
        ).filter(
            Candidates.company_id == self.company_id,
            CandidateFunnelLog.new_funnel_state == 'rejected'
        ).scalar() or 0
        
        rejected_total = rejected_candidates

        abscence_first_day = base_candidates_query.filter(
            Candidates.rejected_reason == "abscense_first_day"
        ).count() or 0

        # For rejection reasons, we still need to use the current candidates table
        # since rejection reasons are stored there
        rejected_pre_screening = base_candidates_query.filter(
            Candidates.rejected_reason == "screening"
        ).count()

        rejected_post_screening = base_candidates_query.filter(
            Candidates.rejected_reason != "screening",
            Candidates.rejected_reason != "abscence"
        ).count()

        # Interview-related calculations
        # Candidates who have ever been scheduled for interview (reached scheduled_interview state)
        interview_scheduled_candidates = db.session.query(
            func.count(func.distinct(CandidateFunnelLog.candidate_id))
        ).join(
            Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
        ).filter(
            Candidates.company_id == self.company_id,
            CandidateFunnelLog.new_funnel_state == 'scheduled_interview'
        ).scalar() or 0

        # For upcoming and completed interviews, we need to check actual interview dates
        # Upcoming interviews: have interview_date_time >= today
        upcoming_interviews = base_candidates_query.filter(
          Candidates.interview_date_time.isnot(None),
          func.date(Candidates.interview_date_time) >= today.date()
        ).count()

        # Completed interviews: have interview_date_time < today 
        completed_interviews = base_candidates_query.filter(
          Candidates.interview_date_time.isnot(None),
          func.date(Candidates.interview_date_time) < today.date()
        ).count()

        # Interview cited = candidates with any interview date set
        interview_cited = base_candidates_query.filter(Candidates.interview_date_time.isnot(None)).count()

        # Hiring rate: hired / interview_cited
        hiring_rate = (hired / interview_cited * 100) if interview_cited else 0

        # Conversion rate: interview_cited / total_evaluated
        conversion_rate = (interview_cited / total_evaluated * 100) if total_evaluated else 0

        # Ingresados: candidates who have been hired or onboarding (in funnel logs) AND have no rejected_reason
        ingresados = db.session.query(
            func.count(func.distinct(CandidateFunnelLog.candidate_id))
        ).join(
            Candidates, CandidateFunnelLog.candidate_id == Candidates.candidate_id
        ).filter(
            Candidates.company_id == self.company_id,
            CandidateFunnelLog.new_funnel_state.in_(['hired', 'onboarding']),
            Candidates.funnel_state.in_(['hired', 'onboarding', 'expired']),
            Candidates.rejected_reason.is_(None)
        ).scalar() or 0

        # Entrevistados: candidates who actually had interviews (interview_cited - missed_interviews) 
        entrevistados = hired + rejected_post_screening

        return {
          "upcoming_interviews": upcoming_interviews,
          "completed_interviews": completed_interviews,
          "missed_interviews": missed_interviews,
          "hired": hired,
          "rejected_total": rejected_total,
          "rejected_pre_screening": rejected_pre_screening,
          "rejected_post_screening": rejected_post_screening,
          "screening_in_progress": screening_progress,
          "today_new_candidates": today_new_candidates,
          "total_evaluated": total_evaluated,
          "interview_cited": interview_cited,
          "entrevistados": entrevistados,
          "hiring_rate": f"{hiring_rate:.2f}%",
          "conversion_rate": f"{conversion_rate:.2f}%",
          "ingresados": ingresados,

          "phone_interview_cited": phone_interview_cited,
          "phone_interview": phone_interview,
          "phone_interview_demo": phone_interview_demo,
          "phone_interview_passed": phone_interview_passed,
        }
      except Exception as e:
        logger.error(f"Error calculating candidate statistics: {str(e)}")
        return {}


    def _get_candidate_media_urls(self, candidate_id: int) -> List[Dict]:
        """Get all media URLs for a candidate"""
        try:
            media_records = db.session.query(CandidateMedia).filter_by(
                candidate_id=candidate_id
            ).order_by(CandidateMedia.upload_timestamp.desc()).all()
            
            media_urls = []
            for media in media_records:
                media_info = {
                    "media_id": media.media_id,
                    "s3_url": media.s3_url,
                    "file_name": media.file_name,
                    "mime_type": media.mime_type,
                    "file_size": media.file_size,
                    "upload_timestamp": media.upload_timestamp.isoformat() if media.upload_timestamp else None,
                    "question_id": media.question_id
                }
                media_urls.append(media_info)
            
            return media_urls
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching candidate media: {str(e)}")
            return []
    
    def _get_previous_funnel_state(self, candidate_id: int, current_state: Optional[str]) -> Optional[str]:
        """Get the previous funnel state from the most recent funnel log entry"""
        try:
            # Get the most recent funnel log where new_funnel_state equals the current state
            log_entry = db.session.query(CandidateFunnelLog).filter(
                CandidateFunnelLog.candidate_id == candidate_id,
                CandidateFunnelLog.new_funnel_state == current_state
            ).order_by(CandidateFunnelLog.changed_at.desc()).first()
            
            if log_entry and log_entry.previous_funnel_state:
                return log_entry.previous_funnel_state
            
            return None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching previous funnel state for candidate {candidate_id}: {str(e)}")
            return None
    
    def get_candidate_by_id(self, candidate_id: int) -> Optional[Dict]:
        """Get a specific candidate by ID with all related data including media"""
        try:
            candidate_data = db.session.query(Candidates, Roles.role_name).outerjoin(
                Roles, Candidates.role_id == Roles.role_id
            ).filter(
                Candidates.candidate_id == candidate_id,
                Candidates.company_id == self.company_id
            ).first()
            
            if not candidate_data:
                return None
                
            candidate, role_name = candidate_data
            return self._format_candidate_data(candidate, role_name)
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching candidate {candidate_id}: {str(e)}")
            return None

    def get_candidate_document_verification(self, candidate_id: int) -> Optional[Dict]:
        """Get document verification status for a candidate (only for group_id = 1)"""
        try:
            # First check if the candidate belongs to a company with group_id = 1
            candidate = db.session.query(Candidates).filter_by(
                candidate_id=candidate_id,
                company_id=self.company_id
            ).first()
            
            if not candidate or candidate.company_group_id != 1:
                return None
            
            # Get all verification documents for this candidate
            media_records = db.session.query(CandidateMedia).filter(
                CandidateMedia.candidate_id == candidate_id,
                CandidateMedia.media_subtype.in_(['RFC', 'INE', 'CURP', 'NSS'])
            ).order_by(CandidateMedia.media_subtype, CandidateMedia.upload_timestamp).all()
            
            # Process and categorize the documents
            documents = {
                'RFC': None,
                'INE': [],
                'CURP': None,
                'NSS': None
            }
            
            for media in media_records:
                doc_info = {
                    'media_id': media.media_id,
                    'media_subtype': media.media_subtype,
                    'verified': media.verified,
                    'upload_timestamp': media.upload_timestamp.isoformat() if media.upload_timestamp else None,
                    'verification_result': media.verification_result,
                    's3_url': media.s3_url,
                    'file_name': media.file_name,
                    'string_submission': media.string_submission,
                    'media_type': media.media_type
                }
                
                # Determine verification status
                if media.media_subtype == 'NSS':
                    # NSS has special logic for pending status
                    if not media.verified and media.verification_result and isinstance(media.verification_result, dict):
                        verification_id = media.verification_result.get('verificationId')
                        if verification_id:
                            doc_info['status'] = 'pending'
                            doc_info['status_message'] = 'Verificación en proceso'
                        else:
                            doc_info['status'] = 'rejected'
                            doc_info['status_message'] = 'Verificación fallida'
                    elif media.verified:
                        doc_info['status'] = 'verified'
                        doc_info['status_message'] = 'Verificado'
                    else:
                        doc_info['status'] = 'rejected'
                        doc_info['status_message'] = 'Verificación fallida'
                else:
                    # RFC, INE, CURP standard logic
                    if media.verified:
                        doc_info['status'] = 'verified'
                        doc_info['status_message'] = 'Verificado'
                    else:
                        doc_info['status'] = 'rejected'
                        doc_info['status_message'] = 'Verificación fallida'
                # 🔴 Add warnings if rejected (applies to all media types)
                if doc_info['status'] == 'rejected' and media.verification_result:
                    try:
                        if isinstance(media.verification_result, dict):
                            warnings = media.verification_result.get('warnings', [])
                            if warnings:
                                doc_info['warnings'] = " | ".join(w.get("message") for w in warnings if "message" in w)
                    except Exception as e:
                        logger.warning(f"Failed to extract warnings for media_id {media.media_id}: {str(e)}")
                                
                # Categorize by document type
                if media.media_subtype == 'INE':
                    documents['INE'].append(doc_info)
                else:
                    documents[media.media_subtype] = doc_info
            
            # Calculate overall verification status
            overall_status = self._calculate_overall_verification_status(documents)
            
            return {
                'candidate_id': candidate_id,
                'group_id': candidate.company_group_id,
                'documents': documents,
                'overall_status': overall_status
            }
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching document verification for candidate {candidate_id}: {str(e)}")
            return None
    
    def _calculate_overall_verification_status(self, documents: Dict) -> Dict:
        """Calculate overall verification status based on individual document statuses"""
        # Count statuses
        verified_count = 0
        pending_count = 0
        rejected_count = 0
        total_required = 4  # RFC, INE (2 images), CURP, NSS
        
        # RFC status
        if documents['RFC']:
            if documents['RFC']['status'] == 'verified':
                verified_count += 1
            elif documents['RFC']['status'] == 'pending':
                pending_count += 1
            else:
                rejected_count += 1
        else:
            rejected_count += 1
        
        # INE status (2 images required)
        if len(documents['INE']) >= 2:
            ine_verified = all(doc['status'] == 'verified' for doc in documents['INE'][:2])
            if ine_verified:
                verified_count += 1
            else:
                rejected_count += 1
        else:
            rejected_count += 1
        
        # CURP status
        if documents['CURP']:
            if documents['CURP']['status'] == 'verified':
                verified_count += 1
            elif documents['CURP']['status'] == 'pending':
                pending_count += 1
            else:
                rejected_count += 1
        else:
            rejected_count += 1
        
        # NSS status (special handling for async nature)
        if documents['NSS']:
            if documents['NSS']['status'] == 'verified':
                verified_count += 1
            elif documents['NSS']['status'] == 'pending':
                pending_count += 1
            else:
                # NSS rejection doesn't fail the overall process
                pass
        else:
            # No NSS submission doesn't fail the overall process
            pass
        
        # Determine overall status
        # For now, we consider the process successful if RFC, INE, and CURP are verified
        # NSS is tracked but doesn't affect the overall status due to its async nature
        critical_verified = (
            documents['RFC'] and documents['RFC']['status'] == 'verified' and
            len(documents['INE']) >= 2 and all(doc['status'] == 'verified' for doc in documents['INE'][:2]) and
            documents['CURP'] and documents['CURP']['status'] == 'verified'
        )
        
        if critical_verified:
            overall_status = 'verified'
            status_message = 'Documentos verificados exitosamente'
        elif pending_count > 0:
            overall_status = 'pending'
            status_message = 'Verificación en proceso'
        else:
            overall_status = 'rejected'
            status_message = 'Verificación fallida'
        
        return {
            'status': overall_status,
            'message': status_message,
            'verified_count': verified_count,
            'pending_count': pending_count,
            'rejected_count': rejected_count,
            'total_required': total_required
        }

    def get_interview_candidates_for_export(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Return list of candidates who have reached scheduled_interview with optional interview_date_time range.

        Includes all candidate columns except: candidate_id, company_id, start_date, end_flow_rejected.
        Replaces role_id with role name and maps eligible_roles to role names.
        """
        try:
            # Build roles map for this company for quick lookup
            roles_rows = db.session.query(Roles.role_id, Roles.role_name).filter(
                Roles.company_id == self.company_id
            ).all()
            role_id_to_name = {rid: rname for rid, rname in roles_rows}

            # Base query: candidates who have a funnel log with scheduled_interview
            query = (
                db.session.query(Candidates, Roles.role_name)
                .outerjoin(Roles, Candidates.role_id == Roles.role_id)
                .join(CandidateFunnelLog, CandidateFunnelLog.candidate_id == Candidates.candidate_id)
                .filter(
                    Candidates.company_id == self.company_id,
                    CandidateFunnelLog.new_funnel_state == 'scheduled_interview',
                )
            )

            # Apply interview date range filters
            if start_date:
                query = query.filter(Candidates.interview_date_time.isnot(None))
                query = query.filter(Candidates.interview_date_time >= start_date)
            if end_date:
                query = query.filter(Candidates.interview_date_time.isnot(None))
                query = query.filter(Candidates.interview_date_time <= end_date)

            query = query.order_by(Candidates.interview_date_time.desc())

            results = query.all()

            # Deduplicate candidates in case of multiple logs
            seen_ids = set()
            rows: List[Dict] = []

            for candidate, role_name in results:
                if candidate.candidate_id in seen_ids:
                    continue
                seen_ids.add(candidate.candidate_id)

                # Map eligible_roles JSON to role names if possible
                eligible_roles_names: str = ""
                try:
                    names: List[str] = []
                    er = candidate.eligible_roles
                    if isinstance(er, list):
                        for item in er:
                            if isinstance(item, int):
                                name = role_id_to_name.get(item)
                                if name:
                                    names.append(name)
                            elif isinstance(item, dict):
                                rid = item.get('role_id') or item.get('id')
                                if isinstance(rid, int):
                                    name = role_id_to_name.get(rid)
                                    if name:
                                        names.append(name)
                    elif isinstance(er, dict):
                        # keys could be role ids
                        for key in er.keys():
                            try:
                                rid = int(key)
                                name = role_id_to_name.get(rid)
                                if name:
                                    names.append(name)
                            except Exception:
                                continue
                    eligible_roles_names = ", ".join(sorted(set(names))) if names else ""
                except Exception:
                    eligible_roles_names = ""

                row: Dict = {
                    # Exclude candidate_id, company_id, start_date, end_flow_rejected
                    "phone": candidate.phone,
                    "name": candidate.name,
                    "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                    "interview_date_time": candidate.interview_date_time.isoformat() if candidate.interview_date_time else None,
                    "funnel_state": candidate.funnel_state,
                    "grade": candidate.grade,
                    "role": role_name or (role_id_to_name.get(candidate.role_id) if candidate.role_id else None),
                    "travel_time_minutes": candidate.travel_time_minutes,
                    "age": candidate.age,
                    "gender": candidate.gender,
                    "interview_reminder_sent": candidate.interview_reminder_sent,
                    "application_reminder_sent": candidate.application_reminder_sent,
                    "interview_address": candidate.interview_address,
                    "interview_map_link": candidate.interview_map_link,
                    "eligible_roles": eligible_roles_names,
                    "reschedule_sent": candidate.reschedule_sent,
                    "rejected_reason": candidate.rejected_reason,
                    "screening_rejected_reason": candidate.screening_rejected_reason,
                    "education_level": candidate.education_level,
                    "interview_confirmed": candidate.interview_confirmed,
                    "source": candidate.source,
                    "worked_here": candidate.worked_here,
                }

                rows.append(row)

            return rows
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when exporting interview candidates: {str(e)}")
            raise RuntimeError("Error retrieving candidates for export from database")
