from baltra_sdk.legacy.dashboards_folder.models import (
    ScreeningMessages, Candidates, 
    ScreeningQuestions, QuestionSets, 
    ScreeningAnswers, Roles, 
    CompaniesScreening, CandidateFunnelLog, CompanyGroups, db, Locations
)
import logging
from datetime import datetime
import json
from flask import current_app

"""
candidate_data_fetcher.py
 Purpose: Manage candidate retrieval/creation, thread handling, and question tracking for screening process.
 This class abstracts logic needed to initialize conversation context with a candidate.
"""

class CandidateDataFetcher:
    """
    Fetches or creates candidate data, initializes thread, and determines current and next screening questions.
    """

    def __init__(self, wa_id_user, client, wa_id_system):
        # Constructor: Initializes the CandidateDataFetcher with wa_id and OpenAI client
        self.wa_id_user = wa_id_user
        self.wa_id_system = wa_id_system
        self.client = client
        self.candidate, self.first_question_flag = self._get_or_create_candidate()
        self.latest_message = self._get_latest_message()
        self.thread_id = self._get_thread_id()
        self.set_id, self.question_id = self._get_set_and_question_id()
        

    def _get_or_create_candidate(self):
        logging.info(f'Get or create candidate for wa_id {self.wa_id_user} and system_wa_id {self.wa_id_system}')
        # Step 0: Check if wa_id_system belongs to a company group
        company_group = db.session.query(CompanyGroups).filter_by(wa_id=self.wa_id_system).first()
        # Step 1: Check if candidate exists for this group
        candidate = None
        if company_group:
            candidate = (
                db.session.query(Candidates)
                .filter_by(phone=self.wa_id_user, company_group_id=company_group.group_id)
                .order_by(Candidates.created_at.desc())
                .first()
            )

            if not candidate:

                # Candidate does not exist yet at group level → create it
                try:
                    new_candidate = Candidates(
                        phone=self.wa_id_user,
                        company_group_id=company_group.group_id,
                        name="",
                        created_at=datetime.now(),
                        funnel_state="screening_in_progress"
                    )
                    db.session.add(new_candidate)
                    db.session.commit()
                    return new_candidate, True
                except Exception as e:
                    logging.error(f"Failed to create candidate for company group {company_group.group_id}: {e}")
                    db.session.rollback()
                    return None, False
        else:
            #if no company_group start by fetching company
            company = db.session.query(CompaniesScreening).filter_by(wa_id=self.wa_id_system).first()
            if not company:
                logging.warning(f"No company found for wa_id_system: {self.wa_id_system}")
                return None, False
            # Fetches candidate by phone and company_id, or creates a new one if not found
            candidate = (
                db.session.query(Candidates)
                .filter_by(phone=self.wa_id_user, company_id =company.company_id)
                .order_by(Candidates.created_at.desc())
                .first()
                )
            
        if candidate:
            logging.info(f"Candidate found: ID {candidate.candidate_id}")
            
            # Get latest message for candidate to determine if a new candidate should be created
            latest_message = (
                db.session.query(ScreeningMessages)
                .filter_by(candidate_id=candidate.candidate_id)
                .order_by(ScreeningMessages.time_stamp.desc())
                .first()
            )
            
            if latest_message and latest_message.time_stamp and (datetime.now() - latest_message.time_stamp).days > current_app.config["SCREENING_EXPIRATION_DAYS"]:
                # Log funnel state change manually before marking expired
                previous_state = candidate.funnel_state or ""
                if previous_state != "expired":
                    try:
                        log_entry = CandidateFunnelLog(
                            candidate_id=candidate.candidate_id,
                            previous_funnel_state=previous_state,
                            new_funnel_state="expired",
                            changed_at=datetime.now()
                        )
                        db.session.add(log_entry)
                        db.session.commit()
                        logging.info(f"Logged funnel state change for candidate {candidate.candidate_id}: {previous_state} -> expired")
                    except Exception as e:
                        logging.error(f"Failed to log funnel state change for candidate {candidate.candidate_id}: {e}")
                        db.session.rollback()
                # Mark old candidate as expired
                candidate.funnel_state = "expired"
                db.session.commit()
                logging.info(f"Candidate {candidate.candidate_id} marked as expired after {current_app.config['SCREENING_EXPIRATION_DAYS']} days.")
                # Create a new candidate
                try:
                    new_candidate = Candidates(
                        phone=self.wa_id_user,
                        company_id=company.company_id,
                        name="",
                        created_at=datetime.now(),
                        funnel_state="screening_in_progress"
                    )
                    db.session.add(new_candidate)
                    db.session.commit()
                    logging.info(f"New candidate created: ID {new_candidate.candidate_id}")
                    
                    return new_candidate, True
                
                except Exception as e:
                    logging.error(f"Error creating new candidate after expiration: {e}")
                    db.session.rollback()
                    return None, False
                
            return candidate, False

        try:
            # Determine company_id from CompaniesScreening using self.wa_id_system

            new_candidate = Candidates(
                phone=self.wa_id_user,
                company_id=company.company_id,
                name="",
                created_at=datetime.now(),
                funnel_state = "screening_in_progress"
            )
            db.session.add(new_candidate)
            db.session.commit()
            first_question_flag = True
            logging.info(f"Created new candidate with wa_id: {self.wa_id_user}")
            return new_candidate, first_question_flag
        except Exception as e:
            logging.error(f"Error creating new candidate: {e}")
            db.session.rollback()
            return None, False

    def _get_latest_message(self):
        # Retrieves the most recent message sent by the candidate
        if not self.candidate:
            logging.warning("No candidate available when fetching latest message.")
            return None
        return (
            db.session.query(ScreeningMessages)
            .filter_by(candidate_id=self.candidate.candidate_id)
            .order_by(ScreeningMessages.time_stamp.desc())
            .first()
        )

    def _get_thread_id(self):
        # Retrieves existing thread or creates a new one if needed
        if self.latest_message and self.latest_message.thread_id:
            logging.debug(f"Using existing thread ID: {self.latest_message.thread_id}")
            return self.latest_message.thread_id
        try:
            thread = self.client.beta.threads.create()
            logging.debug(f"New Thread Created: {thread.id}")
            return thread.id
        except Exception as e:
            logging.error(f"Error creating thread: {e}")
            return None

    def _get_set_and_question_id(self):
        # Determines current question set and question based on last message or new start
        if self.latest_message:
            return (
                self.latest_message.set_id or 1,
                self.latest_message.question_id or 1
            )
        if self.candidate.company_id:
            logging.info("No previous messages found, fetching first question from active set.")
            set_obj = (
                db.session.query(QuestionSets)
                .filter_by(company_id=self.candidate.company_id, is_active=True, general_set=True)
                .order_by(QuestionSets.created_at.desc())
                .first()
            )

            if not set_obj:
                logging.warning(f"No active question set found for company {self.candidate.company_id}")
                return 1, 1  # fallback

            logging.info(f"Active question set selected: set_id {set_obj.set_id}")
            first_question = (
                db.session.query(ScreeningQuestions)
                .filter_by(set_id=set_obj.set_id, position=1, is_active=True)
                .first()
            )
            if not first_question:
                logging.warning(f"No question with position=1 found in set {set_obj.set_id}")
                return set_obj.set_id, 1
        elif self.candidate.company_group_id:
            logging.info("Candidate belongs to a company group, fetching first question from active group set.")
            set_obj = (
                db.session.query(QuestionSets)
                .filter_by(group_id=self.candidate.company_group_id, is_active=True)
                .order_by(QuestionSets.created_at.desc())
                .first()
            )

            if not set_obj:
                logging.warning(f"No active group question set found for group {self.candidate.company_group_id}")
                return 1, 1  # fallback

            logging.info(f"Active group question set selected: set_id {set_obj.set_id}")
            first_question = (
                db.session.query(ScreeningQuestions)
                .filter_by(set_id=set_obj.set_id, position=1, is_active=True)
                .first()
            )

            if not first_question:
                logging.warning(f"No question with position=1 found in group set {set_obj.set_id}")
                return set_obj.set_id, 1

        return set_obj.set_id, first_question.question_id

    def _get_current_and_next_question(self):
        # Gets current and next question text based on question_id and position
        current = db.session.query(ScreeningQuestions).filter_by(
            question_id=self.question_id
        ).first()

        if not current:
            logging.warning(f"No question found with ID: {self.question_id}")
            return None, None, None, None, None, None, None, None

        next_q = db.session.query(ScreeningQuestions).filter_by(
            set_id=self.set_id,
            position=current.position + 1,
            is_active = True
        ).first()

        if next_q:
            logging.debug(f"Next question found: position {next_q.position}")
            return current.question, current.response_type, current.position, current.end_interview_answer, current.example_answer, next_q.question, next_q.response_type, next_q.question_id if next_q else None
    
        else:
            logging.info(f"No next question found after position {current.position} in set {self.set_id}")
            return current.question, current.response_type, current.position, current.end_interview_answer, current.example_answer,None, None, None
    
    def _get_company_context(self):
        """
        Gets company context based on candidate's company_id.
        If no company_id, falls back to company_groups info.
        """
        # Try company first
        if self.candidate.company_id:
            company = db.session.query(CompaniesScreening).filter_by(company_id=self.candidate.company_id).first()
            if company:
                return (
                    company.name,
                    company.description,
                    company.address,
                    company.benefits,
                    company.general_faq,
                    company.classifier_assistant_id,
                    company.general_purpose_assistant_id,
                    company.maps_link_json or {},
                    company.interview_address_json or {},
                    company.interview_days,
                    company.interview_hours,
                    company.hr_contact
                )

        # Fallback to company group
        if self.candidate.company_group_id:
            group = db.session.query(CompanyGroups).filter_by(group_id=self.candidate.company_group_id).first()
            if group:
                return (
                    group.name,
                    group.description,
                    None,   # address not available at group level
                    None,   # benefits
                    None,   # general_faq
                    "asst_iBUlpF7FISkh3oY8Pr3bmVUb",   # classifier_assistant_id
                    "asst_drleBzh2ufZ79J7MHeocfp5X",   # general_purpose_assistant_id
                    {},     # maps_link_json
                    {},     # interview_address_json
                    None,   # interview_days
                    None,   # interview_hours
                    None    # hr_contact
                )

        # Default empty values
        return "", "", "", "", "", "", "", {}, {}, None, None, None
    
    def _get_role_context(self):
        # Gets role context for a specific role if role_id is defined, else for all roles in the company
        if self.candidate.role_id:
            role = db.session.query(Roles).filter_by(role_id=self.candidate.role_id).first()
            if role:
                role_info_str = str(role.role_info) if role.role_info else "Sin información adicional"
                return f"- {role.role_name}: {role_info_str}"
            else:
                return "No se encontró información del rol asignado"
        else:
            roles = db.session.query(Roles).filter_by(company_id=self.candidate.company_id).all()
            if roles:
                role_descriptions = []
                for role in roles:
                    role_info_str = str(role.role_info) if role.role_info else "Sin información adicional"
                    role_descriptions.append(f"- {role.role_name}: {role_info_str}")
                return "El candidato aún no ha seleccionado un rol. A continuación se muestra información de todos los roles disponibles en la empresa:\n".join(role_descriptions)
            return "No se encontraron roles para esta empresa"

    def _get_next_set_data(self):
        """
        Determines the role-specific question set and its first question details.
        Returns a tuple:
        - role_set_id
        - next_set_first_question
        - next_set_first_question_id
        - next_set_first_question_type
        - role (object or None)
        """
        role_set_id = None 
        next_set_first_question = None
        next_set_first_question_id = None
        next_set_first_question_type = None
        role = None

        # --- bLOCK TO MANAGE SWITCHING FROM company_group set to company set ---
        current_set_obj = db.session.query(QuestionSets).filter_by(set_id=self.set_id).first()

        if current_set_obj and current_set_obj.group_id and not current_set_obj.company_id and self.candidate.company_id:
            logging.info(f"[CandidateDataFetcher] Candidate finished company_group set {self.set_id}, assigning company general set as next set.")

            general_set_obj = (
                db.session.query(QuestionSets)
                .filter_by(company_id=self.candidate.company_id, general_set=True)
                .first()
            )

            if general_set_obj:
                first_question = (
                    db.session.query(ScreeningQuestions)
                    .filter_by(set_id=general_set_obj.set_id, position=1, is_active=True)
                    .first()
                )

                return (
                    first_question.set_id if first_question else None,
                    first_question.question if first_question else None,
                    first_question.question_id if first_question else None,
                    first_question.response_type if first_question else None,
                    None  # role not yet
                )
        # --- END OF NEW CODE ---

        # check if current set pertains to a role, in that case do not generate a new set
        current_set = db.session.query(QuestionSets.general_set).filter_by(set_id=self.set_id).scalar()
        if current_set is False:
            logging.info(f"[CandidateDataFetcher] Current set_id {self.set_id} is NOT general. Skipping next set.")
            return (
            role_set_id,
            next_set_first_question,
            next_set_first_question_id,
            next_set_first_question_type,
            role,
            )

        if self.candidate.role_id:
            role = db.session.query(Roles).filter_by(role_id=self.candidate.role_id).first()
        else:
            # Fallback to default role by company
            role = (
                db.session.query(Roles)
                .filter_by(company_id=self.candidate.company_id, default_role=True)
                .first()
            )
        if role and role.set_id:
            role_set_id = role.set_id

            first_question = (
                db.session.query(ScreeningQuestions)
                .filter_by(set_id=role_set_id, position=1, is_active = True)
                .first()
            )

            if first_question:
                next_set_first_question = first_question.question
                next_set_first_question_id = first_question.question_id
                next_set_first_question_type = first_question.response_type

        return (
            role_set_id,
            next_set_first_question,
            next_set_first_question_id,
            next_set_first_question_type,
            role,
        )

    def _resolve_interview_location(self, company_address, maps_link_json):
        """
        Resolves interview location based on role-specific interview location or fallback.
        Priority:
        1. Role's location_id_interview (if set)
        2. Role's location_id (fallback)
        3. Company default address (final fallback)
        """
        role = None
        if self.candidate.role_id:
            role = db.session.query(Roles).filter_by(role_id=self.candidate.role_id).first()
            logging.info(f"[_resolve_interview_location] Candidate {self.candidate.candidate_id} has role_id={self.candidate.role_id}")
            
            if role:
                logging.info(f"[_resolve_interview_location] Role found: role_id={role.role_id}, role_name={role.role_name}, location_id={role.location_id}, location_id_interview={role.location_id_interview}")
            else:
                logging.warning(f"[_resolve_interview_location] No role found for role_id={self.candidate.role_id}")
        else:
            logging.info(f"[_resolve_interview_location] Candidate {self.candidate.candidate_id} has no role_id assigned")

        # Priority 1: Check for role-specific interview location
        if role and getattr(role, "location_id_interview", None):
            interview_loc_id = role.location_id_interview
            logging.info(f"[_resolve_interview_location] Using location_id_interview={interview_loc_id} for role {role.role_id}")
            
            loc = db.session.query(Locations).filter_by(location_id=interview_loc_id).first()
            if loc:
                logging.info(f"[_resolve_interview_location] ✅ Found interview location: location_id={loc.location_id}, address={loc.address}")
                return {
                    "location_id": loc.location_id,
                    "address": getattr(loc, "address", None),
                    "url": getattr(loc, "url", None),
                    "latitude": getattr(loc, "latitude", None),
                    "longitude": getattr(loc, "longitude", None),
                }
            else:
                logging.warning(f"[_resolve_interview_location] Location not found in DB for location_id_interview={interview_loc_id}")

        # Priority 2: Fallback to role's general location
        if role and getattr(role, "location_id", None):
            regular_loc_id = role.location_id
            logging.info(f"[_resolve_interview_location] Falling back to location_id={regular_loc_id} for role {role.role_id}")
            
            loc = db.session.query(Locations).filter_by(location_id=regular_loc_id).first()
            if loc:
                logging.info(f"[_resolve_interview_location] ✅ Found fallback location: location_id={loc.location_id}, address={loc.address}")
                return {
                    "location_id": loc.location_id,
                    "address": getattr(loc, "address", None),
                    "url": getattr(loc, "url", None),
                    "latitude": getattr(loc, "latitude", None),
                    "longitude": getattr(loc, "longitude", None),
                }
            else:
                logging.warning(f"[_resolve_interview_location] Location not found in DB for location_id={regular_loc_id}")

        # Priority 3: Final fallback to company default
        logging.info(f"[_resolve_interview_location] Using company default address: {company_address}")
        return {
            "location_id": None,
            "address": company_address,
            "url": (maps_link_json or {}).get("url") if isinstance(maps_link_json, dict) else None,
            "latitude": None,
            "longitude": None,
        }

    def get_data(self):
        # Public method to return structured context about the candidate and screening flow
        if not self.candidate or not self.thread_id:
            logging.warning("Missing candidate or thread ID during data fetch.")
            return None

        current_question, current_response_type, current_position, end_interview_answer, example_answer, next_question, next_question_response_type, next_question_id = self._get_current_and_next_question()

        role_set_id, next_set_first_question, next_set_first_question_id, next_set_first_question_type, role = self._get_next_set_data()

        company_name, company_description, company_address, company_benefits, company_general_faq, classifier_assistant_id, general_purpose_assistant_id, maps_link_json, interview_address_json, interview_days, interview_hours, hr_contact = self._get_company_context()

        interview_date_str = self.candidate.interview_date_time.strftime('%d/%m/%Y %I:%M %p') if self.candidate.interview_date_time else ""

        interview_location = self._resolve_interview_location(company_address, maps_link_json)
        dynamic_map_link = interview_location.get("url")
        final_interview_address = self.candidate.interview_address or interview_location.get("address")
        final_interview_map_link = self.candidate.interview_map_link or dynamic_map_link

        return {
            "wa_id": self.wa_id_user,
            "candidate_id": self.candidate.candidate_id,
            "first_name": self.candidate.name,
            "flow_state": self.candidate.flow_state,
            "first_question_flag": self.first_question_flag,
            "company_group_id": self.candidate.company_group_id,
            "company_id": self.candidate.company_id,
            "company_name": company_name,
            "thread_id": self.thread_id,
            "classifier_assistant_id": classifier_assistant_id,
            "general_purpose_assistant_id": general_purpose_assistant_id,
            "set_id": self.set_id,
            "next_set_id": role_set_id,
            "question_id": self.question_id,
            "current_question": current_question,
            "current_response_type": current_response_type,
            "current_position": current_position,
            "end_interview_answer": end_interview_answer,
            "example_answer":example_answer, 
            "next_question": next_question,
            "next_question_response_type": next_question_response_type,
            "next_question_id": next_question_id,
            "next_set_first_question": next_set_first_question,
            "next_set_first_question_id":next_set_first_question_id,
            "next_set_first_question_type": next_set_first_question_type,
            "company_context": json.dumps({
                "Descripción": company_description,
                "Ubicación_Vacante": company_address,
                "Beneficios": company_benefits,
                "Preguntas_Frecuentes": company_general_faq,
                "Dias_Entrevista": interview_days,
                "Horarios_Entrevista": interview_hours,
                "hr_contact": hr_contact if self.candidate.funnel_state == "scheduled_interview" else None 
            }, ensure_ascii=False),
            "role": self.candidate.role.role_name if self.candidate.role else None,
            "role_context": self._get_role_context(),
            "travel_time_minutes": getattr(self.candidate, "travel_time_minutes", None),
            "funnel_state": self.candidate.funnel_state,
            "end_flow_rejected": self.candidate.end_flow_rejected,
            "interview_date": interview_date_str,
            "interview_address": self.candidate.interview_address,
            "eligible_roles": self.candidate.eligible_roles or [],
            "maps_link_json": maps_link_json,
            "interview_address_json": interview_address_json,

            "interview_location": interview_location,
            "final_interview_address": final_interview_address,
            "final_interview_map_link": final_interview_map_link,
        }
