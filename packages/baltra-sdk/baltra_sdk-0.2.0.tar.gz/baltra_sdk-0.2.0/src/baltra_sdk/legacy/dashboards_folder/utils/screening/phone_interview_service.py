import logging
from sqlalchemy import exc, desc
from sqlalchemy.orm import joinedload
from baltra_sdk.legacy.dashboards_folder.models import (
    Candidates, Roles, db, PhoneInterviews, 
    CompaniesScreening, CandidateMedia, PhoneInterviewQuestions
)
from sqlalchemy import or_, func, and_
from flask import current_app
from typing import List, Dict, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class PhoneInterviewService:
    """Service for managing phone interview data with efficient queries and error handling"""
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
        self.company_id = company_id
    
    def get_questions(self, role_id: Optional[int] = None) -> List[Dict]:
        """Return active questions for company/role ordered by position. Fallback to role-agnostic questions."""
        try:
            query = db.session.query(PhoneInterviewQuestions).filter(
                PhoneInterviewQuestions.company_id == self.company_id,
                PhoneInterviewQuestions.is_active.is_(True)
            )
            if role_id is not None:
                role_specific = query.filter(PhoneInterviewQuestions.role_id == role_id).order_by(PhoneInterviewQuestions.position).all()
                if role_specific:
                    return [
                        {
                            'id': q.id,
                            'position': q.position,
                            'question': q.question_text,
                            'role_id': q.role_id
                        } for q in role_specific
                    ]
            # fallback to company-level questions (role_id is NULL)
            company_default = query.filter(PhoneInterviewQuestions.role_id.is_(None)).order_by(PhoneInterviewQuestions.position).all()
            print(f"[PhoneInterviewService] Company default questions: {[q.question_text for q in company_default if q.question_text]}")
            return [
                {
                    'id': q.id,
                    'position': q.position,
                    'question': q.question_text,
                    'role_id': q.role_id
                } for q in company_default
            ]
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching phone interview questions: {str(e)}")
            raise RuntimeError("Error retrieving phone interview questions from database")

    def upsert_questions(self, questions: List[Dict], role_id: Optional[int] = None) -> List[Dict]:
        """Replace current active questions (scope: company+role) with provided list."""
        try:
            # soft-delete current active questions in scope
            db.session.query(PhoneInterviewQuestions).filter(
                PhoneInterviewQuestions.company_id == self.company_id,
                (PhoneInterviewQuestions.role_id == role_id) if role_id is not None else PhoneInterviewQuestions.role_id.is_(None),
                PhoneInterviewQuestions.is_active.is_(True)
            ).update({PhoneInterviewQuestions.is_active: False}, synchronize_session=False)

            # insert new ones
            created = []
            # sort deterministically by provided position; fallback to stable index order
            ordered_questions: List[Dict] = []
            if isinstance(questions, list):
                try:
                    ordered_questions = sorted(questions, key=lambda x: (x or {}).get('position') or 0)
                except Exception:
                    ordered_questions = list(questions)
            for idx, q in enumerate(ordered_questions, start=1):
                obj = PhoneInterviewQuestions(
                    company_id=self.company_id,
                    role_id=role_id,
                    question_text=(q or {}).get('question') or (q or {}).get('question_text'),
                    position=(q or {}).get('position') or idx,
                    is_active=True
                )
                db.session.add(obj)
                created.append(obj)
            db.session.commit()

            return [
                {
                    'id': q.id,
                    'position': q.position,
                    'question': q.question_text,
                    'role_id': q.role_id
                } for q in created
            ]
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error upserting phone interview questions: {str(e)}")
            raise RuntimeError("Error upserting phone interview questions in database")

    def format_questions_for_agent(self, questions: List[Dict]) -> str:
        """Return a numbered Spanish script, one question per line/paragraph."""
        parts = []
        for i, q in enumerate(sorted(questions, key=lambda x: x['position']), start=1):
            parts.append(f"{i}. {q['question']}")
        return "\n\n".join(parts)
    
    def get_candidate_role_name_by_phone(self, phone_number: str) -> str:
        """Get candidate's role name based on phone number. Defaults to 'operador general' if no role found."""
        try:
            # Normalize phone number variants for better matching
            normalized_digits = ''.join(ch for ch in phone_number if ch.isdigit())
            variants = {phone_number, normalized_digits}
            if normalized_digits.startswith('52') and len(normalized_digits) > 10:
                variants.add(normalized_digits[-10:])
            if normalized_digits.startswith('1') and len(normalized_digits) > 10:
                variants.add(normalized_digits[-10:])
            
            # Query candidate and their role
            result = db.session.query(
                Candidates.candidate_id,
                Candidates.name,
                Roles.role_name
            ).outerjoin(
                Roles, Candidates.role_id == Roles.role_id
            ).filter(
                Candidates.company_id == self.company_id,
                Candidates.phone.in_(list(variants))
            ).first()
            
            if result:
                candidate_id, candidate_name, role_name = result
                logger.info(f"Found candidate {candidate_name} (ID: {candidate_id}) with role: {role_name or 'operador general'}")
                return role_name or 'operador general'
            else:
                logger.warning(f"No candidate found for phone: {phone_number}")
                return 'operador general'
                
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching candidate role by phone {phone_number}: {str(e)}")
            return 'operador general'
    
    def get_phone_interview_candidates(self, 
                                       page: int = 1, 
                                       per_page: int = 50, 
                                       search_query: str = None,
                                       call_status: str = None) -> Dict:
        """Retrieve candidates who have phone interviews with pagination and filters"""
        try:
            # Base query joining phone interviews with candidates and roles
            query = db.session.query(
                PhoneInterviews, 
                Candidates, 
                Roles.role_name
            ).join(
                Candidates, PhoneInterviews.candidate_id == Candidates.candidate_id
            ).outerjoin(
                Roles, Candidates.role_id == Roles.role_id
            ).filter(
                PhoneInterviews.company_id == self.company_id
            )
            
            # Apply call status filter
            if call_status and call_status != 'all':
                query = query.filter(PhoneInterviews.call_status == call_status)
            
            # Apply search filter
            if search_query:
                search_filter = or_(
                    Candidates.name.ilike(f"%{search_query}%"),
                    Candidates.phone.ilike(f"%{search_query}%"),
                    Roles.role_name.ilike(f"%{search_query}%")
                )
                query = query.filter(search_filter)
            
            # Order by interview date (most recent first)
            query = query.order_by(desc(PhoneInterviews.created_at))
            
            # Get total count for pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()
            
            # Format the data
            candidates = []
            for phone_interview, candidate, role_name in results:
                candidate_data = self._format_phone_interview_candidate(
                    phone_interview, candidate, role_name
                )
                candidates.append(candidate_data)
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                'candidates': candidates,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                },
                'filters': {
                    'search_query': search_query,
                    'call_status': call_status
                }
            }
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching phone interview candidates: {str(e)}")
            raise RuntimeError("Error retrieving phone interview candidates from database")
    
    def get_candidate_phone_interview(self, candidate_id: int) -> Optional[Dict]:
        """Get phone interview details for a specific candidate"""
        try:
            result = db.session.query(
                PhoneInterviews, 
                Candidates, 
                Roles.role_name
            ).join(
                Candidates, PhoneInterviews.candidate_id == Candidates.candidate_id
            ).outerjoin(
                Roles, Candidates.role_id == Roles.role_id
            ).filter(
                PhoneInterviews.candidate_id == candidate_id,
                PhoneInterviews.company_id == self.company_id
            ).first()
            
            if not result:
                return None
                
            phone_interview, candidate, role_name = result
            return self._format_phone_interview_candidate(
                phone_interview, candidate, role_name, include_transcript=True
            )
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching phone interview for candidate {candidate_id}: {str(e)}")
            raise RuntimeError("Error retrieving phone interview from database")
    
    def get_phone_interview_stats(self) -> Dict:
        """Get statistics for phone interviews"""
        try:
            stats = db.session.query(
                PhoneInterviews.call_status,
                func.count(PhoneInterviews.interview_id).label('count'),
                func.avg(PhoneInterviews.ai_score).label('avg_score')
            ).filter(
                PhoneInterviews.company_id == self.company_id
            ).group_by(PhoneInterviews.call_status).all()
            
            # Initialize default stats
            result = {
                'total_candidates': 0,
                'completed': 0,
                'failed': 0,
                'scheduled': 0,
                'missed': 0,
                'avg_score': 0,
                'recommended': 0,
                'not_recommended': 0
            }
            
            # Process stats
            for status, count, avg_score in stats:
                result[status] = count
                result['total_candidates'] += count
                if avg_score:
                    result['avg_score'] = round(avg_score)
            
            # Get recommendation stats
            rec_stats = db.session.query(
                PhoneInterviews.ai_recommendation,
                func.count(PhoneInterviews.interview_id).label('count')
            ).filter(
                PhoneInterviews.company_id == self.company_id,
                PhoneInterviews.call_status == 'completed'
            ).group_by(PhoneInterviews.ai_recommendation).all()
            
            for recommendation, count in rec_stats:
                if recommendation == 'recommended':
                    result['recommended'] = count
                elif recommendation == 'not_recommended':
                    result['not_recommended'] = count
            
            return result
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching phone interview stats: {str(e)}")
            raise RuntimeError("Error retrieving phone interview stats from database")
    
    def _format_phone_interview_candidate(self, 
                                          phone_interview: PhoneInterviews, 
                                          candidate: Candidates, 
                                          role_name: Optional[str],
                                          include_transcript: bool = False) -> Dict:
        """Format phone interview candidate data for frontend display"""
        
        # Get candidate media URLs
        media_urls = self._get_candidate_media_urls(candidate.candidate_id)
        
        # Format call duration
        duration_str = self._format_duration(phone_interview.call_duration)
        
        # Format recommendation for display
        recommendation_map = {
            'recommended': 'Recomendado',
            'not_recommended': 'No Recomendado',
            'pending_review': 'Pendiente'
        }
        
        # Format call status for display
        status_map = {
            'completed': 'Completada',
            'failed': 'Fallida',
            'scheduled': 'Programada',
            'missed': 'No Presentado'
        }
        
        result = {
            "id": candidate.candidate_id,
            "name": candidate.name or "Sin nombre",
            "role": role_name or "Sin rol asignado",
            "phone": candidate.phone,
            "interview_id": phone_interview.interview_id,
            "vapi_call_id": phone_interview.vapi_call_id,
            "call_status": phone_interview.call_status,
            "call_status_display": status_map.get(phone_interview.call_status, phone_interview.call_status),
            "call_duration": phone_interview.call_duration,
            "duration_display": duration_str,
            "started_at": phone_interview.started_at.isoformat() if phone_interview.started_at else None,
            "ended_at": phone_interview.ended_at.isoformat() if phone_interview.ended_at else None,
            "call_date": phone_interview.started_at.strftime("%d/%m/%Y") if phone_interview.started_at else "N/A",
            "call_time": phone_interview.started_at.strftime("%H:%M") if phone_interview.started_at else "N/A",
            "ai_score": phone_interview.ai_score or 0,
            "ai_recommendation": phone_interview.ai_recommendation,
            "recommendation_display": recommendation_map.get(phone_interview.ai_recommendation, "TBD"),
            "summary": phone_interview.summary,
            "created_at": phone_interview.created_at.isoformat(),
            "media_urls": media_urls,
            # Additional candidate info
            "age": candidate.age,
            "gender": candidate.gender,
            "education_level": candidate.education_level,
            "funnel_state": candidate.funnel_state
        }
        
        # Include transcript only when specifically requested (for detailed view)
        if include_transcript:
            result["transcript"] = phone_interview.transcript
        
        return result
    
    def _get_candidate_media_urls(self, candidate_id: int) -> List[Dict]:
        """Get media URLs for a candidate"""
        try:
            media_items = db.session.query(CandidateMedia).filter(
                CandidateMedia.candidate_id == candidate_id
            ).all()
            
            return [{
                "id": item.media_id,
                "url": item.media_url,
                "media_type": item.media_type,
                "uploaded_at": item.uploaded_at.isoformat() if item.uploaded_at else None
            } for item in media_items]
            
        except exc.SQLAlchemyError as e:
            logger.warning(f"Error fetching media for candidate {candidate_id}: {str(e)}")
            return []
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
        """Format call duration from seconds to human readable format"""
        if not duration_seconds:
            return "N/A"
        
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        
        if minutes > 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"0:{seconds:02d}"
    
    def store_phone_interview(self, interview_data: Dict) -> PhoneInterviews:
        """Upsert phone interview by vapi_call_id. Update status/timestamps/transcript on repeat webhooks."""
        try:
            existing: PhoneInterviews = db.session.query(PhoneInterviews).filter(
                PhoneInterviews.vapi_call_id == interview_data['vapi_call_id'],
                PhoneInterviews.company_id == self.company_id
            ).first()

            if existing:
                existing.candidate_id = interview_data.get('candidate_id', existing.candidate_id)
                incoming_status = interview_data.get('call_status')
                # Upgrade status to completed if incoming indicates completion
                if incoming_status in ('completed', 'ended'):
                    existing.call_status = 'completed'
                elif incoming_status:
                    existing.call_status = incoming_status
                if interview_data.get('call_duration') is not None:
                    existing.call_duration = interview_data.get('call_duration')
                if interview_data.get('started_at'):
                    existing.started_at = interview_data.get('started_at')
                if interview_data.get('ended_at'):
                    existing.ended_at = interview_data.get('ended_at')
                    # If we now have both timestamps but no duration, compute it
                    if existing.started_at and existing.ended_at and not existing.call_duration:
                        existing.call_duration = max(0, int((existing.ended_at - existing.started_at).total_seconds()))
                # Prefer incoming transcript/summary when present
                if interview_data.get('transcript'):
                    existing.transcript = interview_data.get('transcript')
                if interview_data.get('summary'):
                    existing.summary = interview_data.get('summary')
                if interview_data.get('ai_score') is not None:
                    existing.ai_score = interview_data.get('ai_score')
                if interview_data.get('ai_recommendation'):
                    existing.ai_recommendation = interview_data.get('ai_recommendation')

                # Short-term demo logic: if completed and no AI data, auto-fill recommended score
                if existing.call_status == 'completed':
                    if existing.ai_score is None:
                        existing.ai_score = random.randint(70, 89)
                    if not existing.ai_recommendation or existing.ai_recommendation == 'pending_review':
                        existing.ai_recommendation = 'recommended'
                db.session.commit()
                logger.info(f"Updated phone interview {existing.interview_id} for vapi_call_id {existing.vapi_call_id}")
                return existing

            phone_interview = PhoneInterviews(
                candidate_id=interview_data['candidate_id'],
                company_id=self.company_id,
                vapi_call_id=interview_data['vapi_call_id'],
                call_status=interview_data.get('call_status', 'completed'),
                call_duration=interview_data.get('call_duration'),
                started_at=interview_data.get('started_at'),
                ended_at=interview_data.get('ended_at'),
                transcript=interview_data.get('transcript'),
                summary=interview_data.get('summary'),
                ai_score=interview_data.get('ai_score'),
                ai_recommendation=interview_data.get('ai_recommendation')
            )

            # Short-term demo logic for inserts as well
            if phone_interview.call_status == 'completed':
                if phone_interview.ai_score is None:
                    phone_interview.ai_score = random.randint(70, 89)
                if not phone_interview.ai_recommendation or phone_interview.ai_recommendation == 'pending_review':
                    phone_interview.ai_recommendation = 'recommended'
            db.session.add(phone_interview)
            db.session.commit()
            logger.info(f"Stored phone interview for candidate {interview_data['candidate_id']}")
            return phone_interview

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error storing phone interview: {str(e)}")
            raise RuntimeError("Error storing phone interview in database")
