import random
from baltra_sdk.legacy.dashboards_folder.models import (
    ScreeningMessages, ScreeningAnswers, CandidateReferences,                                       
    Candidates, CompaniesScreening, ReferenceMessages, ResponseTiming, Roles, MessageTemplates,
    QuestionSets, ScreeningQuestions, ActiveOpenAIRun, CandidateFunnelLog, EligibilityEvaluationLog, 
    OnboardingResponses, db
)
from sqlalchemy.exc import NoResultFound, IntegrityError, SQLAlchemyError
from sqlalchemy import select, insert, Table
from datetime import datetime, timezone, timedelta, time
import logging
import json
from baltra_sdk.shared.mixpanel.metrics_screening import send_funnel_state_mixpanel
import heapq
from math import radians, sin, cos, atan2, sqrt
from typing import Optional, List, Dict, Iterable, Tuple
from .google_maps import LocationService


# sql_utils.py
# Purpose: Store screening messages and answers from candidates during the screening workflow.

def store_message(message_id, candidate_data, sent_by, message_body, whatsapp_msg_id):
    """
    Stores a screening message in the database.

    Parameters:
    - message_id (str): Custom message identifier
    - candidate_data (dict): Dictionary with keys: wa_id, company_id, candidate_id, set_id, question_id, answer_id, thread_id
    - sent_by (str): Who sent the message
    - message_body (str): Body of the message
    - whatsapp_msg_id (str): WhatsApp message ID

    Returns:
    - ScreeningMessages instance if successful, None otherwise.
    """
    logging.debug(f"Storing message for candidate {candidate_data.get('candidate_id')} with message_id {message_id}")
    try:
        message = ScreeningMessages(
            message_id=message_id,
            wa_id=candidate_data.get('wa_id'),
            company_id=candidate_data.get('company_id'),
            candidate_id=candidate_data.get('candidate_id'),
            thread_id=candidate_data.get('thread_id'),
            time_stamp=datetime.now(),
            sent_by=sent_by,
            message_body=message_body,
            conversation_type='screening',  # or change based on context
            whatsapp_msg_id=whatsapp_msg_id,
            set_id=candidate_data.get('set_id'),
            question_id=candidate_data.get('question_id'),
        )
        db.session.add(message)
        db.session.commit()
        logging.info(f"Message stored successfully for candidate {candidate_data.get('candidate_id')} with message_id {message_id}")
        return message
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error storing message for candidate {candidate_data.get('candidate_id')}: {e}")
        return None

def store_message_reference(message_id, candidate_data, sent_by, message_body, whatsapp_msg_id):
    """
    Stores a reference message in the database.

    Parameters:
    - message_id (str): Custom message identifier
    - candidate_data (dict): Dictionary with keys including:
        wa_id (str), reference_id (int), thread_id (str)
    - sent_by (str): Who sent the message (e.g., 'candidate', 'reference', 'assistant')
    - message_body (str): The content of the message
    - whatsapp_msg_id (str): The WhatsApp message ID

    Returns:
    - ReferenceMessages instance if successful, None otherwise.
    """
    logging.debug(f"Storing message for reference_id {candidate_data.get('reference_id')} with message_id {message_id}")
    try:
        message = ReferenceMessages(
            message_id=message_id,
            wa_id=candidate_data.get('wa_id'),
            reference_id=candidate_data.get('reference_id'),
            thread_id=candidate_data.get('thread_id'),
            time_stamp=datetime.now(),
            sent_by=sent_by,
            message_body=message_body,
            conversation_type='reference',  # specify conversation type
            whatsapp_msg_id=whatsapp_msg_id,
        )
        db.session.add(message)
        db.session.commit()
        logging.info(f"Message stored successfully for reference_id {candidate_data.get('reference_id')} with message_id {message_id}")
        return message
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error storing message for reference_id {candidate_data.get('reference_id')}: {e}")
        return None

def store_screening_answer(candidate_data, message_body, json_data: str = None, data_flag: str = None):
    """
    Stores or updates a screening answer from a candidate.

    Parameters:
    - candidate_data (dict): Includes candidate_id and question_id
    - message_body (str): The candidate's raw text answer

    Returns:
    - True if the operation succeeded, False otherwise.
    """
    candidate_id = candidate_data.get('candidate_id')
    question_id = candidate_data.get('question_id')
    position = candidate_data.get('current_position')
    set_id = candidate_data.get('set_id')
    logging.debug(f"Storing answer for candidate {candidate_id}, question {question_id}, position {position}, set_id {set_id}")
    
    try:
        # Check if the answer already exists
        existing_answer = db.session.query(ScreeningAnswers).filter_by(
            candidate_id=candidate_id,
            question_id=question_id
        ).first()

        if data_flag == "location":
            if json_data and "duration_minutes" in json_data:
                add_travel_time_minutes(candidate_data, json_data["duration_minutes"])
            else:
                logging.warning(f"Missing 'duration_minutes' in location json_data for candidate {candidate_id}: {json_data}")

        if data_flag == "nfm_reply":
            add_interview_date_time(candidate_data, message_body)
        
        if data_flag == "document_upload":
            logging.info(f"Storing document upload answer for candidate {candidate_id}, question {question_id}")

        if existing_answer:
            # Update existing answer
            existing_answer.answer_raw = message_body
            existing_answer.created_at = datetime.now()
            if json_data:
              existing_answer.answer_json = json_data
            logging.debug(f"Updated answer for candidate {candidate_id}, question {question_id}, position {position}, set_id {set_id}")
        else:
            # Insert new answer
            new_answer = ScreeningAnswers(
                candidate_id=candidate_id,
                question_id=question_id,
                answer_raw=message_body,
                created_at=datetime.now(),
                answer_json=json_data or None
            )
            db.session.add(new_answer)
            logging.info(f"Stored new answer for candidate {candidate_id}, question {question_id}, position {position}, set_id {set_id}")

        db.session.commit()
        return True

    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"Integrity error while storing answer for candidate {candidate_id}, question {question_id}: {e}")
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error while storing answer for candidate {candidate_id}, question {question_id}: {e}")
        return False
    
def store_reference_contact(candidate_data, reference_wa_id):
    """
    Stores or updates a reference contact from a candidate.

    Parameters:
    - candidate_data (dict): Includes candidate_id, set_id, and question_id
    - reference_wa_id (str): The reference's WhatsApp ID

    Returns:
    - True if the operation succeeded, False otherwise.
    """
    candidate_id = candidate_data.get('candidate_id')
    set_id = candidate_data.get('set_id')
    question_id = candidate_data.get('question_id')
    
    logging.debug(f"Storing reference contact for candidate {candidate_id}, question {question_id}")
    
    try:
        # Check if reference already exists
        existing_reference = db.session.query(CandidateReferences).filter_by(
            candidate_id=candidate_id,
            set_id=set_id,
            question_id=question_id
        ).first()
        
        if existing_reference:
            # Update existing reference
            existing_reference.reference_wa_id = reference_wa_id
            logging.debug(f"Updated reference contact for candidate {candidate_id}")
        else:
            # Create new reference
            new_reference = CandidateReferences(
                candidate_id=candidate_id,
                set_id=set_id,
                question_id=question_id,
                reference_wa_id=reference_wa_id
            )
            db.session.add(new_reference)
            logging.info(f"Stored new reference contact for candidate {candidate_id}")
        
        db.session.commit()
        return True
        
    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"Integrity error storing reference for candidate {candidate_id}: {e}")
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error storing reference for candidate {candidate_id}: {e}")
        return False
    
def get_company_location_info(candidate_data):
    company_id = candidate_data.get("company_id")
    if not company_id:
        return "unkown", "unkown"

    company = CompaniesScreening.query.filter_by(company_id=company_id).first()
    if company:
        # Safely access JSON fields with fallbacks
        maps_link_json = company.maps_link_json or {}
        interview_address_json = company.interview_address_json or {}
        
        # Get the correct values from the correct JSON objects
        map_link = maps_link_json.get("location_link_1", "No disponible")
        address = interview_address_json.get("location_1", "No disponible")
        
        return map_link, address

    return "unkown", "unknown"

def get_company_additional_info(company_id: int) -> Optional[str]:
    """Retrieves the additional_info field for a given company_id."""
    try:
        company = db.session.query(CompaniesScreening.additional_info).filter_by(company_id=company_id).one_or_none()
        if company:
            return company.additional_info
        return None
    except Exception as e:
        logging.error(f"Error fetching additional_info for company_id {company_id}: {e}")
        return None


def get_company_screening_data(company_id):
    company = CompaniesScreening.query.filter_by(company_id=company_id).first()
    if not company:
        return None
    return {
        "address": company.address,
        "unavailable_dates": company.interview_excluded_dates or [],
        "interview_days": company.interview_days or [],
        "interview_hours": company.interview_hours or [],
        "interview_address_json": company.interview_address_json or {},
        "maps_link_json": company.maps_link_json or {},
        "max_interviews_per_slot": company.max_interviews_per_slot
    }

def count_bookings_for_slot(company_id, date, hour):
    """
    Count existing bookings for a specific company, date, and hour.
    
    Args:
        company_id (int): The company ID
        date (str): Date in 'YYYY-MM-DD' format
        hour (str): Hour in 'HH:MM' format
    
    Returns:
        int: Number of candidates already scheduled for this slot
    """
    try:
        # Parse date and hour to create datetime range
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        hour_obj = datetime.strptime(hour, '%H:%M').time()
        target_datetime = datetime.combine(date_obj, hour_obj)
        target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        
        # Count candidates with interviews scheduled at this exact datetime
        count = db.session.query(Candidates).filter(
            Candidates.company_id == company_id,
            Candidates.interview_date_time == target_datetime,
            Candidates.funnel_state.in_(['scheduled_interview', 'screening_in_progress'])
        ).count()
        
        return count
    except Exception as err:
        logging.error(f"Error counting bookings for slot: {err}")
        return 0

def is_slot_available(company_id, date, hour, max_capacity):
    """
    Check if a time slot is still available based on capacity.
    
    Args:
        company_id (int): The company ID
        date (str): Date in 'YYYY-MM-DD' format
        hour (str): Hour in 'HH:MM' format
        max_capacity (int or None): Maximum candidates per slot, None means unlimited
    
    Returns:
        bool: True if slot is available, False otherwise
    """
    # If no capacity limit is set, slot is always available
    if max_capacity is None:
        return True
    
    current_bookings = count_bookings_for_slot(company_id, date, hour)
    return current_bookings < max_capacity

def get_available_hours_for_date(company_id, date, all_hours, max_capacity):
    """
    Filter interview hours to only include those with available capacity for a specific date.
    
    Args:
        company_id (int): The company ID
        date (str): Date in 'YYYY-MM-DD' format
        all_hours (list): List of all possible interview hours
        max_capacity (int or None): Maximum candidates per slot, None means unlimited
    
    Returns:
        list: Filtered list of available hours
    """
    if max_capacity is None:
        return all_hours
    
    available_hours = []
    for hour in all_hours:
        if is_slot_available(company_id, date, hour, max_capacity):
            available_hours.append(hour)
    
    return available_hours

def get_available_hours_for_date_range(company_id, start_date, end_date, all_hours, max_capacity, interview_days):
    """
    Filter interview hours to only include those with capacity on at least one date in the range.
    This is used for WhatsApp Flows where we send a single hours array for all dates.
    
    Args:
        company_id (int): The company ID
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        all_hours (list): List of all possible interview hours
        max_capacity (int or None): Maximum candidates per slot, None means unlimited
        interview_days (list): List of allowed weekday numbers (0=Monday, 6=Sunday)
    
    Returns:
        list: Filtered list of hours that have capacity on at least one valid date
    """
    if max_capacity is None:
        return all_hours
    
    # Parse dates
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Track which hours have capacity on at least one date
    hours_with_capacity = set()
    
    # Check each date in the range
    current_date = start
    while current_date <= end:
        # Check if this weekday is allowed for interviews
        weekday = current_date.weekday()  # 0=Monday, 6=Sunday
        if interview_days and weekday not in interview_days:
            current_date += timedelta(days=1)
            continue
        
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Check each hour for this date
        for hour in all_hours:
            if is_slot_available(company_id, date_str, hour, max_capacity):
                hours_with_capacity.add(hour)
        
        current_date += timedelta(days=1)
    
    # Return hours in original order, filtered to only those with capacity
    return [hour for hour in all_hours if hour in hours_with_capacity]

def _weekday_to_short_name(weekday_num):
    """Convert Python weekday number (0=Monday) to 3-letter format (Mon, Tue, etc.)"""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return days[weekday_num]

def get_available_dates_and_hours(company_id, start_date, end_date, all_hours, max_capacity, interview_days, unavailable_dates, max_days=4):
    """
    Get available dates and corresponding hour availability for the new calendar picker flow.
    Returns up to max_days dates with per-date hour availability.
    
    Args:
        company_id (int): The company ID
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        all_hours (list): List of all possible interview hours (e.g., ["09:00", "09:30"])
        max_capacity (int or None): Maximum candidates per slot, None means unlimited
        interview_days (list): List of allowed day names (e.g., ["Mon", "Tue", "Wed"])
        unavailable_dates (list): List of excluded dates in 'YYYY-MM-DD' format
        max_days (int): Maximum number of days to return (default 4 for WhatsApp Flow limit)
    
    Returns:
        list: List of dicts with 'date' and 'hours' (with enabled flags)
              Example: [{'date': '2025-10-15', 'hours': [{'id': '1', 'title': '09:00', 'enabled': True}, ...]}, ...]
    """
    
    all_hours = sorted(all_hours)
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    available_dates = []
    current_date = start
    
    while current_date <= end and len(available_dates) < max_days:
        # Check if this weekday is allowed for interviews
        weekday_name = _weekday_to_short_name(current_date.weekday())
        if interview_days and weekday_name not in interview_days:
            current_date += timedelta(days=1)
            continue
        
        # Check if this date is excluded
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str in unavailable_dates:
            current_date += timedelta(days=1)
            continue
        
        # Build hours array with availability for this specific date
        hours = []
        for i, hour in enumerate(all_hours):
            is_available = is_slot_available(company_id, date_str, hour, max_capacity)
            hours.append({
                "id": str(i + 1),
                "title": hour,
                "enabled": is_available,
                "on-select-action": {
                    "name": "update_data",
                    "payload": {
                        "selected_hour": hour
                    }
                }
            })
        
        available_dates.append({
            'date': date_str,
            'hours': hours
        })
        
        current_date += timedelta(days=1)
    
    return available_dates

def store_reference_assessment(reference_id, assessment):
    reference_row = db.session.query(CandidateReferences).get(reference_id)
    if reference_row:
        reference_row.assessment = assessment
        reference_row.reference_complete = True
        db.session.commit()

def save_answer_json(candidate_id, question_id, answer_json):
    try:
        # Buscar registro existente
        answer = db.session.query(ScreeningAnswers).filter_by(
            candidate_id=candidate_id,
            question_id=question_id
        ).one()
        # Actualizar campo JSON y fecha
        answer.answer_json = answer_json
        answer.created_at = db.func.now()
    except NoResultFound:
        # No existe, crear uno nuevo
        answer = ScreeningAnswers(
            candidate_id=candidate_id,
            question_id=question_id,
            answer_json=answer_json,
        )
        db.session.add(answer)
    db.session.commit()


def update_funnel_state(candidate_id, new_state):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
    if candidate:
        previous_state = candidate.funnel_state or ""
        if candidate.funnel_state != new_state:
            log_funnel_state_change(candidate_id, previous_state, new_state)
            candidate.funnel_state = new_state
            db.session.commit()
            #Send funnel state to mixpanel
            send_funnel_state_mixpanel(candidate_id, new_state, candidate.company_id)
        return True
    return False

def update_screening_rejection(candidate_id, rejected_reason):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()

    if not candidate:
        raise ValueError(f"No se encontró candidato con ID {candidate_id}")

    candidate.rejected_reason = "screening"
    candidate.screening_rejected_reason = rejected_reason

    db.session.commit()

def log_response_time(candidate_data, start_time, end_time, time_delta, assistant_id, model, prompt_tokens, completion_tokens, total_tokens):
    """
    Log time it takes for an assistant to generate a response including token and model info using SQLAlchemy
    """
    try:
        record = ResponseTiming(
            employee_id=candidate_data.get("candidate_id", 99999),
            company_id=candidate_data.get("company_id", 99999),
            start_time=start_time,
            end_time=end_time,
            time_delta=time_delta,
            assistant_id=assistant_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while logging response time: {e}")

def add_travel_time_minutes(candidate_data, duration_minutes):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_data.get("candidate_id")).first()
    if candidate:
        candidate.travel_time_minutes = duration_minutes
        logging.info(f"Added travel time {duration_minutes} minutes for candidate {candidate_data.get('candidate_id')}")
        db.session.commit()
        return True
    return False

def add_role(candidate_data, role):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_data.get("candidate_id")).first()
    if candidate:
        candidate.role_id = role
        logging.info(f"Added role {role} for candidate {candidate_data.get('candidate_id')}")
        db.session.commit()
        return True

def add_interview_date_time(candidate_data, nfm_reply):
    """
    Parse the WhatsApp Flow (nfm_reply) payload, extract the selected
    interview *fecha* (date) and *hora* (time), combine them into a
    timezone-aware ``datetime`` instance and persist it in the
    ``Candidates.interview_date_time`` column.

    Expected payload example (string or dict):
        {
            "flow_token": "{\"flow_type\": \"appointment_booking\", \"expiration_date\": \"2025-06-12T17:00:59.562695\"}",
            "fecha": "2025-08-12",
            "hora": "10:00"
        }
    """
    # Ensure we work with a dict
    try:
        if isinstance(nfm_reply, str):
            reply_dict = json.loads(nfm_reply)
        elif isinstance(nfm_reply, dict):
            reply_dict = nfm_reply
        else:
            logging.error(f"Unexpected type for nfm_reply: {type(nfm_reply)} – value: {nfm_reply}")
            return False
    except json.JSONDecodeError as err:
        logging.error(f"Failed to decode nfm_reply JSON: {err} – value: {nfm_reply}")
        return False

    fecha = reply_dict.get("fecha")  # e.g. '2025-08-12'
    hora = reply_dict.get("hora")    # e.g. '10:00'

    if not (fecha and hora):
        logging.error(f"Missing 'fecha' or 'hora' in nfm_reply: {reply_dict}")
        return False

    try:
        # Combine to ISO string 'YYYY-MM-DDTHH:MM' then parse
        combined = f"{fecha}T{hora}"
        interview_dt = datetime.fromisoformat(combined)

        # Make the datetime explicit in UTC to satisfy timestamptz column
        interview_dt = interview_dt.replace(tzinfo=timezone.utc)
    except Exception as err:
        logging.error(f"Error constructing interview datetime from fecha={fecha}, hora={hora}: {err}")
        return False

    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_data.get("candidate_id")).first()
        if candidate:
            candidate.interview_date_time = interview_dt
            db.session.commit()
            logging.info(f"Saved interview_date_time {interview_dt.isoformat()} for candidate {candidate.candidate_id}")
            return True
        else:
            logging.warning(f"Candidate not found for ID {candidate_data.get('candidate_id')}")
            return False
    except Exception as err:
        db.session.rollback()
        logging.error(f"Database error while saving interview datetime: {err}")
        return False

#Function to store updated data for candidates upon each interaction
def apply_candidate_updates(candidate_id, updates_list):
    """
    Applies updates to the Candidates model based on assistant output.

    Args:
        db: SQLAlchemy database instance
        candidate_id: ID of the candidate to update
        updates_list: a list of dicts like [{"name": "Juan"}, {"role_id": 3}]

    Returns:
        True if updates were applied successfully, False otherwise
    """
    if not updates_list:
        return False

    try:
        candidate = Candidates.query.get(candidate_id)
        if not candidate:
            logging.warning(f"[apply_candidate_updates] Candidate not found: {candidate_id}")
            return False

        allowed_fields = {c.name for c in Candidates.__table__.columns}
        updated_fields = {}

        for update in updates_list:
            for field, value in update.items():
                if field in allowed_fields and value is not None:
                    setattr(candidate, field, value)
                    updated_fields[field] = value

        if updated_fields:
            db.session.commit()
            return True
        else:
            return False

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"[apply_candidate_updates] DB error for candidate {candidate_id}: {e}")
        return False

    except Exception as e:
        logging.exception(f"[apply_candidate_updates] Unexpected error for candidate {candidate_id}: {e}")
        return False

def get_active_roles_for_company(company_id):
    """
    Fetch active roles for a given company as a list of dicts
    with role_id, role_name, and shift.

    Args:
        company_id (int): The company to filter roles by.

    Returns:
        list[dict]: List of role dictionaries like:
                    [{ "role_id": 1, "role_name": "Ayudante general", "shift": "Día 6-14" }, ...]
    """
    roles = (
        Roles.query
        .filter_by(company_id=company_id, active=True)
        .with_entities(Roles.role_id, Roles.role_name, Roles.shift)
        .all()
    )

    return [{"role_id": r.role_id, "role_name": r.role_name, "shift": r.shift} for r in roles]

def save_candidate_grade(candidate_id: int, new_grade: int) -> bool:
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).one()
        candidate.grade = new_grade
        db.session.commit()
        logging.info(f"Updated candidate {candidate_id} with grade {new_grade}")
        return True
    except NoResultFound:
        logging.warning(f"No candidate found with ID {candidate_id}")
        return False
    except Exception as e:
        logging.error(f"Error updating grade for candidate {candidate_id}: {e}")
        db.session.rollback()
        return False
    
def update_candidate_grade(candidate_id: int, reference_grade):

    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()

        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return

        current_grade = candidate.grade or 0
        updated_grade = int(current_grade + 0.05 * reference_grade)

        candidate.grade = updated_grade
        db.session.commit()

        logging.info(f"Updated candidate ID {candidate_id} grade from {current_grade} to {updated_grade}")

    except Exception as e:
        logging.error(f"Error updating grade for candidate {candidate_id}: {e}")
        db.session.rollback()

def get_active_roles_text(company_id):
    # Query active roles for the given company
    roles = Roles.query.filter_by(company_id=company_id, active=True).order_by(Roles.role_name).all()
    
    if not roles:
        return "No hay puestos activos para esta empresa."

    # Build the roles list without the question prompt
    lines = []
    for idx, role in enumerate(roles, start=1):
        lines.append(f"{idx}️⃣ {role.role_name}")

    return "\n".join(lines)

def update_list_reply(list_id: str, candidate_data: dict):
    """
    Updates a field on the Candidates table using a list_reply ID in the format "field$value".
    
    Special handling for interview_date_time:
    - Updates interview_date_time
    - Updates funnel_state to 'scheduled_interview'
    - Updates interview_address and interview_map_link from company settings
    - Returns a confirmation message

    Args:
        list_id (str): e.g. "role_id$3" or "interview_date_time$2025-07-01T10:00:00"
        candidate_data (dict): Dictionary containing at least 'candidate_id'
        
    Returns:
        str or None: Confirmation message for interview_date_time, None otherwise
    """
    
    try:
        # Split and validate
        if "$" not in list_id:
            logging.warning(f"Invalid list_id format: '{list_id}'")
            return None

        field, raw_value = list_id.split("$", 1)

        # Fetch candidate
        candidate_id = candidate_data.get("candidate_id")
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()

        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return None

        # Check if field exists
        if not hasattr(Candidates, field):
            logging.warning(f"Field '{field}' does not exist on Candidates model")
            return None

        column = getattr(Candidates, field).property.columns[0]
        column_type = column.type

        # Type conversion
        if isinstance(column_type, db.Integer):
            value = int(raw_value)
        elif isinstance(column_type, (db.String, db.Text)):
            value = raw_value
        elif isinstance(column_type, db.Boolean):
            # Convert string to boolean
            value = raw_value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(column_type, db.DateTime):
            try:
                value = datetime.strptime(raw_value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    value = datetime.strptime(raw_value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    logging.error(f"Invalid datetime format: '{raw_value}' for field '{field}'")
                    return None
        else:
            logging.warning(f"Unsupported column type '{column_type}' for field '{field}'")
            return None

        # Set and commit
        setattr(candidate, field, value)
        
        # Special handling for interview_date_time: also update funnel_state and location info
        confirmation_message = None
        if field == "interview_date_time":
            # Log funnel state change before updating (important for tracking reschedules)
            previous_state = candidate.funnel_state or ""
            new_state = "scheduled_interview"
            if previous_state != new_state:
                log_funnel_state_change(candidate_id, previous_state, new_state)
                # Send funnel state to mixpanel (consistent with update_funnel_state behavior)
                send_funnel_state_mixpanel(candidate_id, new_state, candidate.company_id)
                logging.info(f"Logged funnel state change for candidate {candidate_id}: {previous_state} -> {new_state}")
            
            candidate.funnel_state = new_state
            
            # Get role-specific interview location from candidate_data
            # This uses the correctly resolved location from _resolve_interview_location
            interview_location = candidate_data.get("interview_location") or {}
            interview_address = (
                candidate_data.get("final_interview_address")
                or interview_location.get("address")
                or "No disponible"
            )
            map_link = (
                candidate_data.get("final_interview_map_link")
                or interview_location.get("url")
                or "No disponible"
            )
            
            # Update candidate with resolved location
            candidate.interview_address = interview_address
            candidate.interview_map_link = map_link
            
            logging.info(f"Updated interview location for candidate {candidate_id}: address={interview_address}, link={map_link}")
            
            # Get additional info if available
            company_id = candidate_data.get("company_id")
            additional_info = get_company_additional_info(company_id)
            
            # Format datetime for display
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            month_names = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            
            interview_dt = value  # This is the datetime object we just created
            day_name = day_names[interview_dt.weekday()]
            month_name = month_names[interview_dt.month - 1]
            formatted_date = f"{day_name} {interview_dt.day} de {month_name}"
            
            # Convert hour to 12-hour AM/PM format
            hour = interview_dt.hour
            minute = interview_dt.minute
            period = 'AM' if hour < 12 else 'PM'
            display_hour = hour if hour <= 12 else hour - 12
            display_hour = 12 if display_hour == 0 else display_hour
            formatted_time = f"{display_hour}:{minute:02d} {period}"
            
            # Build confirmation message matching nfm_reply format
            confirmation_message = "Gracias por agendar tu entrevista:\n\n"
            confirmation_message += f"*Fecha de la entrevista*: {formatted_date}\n"
            confirmation_message += f"*Hora de la entrevista*: {formatted_time}\n\n"
            confirmation_message += f"*Dirección*: {interview_address}\n"
            confirmation_message += f"*Ubicación*: {map_link}"
            
            if additional_info:
                confirmation_message += f"\n\n{additional_info}"
        
        db.session.commit()
        logging.info(f"✅ Updated candidate_id={candidate_id}: {field} = {value}")
        
        return confirmation_message

    except Exception as e:
        logging.error(f"Error updating candidate_id={candidate_data.get('candidate_id')}: {e}")
        db.session.rollback()
        return None

def get_candidates_to_remind(company_id=None):
    # System time is UTC, DB times are in local (Mexico, UTC-6)
    # So we work directly in local time

    # Current time in UTC
    utc_now = datetime.now()

    # Convert to Mexico local time by subtracting 6 hours
    mexico_now = utc_now - timedelta(hours=6)

    # Determine "tomorrow" in Mexico local time
    mexico_tomorrow = (mexico_now + timedelta(days=1)).date()

    # Build datetime range for that day (in local time)
    start_mexico = datetime.combine(mexico_tomorrow, time.min)
    end_mexico = datetime.combine(mexico_tomorrow, time.max)

    # Base query filters
    query = db.session.query(Candidates).filter(
        Candidates.interview_date_time >= start_mexico,
        Candidates.interview_date_time <= end_mexico,
        Candidates.interview_reminder_sent == False,
        Candidates.phone.isnot(None)
    )
    
    # Add company_id filter if specified
    if company_id is not None:
        query = query.filter(Candidates.company_id == company_id)
    
    return query.all()

#Reminder to finish flow
def get_candidates_to_remind_application():
    now = datetime.now()  # returns UTC (your system's default)
    cutoff_time = now - timedelta(hours=23)  # candidates created before this point are eligible

    return (
        db.session.query(Candidates)
        .filter(
            Candidates.funnel_state == 'screening_in_progress',  # still in the application flow
            Candidates.application_reminder_sent == False,       # not reminded yet
            Candidates.created_at <= cutoff_time,                # created over 23 hours ago
            Candidates.phone.isnot(None)                         # can actually be messaged
        )
        .all()
    )

#Get a whatsapp sender id based on a company id
def get_company_wa_id(company_id):
    company = (
        db.session.query(CompaniesScreening)
        .filter(CompaniesScreening.company_id == company_id)
        .first()
    )
    if company and company.wa_id:
        return company.wa_id
    return None

def get_message_text_by_keyword(keyword):
    """
    Retrieves the `text` field from the MessageTemplates table for a given keyword.

    Args:
        keyword (str): The keyword to search for.

    Returns:
        str | None: The corresponding text if found, otherwise None.
    """
    template = (
        db.session.query(MessageTemplates)
        .filter(MessageTemplates.keyword == keyword)
        .first()
    )
    return template.text if template else None

def update_flow_state(candidate_data: dict, new_state: str):
    """
    Updates the flow_state for a candidate using a candidate_data dict.

    Args:
        candidate_data (dict): Dictionary containing at least 'candidate_id'
        new_state (str): New value to set for flow_state: respuesta, aclaración, pregunta, interrumpir_chat
    """
    try:
        candidate_id = candidate_data.get("candidate_id")
        if not candidate_id:
            logging.warning("Missing candidate_id in candidate_data")
            return

        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return

        candidate.flow_state = new_state
        db.session.commit()
        logging.info(f"✅ flow_state updated for candidate_id={candidate_id} -> {new_state}")

    except Exception as e:
        logging.error(f"❌ Error updating flow_state for candidate_id={candidate_data.get('candidate_id')}: {e}")
        db.session.rollback()

def update_candidate_interview_address_and_link(candidate_id: int, interview_address: str, interview_link: str):
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return
        candidate.interview_address = interview_address
        candidate.interview_map_link = interview_link
        db.session.commit()
        logging.info(f"✅ interview_address and interview_link updated for candidate_id={candidate_id}")
    except Exception as e:
        logging.error(f"❌ Error updating interview_address and interview_link for candidate_id={candidate_id}: {e}")
        db.session.rollback()

def get_eligibility_questions_and_answers(candidate_id: int, company_id: int, role_data):
    """
    Get all eligibility questions from the general set and the candidate's answers to those questions.
    
    Args:
        candidate_id (int): The candidate's ID
        company_id (int): The company's ID
        
    Returns:
        dict: Dictionary containing question-answer pairs for eligibility evaluation
    """
    try:
        
        eligibility_criteria = role_data.get('eligibility_criteria', {})
        eligibility_question_ids = [int(question_id) for question_id in eligibility_criteria.keys()]

        # Get all eligibility questions from the general set
        eligibility_questions = (
            db.session.query(ScreeningQuestions)
            .filter(ScreeningQuestions.question_id.in_(eligibility_question_ids), ScreeningQuestions.is_active == True)
            .order_by(ScreeningQuestions.position)
            .all()
        )
        
        if not eligibility_questions:
            logging.warning(f"No eligibility questions found for company {company_id}")
            return {}
        
        # Get candidate's answers to these questions
        question_ids = [q.question_id for q in eligibility_questions]
        answers = (
            db.session.query(ScreeningAnswers)
            .filter(
                ScreeningAnswers.candidate_id == candidate_id,
                ScreeningAnswers.question_id.in_(question_ids)
            )
            .all()
        )
        
        # Create a mapping of question_id to answer
        answer_map = {answer.question_id: answer for answer in answers}
        
        # Build the result dictionary with question_id, question_text, and answer_text
        result = {}
        for question in eligibility_questions:
            answer_obj = answer_map.get(question.question_id)
            
            if answer_obj:
                # Check if this is a location question and has answer_json
                if question.response_type == 'location' and answer_obj.answer_json:
                    try:
                        answer_json = answer_obj.answer_json
                        if isinstance(answer_json, str):
                            answer_json = json.loads(answer_json)
                        answer_text = answer_json.get("duration_text", "No disponible")
                    except (json.JSONDecodeError, AttributeError) as e:
                        logging.warning(f"Error parsing answer_json for question {question.question_id}: {e}")
                        answer_text = answer_obj.answer_raw or "No respondido"
                else:
                    answer_text = answer_obj.answer_raw or "No respondido"
            else:
                answer_text = "No respondido"
            
            result[str(question.question_id)] = {
                "question_id": question.question_id,
                "question_text": question.question,
                "answer_text": answer_text
            }
        
        # Add fake gender question for company_id = 6
        if company_id in (6, 160):
            candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
            if candidate:
                fake_question_id = 1  # Using a high number to avoid conflicts
                gender_answer = candidate.gender or "No respondido"
                
                result[str(fake_question_id)] = {
                    "question_id": fake_question_id,
                    "question_text": "cual es tu genero",
                    "answer_text": gender_answer
                }
                logging.info(f"Added fake gender question for candidate {candidate_id}, company {company_id}")
        
        logging.info(f"Retrieved {len(result)} eligibility questions and answers for candidate {candidate_id}")
        return result
        
    except Exception as e:
        logging.error(f"Error retrieving eligibility questions and answers for candidate {candidate_id}: {e}")
        return {}

def get_company_roles_with_criteria(company_id: int):
    """
    Get all active roles for a company along with their eligibility criteria.
    
    Args:
        company_id (int): The company's ID
        
    Returns:
        list: List of dictionaries containing role_id, role_name, and eligibility_criteria
    """
    try:
        roles = (
            db.session.query(Roles)
            .filter_by(company_id=company_id, active=True)
            .all()
        )
        
        result = []
        for role in roles:
            result.append({
                "role_id": role.role_id,
                "role_name": role.role_name,
                "eligibility_criteria": role.eligibility_criteria or {}
            })
        
        logging.info(f"Retrieved {len(result)} active roles for company {company_id}")
        return result
        
    except Exception as e:
        logging.error(f"Error retrieving roles for company {company_id}: {e}")
        return []

def update_candidate_eligible_roles(candidate_id: int, eligible_role_ids: list):
    """
    Update the eligible_roles JSON field for a candidate.
    
    Args:
        candidate_id (int): The candidate's ID
        eligible_role_ids (list): List of role IDs the candidate is eligible for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return False
        
        candidate.eligible_roles = eligible_role_ids
        db.session.commit()
        logging.info(f"✅ Updated eligible_roles for candidate {candidate_id}: {eligible_role_ids}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error updating eligible_roles for candidate {candidate_id}: {e}")
        db.session.rollback()
        return False

def get_candidate_eligible_roles(candidate_id: int):
    """
    Get the eligible roles for a candidate.
    
    Args:
        candidate_id (int): The candidate's ID
        
    Returns:
        list: List of eligible role IDs, or empty list if none found
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return []
        
        return candidate.eligible_roles or []
        
    except Exception as e:
        logging.error(f"Error retrieving eligible_roles for candidate {candidate_id}: {e}")
        return []

def handle_role_selection(candidate_id: int, selection: str):
    """
    Handle role selection by candidate and update their role_id.
    
    Args:
        candidate_id (int): The candidate's ID
        selection (str): The selection from list_reply (either "role_id$X" or "no_preference")
        
    Returns:
        tuple: (success: bool, selected_role_id: int or None, message: str)
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return False, None, "Candidato no encontrado"
        
        eligible_roles = candidate.eligible_roles or []
        selected_role_id = None
        
        if selection == "no_preference":
            # Move the empty eligible roles check here (before randomizer)
            if not eligible_roles:
                logging.warning(f"No eligible roles found for candidate {candidate_id}")
                return False, None, "No hay puestos elegibles"
            
            # Randomly select from eligible roles
            selected_role_id = random.choice(eligible_roles)
            logging.info(f"Randomly selected role {selected_role_id} for candidate {candidate_id}")
        
        elif selection.startswith("role_id$"):
            # Extract role_id from selection
            try:
                selected_role_id = int(selection.split("$")[1])
                # removed: eligible_roles validation (selected_role_id not in eligible_roles)
            except (ValueError, IndexError):
                logging.error(f"Invalid role selection format: {selection} for candidate {candidate_id}")
                return False, None, "Formato de selección inválido"
        
        else:
            logging.error(f"Unknown selection format: {selection} for candidate {candidate_id}")
            return False, None, "Selección desconocida"
        
        # Update candidate's role_id
        candidate.role_id = selected_role_id
        db.session.commit()
        
        # Get role name for confirmation
        role = db.session.query(Roles).filter_by(role_id=selected_role_id).first()
        role_name = role.role_name if role else f"Puesto ID {selected_role_id}"
        
        logging.info(f"✅ Updated candidate {candidate_id} role_id to {selected_role_id} ({role_name})")
        return True, selected_role_id, f"Has seleccionado: {role_name}"
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error handling role selection for candidate {candidate_id}: {e}")
        return False, None, "Error al procesar la selección"


def store_candidate_media(media_data):
    """
    Store candidate media metadata in the database.
    
    Args:
        media_data (dict): Dictionary containing media metadata
        
    Returns:
        int: media_id if successful, None otherwise
    """
    try:
        # Reflect once and cache table
        if not hasattr(store_candidate_media, "_table"):
            metadata = getattr(db, "metadata", None) or getattr(db, "Model").metadata  # type: ignore[attr-defined]
            store_candidate_media._table = Table("candidate_media", metadata, autoload_with=db.engine)
        T = store_candidate_media._table

        stmt = (
            insert(T)
            .values(
                candidate_id=media_data.get("candidate_id"),
                company_id=media_data.get("company_id"),
                question_id=media_data.get("question_id"),
                set_id=media_data.get("set_id"),
                file_name=media_data.get("file_name"),
                mime_type=media_data.get("mime_type"),
                file_size=media_data.get("file_size"),
                s3_bucket=media_data.get("s3_bucket"),
                s3_key=media_data.get("s3_key"),
                s3_url=media_data.get("s3_url"),
                whatsapp_media_id=media_data.get("whatsapp_media_id"),
                sha256_hash=media_data.get("sha256_hash"),
                flow_token=media_data.get("flow_token"),
            )
            .returning(T.c.media_id)
        )

        media_id = db.session.execute(stmt).scalar_one()
        db.session.commit()

        logging.info(
            f"✅ Stored media metadata for candidate {media_data['candidate_id']}: media_id={media_id}"
        )
        return media_id

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"❌ Error storing media metadata for candidate {media_data.get('candidate_id')}: {e}"
        )
        return None

def get_candidate_media(candidate_id, question_id=None):
    """
    Retrieve media files for a candidate, optionally filtered by question.
    
    Args:
        candidate_id (int): The candidate's ID
        question_id (int, optional): Filter by specific question
        
    Returns:
        list: List of media records
    """
    try:
        # Reflect once and cache table
        if not hasattr(get_candidate_media, "_table"):
            metadata = getattr(db, "metadata", None) or getattr(db, "Model").metadata  # type: ignore[attr-defined]
            get_candidate_media._table = Table("candidate_media", metadata, autoload_with=db.engine)
        T = get_candidate_media._table

        stmt = (
            select(
                T.c.media_id,
                T.c.candidate_id,
                T.c.company_id,
                T.c.question_id,
                T.c.set_id,
                T.c.file_name,
                T.c.mime_type,
                T.c.file_size,
                T.c.s3_bucket,
                T.c.s3_key,
                T.c.s3_url,
                T.c.upload_timestamp,
                T.c.whatsapp_media_id,
                T.c.sha256_hash,
                T.c.flow_token,
            )
            .where(T.c.candidate_id == candidate_id)
            .order_by(T.c.upload_timestamp.desc())
        )
        if question_id:
            stmt = stmt.where(T.c.question_id == question_id)

        rows = db.session.execute(stmt).all()
        media_records = [
            {
                "media_id": r.media_id,
                "candidate_id": r.candidate_id,
                "company_id": r.company_id,
                "question_id": r.question_id,
                "set_id": r.set_id,
                "file_name": r.file_name,
                "mime_type": r.mime_type,
                "file_size": r.file_size,
                "s3_bucket": r.s3_bucket,
                "s3_key": r.s3_key,
                "s3_url": r.s3_url,
                "upload_timestamp": r.upload_timestamp,
                "whatsapp_media_id": r.whatsapp_media_id,
                "sha256_hash": r.sha256_hash,
                "flow_token": r.flow_token,
            }
            for r in rows
        ]

        logging.info(
            f"Retrieved {len(media_records)} media records for candidate {candidate_id}"
        )
        return media_records

    except Exception as e:
        logging.error(f"Error retrieving media for candidate {candidate_id}: {e}")
        return []

def create_run_in_db(thread_id, run_id, status="in_progress"):
    """
    Inserts or updates a run record for the given thread_id and run_id.
    Ensures only one active run per thread_id.
    """
    try:
        existing_run = db.session.query(ActiveOpenAIRun).filter_by(run_id=run_id).first()
        if existing_run:
            existing_run.status = status
        else:
            new_run = ActiveOpenAIRun(thread_id=thread_id, run_id=run_id, status=status)
            db.session.add(new_run)
        db.session.commit()
    except Exception as e:
        logging.error(f"[create_run_in_db] Failed to insert run {run_id}: {e}")
        db.session.rollback()

def insert_openai_run_status(thread_id, run_id, status, source=None):
    """
    Inserts a new run status record in the database.
    """
    try:
        run = ActiveOpenAIRun(thread_id=thread_id, run_id=run_id, status=status, source=source)
        db.session.add(run)
        db.session.commit()
        logging.info(f"[insert_openai_run_status] Inserted run {run_id} on thread {thread_id} with status '{status}' by {source}.")
    except Exception as e:
        logging.error(f"[insert_openai_run_status] DB error while inserting run {run_id}: {e}")
        db.session.rollback()

def get_run_status(run_id):
    """
    Returns the status and source of a given run.
    """
    try:
        run = db.session.query(ActiveOpenAIRun).filter_by(run_id=run_id).first()
        if run:
            return run.status, run.source
        return None, None
    except Exception as e:
        logging.error(f"[get_run_status] Error retrieving run {run_id}: {e}")
        return None, None

def mark_end_flow_rejected(candidate_id):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
    if candidate:
        candidate.end_flow_rejected = True
        db.session.commit()
        return True
    return False

def mark_interview_confirmed(candidate_id):
    candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
    if candidate:
        candidate.interview_confirmed = True
        db.session.commit()
        return
    return

def mark_interview_completed(candidate_id):
    """Mark a candidate as having completed a physical interview.

    - Adds a funnel log from previous state to 'interview_completed'
    - Updates candidate.funnel_state accordingly
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"mark_interview_completed: candidate {candidate_id} not found")
            return False
        previous_state = candidate.funnel_state
        log_funnel_state_change(candidate_id, previous_state, 'interview_completed')
        candidate.funnel_state = 'interview_completed'
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error marking interview completed for candidate {candidate_id}: {e}")
        return False
def log_funnel_state_change(candidate_id, previous_state, new_state):
    new_log = CandidateFunnelLog(
        candidate_id=candidate_id,
        previous_funnel_state=previous_state,
        new_funnel_state=new_state
    )
    db.session.add(new_log)
    db.session.commit()

def get_candidate_origin(candidate_id, company_id):
    """
    Determines the origin of a single candidate and saves it to the database:
    - 'facebook_ads': any message contains ad_trigger_phrase
    - 'baltra': wa_id appears in candidate_references.reference_wa_id
    - 'second_time_applicant': another candidate exists with same wa_id
    - 'other': fallback
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id, company_id=company_id).one_or_none()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found in company {company_id}")

        wa_id = candidate.phone
        origin = "other"

        # Get ad trigger phrase
        company = db.session.query(CompaniesScreening).filter_by(company_id=company_id).one_or_none()
        ad_phrase = company.ad_trigger_phrase if company and company.ad_trigger_phrase else ""

        # 1. Check if any message contains ad_trigger_phrase
        if ad_phrase:
            matched = (
                db.session.query(ScreeningMessages)
                .filter(
                    ScreeningMessages.candidate_id == candidate_id,
                    ScreeningMessages.message_body.ilike(f"%{ad_phrase}%")
                )
                .first()
            )
            if matched:
                origin = "facebook_ads"

        # 2. Check if candidate was referred via baltra (wa_id in reference_wa_id for another candidate from same company)
        if db.session.query(CandidateReferences) \
            .join(Candidates, CandidateReferences.candidate_id == Candidates.candidate_id) \
            .filter(
                CandidateReferences.reference_wa_id == wa_id,
                Candidates.company_id == company_id
            ).first():
            if origin == 'other':
                origin = "baltra"

        # 3. Check if wa_id has already applied before as a different candidate
        if db.session.query(Candidates) \
            .filter(
                Candidates.phone == wa_id,
                Candidates.candidate_id != candidate_id,
                Candidates.company_id == company_id
            ).first():
            if origin == 'other':
                origin = "second_time_applicant"

        # Update candidate source
        candidate.source = origin
        db.session.commit()

        return origin

    except Exception as e:
        logging.error(f"Error determining origin for candidate {candidate_id}: {e}")
        db.session.rollback()
        raise RuntimeError("Could not determine candidate origin") from e


# -------- Nearest locations (shortlist + coordinator) --------

def _is_valid_lat_lng(lat: float, lng: float) -> bool:
    return lat is not None and lng is not None and -90.0 <= float(lat) <= 90.0 and -180.0 <= float(lng) <= 180.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lon points in kilometers.
    """
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def shortlist_top8(candidate_lat: float, candidate_lon: float, locations: Iterable[Dict]) -> List[Dict]:
    """
    Return the 8 closest locations by straight-line distance.
    Uses a size-8 max-heap for O(n) selection. Ignores invalid lat/lng rows.
    """
    heap: List[Tuple[float, Dict]] = []  # stores (-distance_km, loc)

    for loc in locations:
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if not _is_valid_lat_lng(lat, lng):
            logging.debug(f"Ignoring invalid location row (lat/lng): {loc}")
            continue

        d_km = haversine_km(candidate_lat, candidate_lon, float(lat), float(lng))
        item = (-d_km, loc)
        if len(heap) < 8:
            heapq.heappush(heap, item)
        else:
            if d_km < -heap[0][0]:
                heapq.heapreplace(heap, item)

    # sort ascending by geometric distance
    top8 = [loc for _, loc in sorted(heap, key=lambda t: -t[0])]
    # attach straight-line distance for reference
    for i, loc in enumerate(top8):
        top8[i] = {
            **loc,
            "_haversine_km": haversine_km(
                candidate_lat, candidate_lon, float(loc["latitude"]), float(loc["longitude"])  # type: ignore[arg-type]
            ),
        }
    return top8


def fetch_company_locations(company_id: int) -> List[Dict]:
    """
    Fetch candidate locations filtered by company.
    Only selects columns needed for distance calc and identification.
    Returns: [{ "location_id": int, "company_id": int, "latitude": float, "longitude": float }, ...]
    """
    try:
        # Reflect once and cache tables
        if not hasattr(fetch_company_locations, "_locations_table"):
            metadata = getattr(db, "metadata", None) or getattr(db, "Model").metadata  # type: ignore[attr-defined]
            fetch_company_locations._locations_table = Table("locations", metadata, autoload_with=db.engine)
        L = fetch_company_locations._locations_table

        # location_roles table removed; always fetch by company only
        query = select(L.c.location_id, L.c.company_id, L.c.latitude, L.c.longitude).where(
            L.c.company_id == company_id
        )

        rows = db.session.execute(query).all()
        return [
            {
                "location_id": int(r.location_id),
                "company_id": int(r.company_id),
                "latitude": float(r.latitude) if r.latitude is not None else None,
                "longitude": float(r.longitude) if r.longitude is not None else None,
            }
            for r in rows
        ]
    except Exception as e:
        logging.error(f"Error fetching locations for company_id={company_id}: {e}")
        return []


def get_top5_locations_by_transit(candidate_lat: float, candidate_lon: float, *, company_id: int, api_key: Optional[str] = None) -> List[Dict]:
    """
    1) Query DB for locations filtered by company.
    2) Shortlist 8 by Haversine.
    3) Call Route Matrix (TRANSIT) for those 8, filter out locations >200 minutes travel time.
    4) Pick up to 5 locations with shortest travel time (could return fewer if many are >200 min).
    5) If all locations are >200min, return special 'rejection' response.
    6) Fallback: if matrix fails completely, return top 5 by Haversine order (no time filtering).
    """
    logging.info(f"🚀 Starting get_top5_locations_by_transit for candidate at ({candidate_lat}, {candidate_lon}), company_id={company_id}")
    
    locations = fetch_company_locations(company_id)
    if not locations:
        logging.warning(f"⚠️ No locations found for company_id={company_id}")
        return []

    logging.info(f"📍 Found {len(locations)} total locations for company")

    # shortlist 8 by geometric distance
    top8 = shortlist_top8(candidate_lat, candidate_lon, locations)
    if not top8:
        logging.warning(f"⚠️ No valid locations after Haversine shortlisting")
        return []

    logging.info(f"📏 Shortlisted {len(top8)} locations by Haversine distance")

    # transit matrix for those 8
    logging.info(f"🚌 Calling Google Maps Transit Route Matrix API for {len(top8)} locations")
    svc = LocationService(api_key=api_key)
    dest_payload = [
        {"id": l["location_id"], "lat": float(l["latitude"]), "lng": float(l["longitude"])}
        for l in top8
    ]

    elements: List[Dict] = []
    try:
        elements = svc.compute_transit_route_matrix(
            {"lat": float(candidate_lat), "lng": float(candidate_lon)}, dest_payload
        )
        logging.info(f"✅ Transit matrix API returned {len(elements)} results")
    except Exception as e:
        logging.warning(f"❌ Route Matrix error (TRANSIT): {e}")

    if elements:
        # Filter out locations with more than 200 minutes (12,000 seconds) travel time
        MAX_TRAVEL_TIME_SECONDS = 200 * 60  # 200 minutes in seconds
        logging.info(f"🔍 Starting transit filtering with {len(elements)} elements, MAX_TRAVEL_TIME_SECONDS: {MAX_TRAVEL_TIME_SECONDS}")
        
        filtered_elements = []
        for el in elements:
            duration_seconds = el.get("duration_seconds")
            logging.info(f"Evaluating element: id={el.get('id')}, duration_seconds={duration_seconds}")
            
            if duration_seconds is not None and duration_seconds <= MAX_TRAVEL_TIME_SECONDS:
                filtered_elements.append(el)
                logging.info(f"✅ Element accepted: id={el.get('id')}, duration={duration_seconds}s ({duration_seconds/60:.1f}min)")
            else:
                if duration_seconds is None:
                    logging.info(f"❌ Element rejected (no duration): id={el.get('id')}")
                else:
                    logging.info(f"❌ Element rejected (too far): id={el.get('id')}, duration={duration_seconds}s ({duration_seconds/60:.1f}min)")
        
        logging.info(f"Filtering complete: {len(filtered_elements)} out of {len(elements)} elements passed the 200-minute filter")
        
        if filtered_elements:
            by_id = {l["location_id"]: l for l in top8}
            # Sort by duration and take up to 5 (could be less if many are filtered out)
            best_filtered = sorted(filtered_elements, key=lambda x: x["duration_seconds"])[:5]
            result: List[Dict] = []
            for el in best_filtered:
                loc = by_id.get(el["id"])  # type: ignore[index]
                if not loc:
                    continue
                result.append(
                    {
                        **loc,
                        "eta_seconds": el.get("duration_seconds"),
                        "distance_m": el.get("distance_meters"),
                        "haversine_km": loc.get("_haversine_km"),
                    }
                )
            # Return whatever we have (could be 1-5 locations), sorted by travel time
            if result:
                logging.info(f"✅ Returning {len(result)} filtered locations with travel times ≤200min:")
                for i, loc in enumerate(result, 1):
                    eta_min = loc.get('eta_seconds', 0) / 60 if loc.get('eta_seconds') else 'N/A'
                    logging.info(f"  {i}. Location ID {loc.get('location_id')}: {eta_min:.1f}min travel time")
                return result
        else:
            logging.warning(f"❌ No locations passed the 200-minute filter! All {len(elements)} locations were too far away.")
            # Return special rejection response when all locations are too far
            return [{"rejection_reason": "all_locations_too_far", "message": "Lamentablemente no contamos con vacantes a menos de 3 horas de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌"}]
    else:
        logging.warning(f"❌ No transit matrix results returned from Google Maps API")

    # fallback to locations within 50km by haversine (only when Google Maps API fails completely)
    # Filter by 50km limit and cap to maximum 5 results
    logging.warning(f"⚠️ Using Haversine fallback - filtering locations within 50km straight-line distance")
    fallback = []
    MAX_HAVERSINE_KM = 50.0
    MAX_RESULTS = 5
    
    for l in top8:
        haversine_km = l.get("_haversine_km", 0)
        if haversine_km <= MAX_HAVERSINE_KM:
            fallback.append({
                **l,
                "eta_seconds": None,
                "distance_m": None,
                "haversine_km": haversine_km,
            })
    
    # Cap to maximum 5 results (they're already sorted by distance from shortlist_top8)
    if len(fallback) > MAX_RESULTS:
        logging.info(f"📊 Found {len(fallback)} locations within {MAX_HAVERSINE_KM}km, capping to {MAX_RESULTS} closest")
        fallback = fallback[:MAX_RESULTS]
    
    # Log results
    if fallback:
        logging.info(f"📍 Returning {len(fallback)} locations within {MAX_HAVERSINE_KM}km:")
        for i, l in enumerate(fallback, 1):
            logging.info(f"  {i}. Location ID {l.get('location_id')}: {l.get('haversine_km'):.2f}km straight-line distance")
        logging.warning(f"🔄 Fallback complete: returning {len(fallback)} locations within {MAX_HAVERSINE_KM}km")
        return fallback
    else:
        logging.warning(f"❌ No locations found within {MAX_HAVERSINE_KM}km straight-line distance")
        return [{"rejection_reason": "all_locations_too_far", "message": "Lamentablemente no contamos con vacantes a menos de 50km de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌"}]


def get_roles_for_location_ids(company_id: int, location_ids: List[int]) -> Dict[int, Dict]:
    """
    Given a list of location_ids, fetch one active role per location for the company.
    Now that roles.location_id exists, we select directly from roles.
    Returns a mapping: { location_id: {"role_id": int, "role_name": str} }.
    If multiple roles exist for a location, the first encountered is returned.
    """
    if not location_ids:
        return {}
    try:
        # Reflect roles table once and cache
        if not hasattr(get_roles_for_location_ids, "_roles_table"):
            metadata = getattr(db, "metadata", None) or getattr(db, "Model").metadata  # type: ignore[attr-defined]
            get_roles_for_location_ids._roles_table = Table("roles", metadata, autoload_with=db.engine)
        R = get_roles_for_location_ids._roles_table

        stmt = (
            select(R.c.location_id, R.c.role_id, R.c.role_name)
            .where(R.c.company_id == company_id)
            .where(getattr(R.c, "active", True) == True)  # if 'active' exists, filter True; otherwise no-op
            .where(R.c.location_id.in_(location_ids))
        )

        rows = db.session.execute(stmt).all()
        out: Dict[int, Dict] = {}
        for r in rows:
            loc_id = int(r.location_id) if r.location_id is not None else None
            if loc_id is None:
                continue
            if loc_id not in out:  # pick the first role per location
                out[loc_id] = {"role_id": int(r.role_id), "role_name": r.role_name}
        return out
    except Exception as e:
        logging.error(
            f"Error fetching roles for locations {location_ids} in company_id={company_id}: {e}"
        )
        return {}


def log_eligibility_evaluation(
    candidate_id: int,
    company_id: int, 
    role_data: dict,
    questions_and_answers: dict,
    evaluation_result: dict,
    assistant_id: str = None,
    thread_id: str = None
):
    """
    Log an eligibility evaluation decision to the database for quality control tracking.
    
    Args:
        candidate_id (int): The candidate's ID
        company_id (int): The company's ID
        role_data (dict): Dictionary containing role_id, role_name, and eligibility_criteria
        questions_and_answers (dict): Dictionary of eligibility questions and candidate answers
        evaluation_result (dict): The AI's evaluation result containing 'eligible' and 'reasoning'
        assistant_id (str, optional): OpenAI assistant ID used
        thread_id (str, optional): OpenAI thread ID used
        
    Returns:
        int: evaluation_id if successful, None otherwise
    """
    try:
        log_entry = EligibilityEvaluationLog(
            candidate_id=candidate_id,
            company_id=company_id,
            role_id=role_data.get('role_id'),
            role_name=role_data.get('role_name', ''),
            
            # AI evaluation result
            is_eligible=evaluation_result.get('eligible', False),
            ai_reasoning=evaluation_result.get('reasoning', ''),
            raw_ai_response=evaluation_result,
            
            # Input data
            questions_and_answers=questions_and_answers,
            eligibility_criteria=role_data.get('eligibility_criteria', {}),
            
            # Metadata
            assistant_id=assistant_id,
            thread_id=thread_id,
            manual_review_status='pending'  # Mark as pending manual review
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        evaluation_id = log_entry.evaluation_id
        logging.info(
            f"✅ Logged eligibility evaluation {evaluation_id}: candidate {candidate_id}, "
            f"role {role_data.get('role_id')} ({role_data.get('role_name')}), eligible: {evaluation_result.get('eligible')}"
        )
        return evaluation_id
        
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"❌ Error logging eligibility evaluation for candidate {candidate_id}, role {role_data.get('role_id')}: {e}"
        )
        return None


def get_eligibility_evaluations_for_review(
    company_id: int = None,
    manual_review_status: str = 'pending',
    limit: int = 100,
    offset: int = 0
):
    """
    Get eligibility evaluations that need manual review.
    
    Args:
        company_id (int, optional): Filter by company
        manual_review_status (str): Filter by review status ('pending', 'reviewed', or None for all)
        limit (int): Maximum number of records to return
        offset (int): Number of records to skip
        
    Returns:
        list: List of eligibility evaluation records with related data
    """
    try:
        query = (
            db.session.query(EligibilityEvaluationLog)
            .join(Candidates, EligibilityEvaluationLog.candidate_id == Candidates.candidate_id)
            .join(Roles, EligibilityEvaluationLog.role_id == Roles.role_id)
            .order_by(EligibilityEvaluationLog.evaluation_date.desc())
        )
        
        if company_id is not None:
            query = query.filter(EligibilityEvaluationLog.company_id == company_id)
            
        if manual_review_status is not None:
            query = query.filter(EligibilityEvaluationLog.manual_review_status == manual_review_status)
            
        evaluations = query.offset(offset).limit(limit).all()
        
        # Convert to dictionaries with related data for easier consumption
        result = []
        for eval_log in evaluations:
            result.append({
                'evaluation_id': eval_log.evaluation_id,
                'candidate_id': eval_log.candidate_id,
                'candidate_name': eval_log.candidate.name,
                'candidate_phone': eval_log.candidate.phone,
                'company_id': eval_log.company_id,
                'role_id': eval_log.role_id,
                'role_name': eval_log.role_name,
                'is_eligible': eval_log.is_eligible,
                'ai_reasoning': eval_log.ai_reasoning,
                'raw_ai_response': eval_log.raw_ai_response,
                'questions_and_answers': eval_log.questions_and_answers,
                'eligibility_criteria': eval_log.eligibility_criteria,
                'evaluation_date': eval_log.evaluation_date,
                'manual_review_status': eval_log.manual_review_status,
                'manual_review_result': eval_log.manual_review_result,
                'manual_review_date': eval_log.manual_review_date,
                'assistant_id': eval_log.assistant_id,
                'thread_id': eval_log.thread_id,
            })
        
        logging.info(f"Retrieved {len(result)} eligibility evaluations for review")
        return result
        
    except Exception as e:
        logging.error(f"Error retrieving eligibility evaluations for review: {e}")
        return []


def update_manual_review_result(
    evaluation_id: int,
    manual_review_result: bool
):
    """
    Update the manual review result for an eligibility evaluation.
    
    Args:
        evaluation_id (int): The evaluation ID to update
        manual_review_result (bool): True if AI was correct, False if incorrect
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        evaluation = db.session.query(EligibilityEvaluationLog).filter_by(evaluation_id=evaluation_id).first()
        if not evaluation:
            logging.warning(f"No eligibility evaluation found with ID {evaluation_id}")
            return False
        
        evaluation.manual_review_result = manual_review_result
        evaluation.manual_review_status = 'reviewed'
        evaluation.manual_review_date = datetime.now()
        
        db.session.commit()
        
        logging.info(
            f"✅ Updated manual review for evaluation {evaluation_id}: "
            f"result={manual_review_result}"
        )
        return True
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error updating manual review for evaluation {evaluation_id}: {e}")
        return False


def get_eligibility_accuracy_stats(company_id: int = None, days_back: int = 30):
    """
    Get accuracy statistics for eligibility evaluations.
    
    Args:
        company_id (int, optional): Filter by company
        days_back (int): Number of days to look back for statistics
        
    Returns:
        dict: Statistics about AI accuracy
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = (
            db.session.query(EligibilityEvaluationLog)
            .filter(
                EligibilityEvaluationLog.evaluation_date >= cutoff_date,
                EligibilityEvaluationLog.manual_review_status == 'reviewed'
            )
        )
        
        if company_id is not None:
            query = query.filter(EligibilityEvaluationLog.company_id == company_id)
            
        evaluations = query.all()
        
        total_reviewed = len(evaluations)
        if total_reviewed == 0:
            return {
                'total_reviewed': 0,
                'accuracy': 0.0,
                'correct_predictions': 0,
                'incorrect_predictions': 0,
                'false_positives': 0,  # AI said eligible, should be not eligible
                'false_negatives': 0,  # AI said not eligible, should be eligible
                'days_back': days_back
            }
        
        # Calculate accuracy metrics
        correct_predictions = 0
        false_positives = 0
        false_negatives = 0
        
        for eval_log in evaluations:
            ai_said_eligible = eval_log.is_eligible
            manual_review_correct = eval_log.manual_review_result
            
            if manual_review_correct:
                correct_predictions += 1
            else:
                # AI was wrong - determine type of error
                if ai_said_eligible:
                    false_positives += 1  # AI said eligible but shouldn't be
                else:
                    false_negatives += 1  # AI said not eligible but should be
        
        accuracy = (correct_predictions / total_reviewed) * 100
        
        return {
            'total_reviewed': total_reviewed,
            'accuracy': round(accuracy, 2),
            'correct_predictions': correct_predictions,
            'incorrect_predictions': total_reviewed - correct_predictions,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'days_back': days_back
        }
        
    except Exception as e:
        logging.error(f"Error calculating eligibility accuracy stats: {e}")
        return {
            'total_reviewed': 0,
            'accuracy': 0.0,
            'correct_predictions': 0,
            'incorrect_predictions': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'days_back': days_back,
            'error': str(e)
        }

def update_candidate_media_verification(media_id: int, verified: bool, verification_result: dict):
    """
    Update candidate media record with verification results.
    
    Args:
        media_id (int): ID of the media record to update
        verified (bool): Whether the document was verified successfully
        verification_result (dict): Full verification result from Tu Identidad API
    """
    try:
        from baltra_sdk.legacy.dashboards_folder.models import CandidateMedia
        
        media_record = db.session.query(CandidateMedia).filter_by(media_id=media_id).first()
        
        if not media_record:
            logging.error(f"Media record with ID {media_id} not found")
            return False
        
        # Update verification fields
        media_record.verified = verified
        media_record.verification_result = verification_result
        media_record.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logging.info(f"Updated media record {media_id} with verification status: {verified}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating media verification for {media_id}: {e}")
        db.session.rollback()
        return False

def get_media_verification_status(candidate_id: int, flow_token: str = None) -> dict:
    """
    Get verification status for candidate's media files.
    
    Args:
        candidate_id (int): Candidate ID
        flow_token (str, optional): Filter by specific flow token
        
    Returns:
        dict: Verification status summary
    """
    try:
        from baltra_sdk.legacy.dashboards_folder.models import CandidateMedia
        
        query = db.session.query(CandidateMedia).filter_by(candidate_id=candidate_id)
        
        if flow_token:
            query = query.filter(CandidateMedia.flow_token.like(f'%{flow_token}%'))
        
        media_records = query.all()
        
        total_files = len(media_records)
        verified_files = sum(1 for media in media_records if media.verified)
        pending_files = total_files - verified_files
        
        return {
            'candidate_id': candidate_id,
            'total_files': total_files,
            'verified_files': verified_files,
            'pending_files': pending_files,
            'all_verified': pending_files == 0 and total_files > 0,
            'flow_token': flow_token
        }
        
    except Exception as e:
        logging.error(f"Error getting verification status for candidate {candidate_id}: {e}")
        return {
            'candidate_id': candidate_id,
            'total_files': 0,
            'verified_files': 0,
            'pending_files': 0,
            'all_verified': False,
            'error': str(e)
        }

def get_top5_locations_by_transit_company(candidate_lat: float, candidate_lon: float, *, company_group_id: int, api_key: Optional[str] = None) -> list[dict]:
    """
    Scope: finds best companies within a company group using Haversine distance only.
    1) Query DB for all companies in the group with valid lat/lon.
    2) Calculate Haversine distance for all companies.
    3) Filter companies within 35km straight-line distance.
    4) Return up to 5 closest companies, sorted by distance.
    5) If no companies within 35km, return special 'rejection' response.
    """
    # Fetch all companies in the group with lat/lon
    logging.info(f'🚀 Starting company distance search for candidate at ({candidate_lat}, {candidate_lon}), group_id={company_group_id}')
    companies = (
        db.session.query(
            CompaniesScreening.company_id,
            CompaniesScreening.name,
            CompaniesScreening.latitude,
            CompaniesScreening.longitude
        )
        .filter(
            CompaniesScreening.group_id == company_group_id,
            CompaniesScreening.latitude.isnot(None),
            CompaniesScreening.longitude.isnot(None)
        )
        .all()
    )

    if not companies:
        logging.warning(f"⚠️ No companies found for group_id={company_group_id}")
        return []
    
    logging.info(f'📍 Found {len(companies)} total companies for group')

    # convert query result to list of dicts and calculate distances
    locations_with_distance = []
    MAX_HAVERSINE_KM = 35.0
    MAX_RESULTS = 5
    
    for c in companies:
        lat = float(c.latitude)
        lng = float(c.longitude)
        distance_km = haversine_km(candidate_lat, candidate_lon, lat, lng)
        
        # Only include companies within 35km
        if distance_km <= MAX_HAVERSINE_KM:
            locations_with_distance.append({
                "company_id": c.company_id,
                "name": c.name,
                "latitude": lat,
                "longitude": lng,
                "haversine_km": distance_km,
                "eta_seconds": None,
                "distance_m": None,
            })
    
    logging.info(f"🔍 Found {len(locations_with_distance)} companies within {MAX_HAVERSINE_KM}km straight-line distance")
    
    if locations_with_distance:
        # Sort by distance and take up to 5 closest
        sorted_locations = sorted(locations_with_distance, key=lambda x: x["haversine_km"])[:MAX_RESULTS]
        
        # Log results
        logging.info(f"✅ Returning {len(sorted_locations)} companies within {MAX_HAVERSINE_KM}km:")
        for i, company in enumerate(sorted_locations, 1):
            logging.info(f"  {i}. Company {company.get('company_id')} ({company.get('name')}): {company.get('haversine_km'):.2f}km straight-line distance")
        
        return sorted_locations
    else:
        logging.warning(f"❌ No companies found within {MAX_HAVERSINE_KM}km straight-line distance")
        if company_group_id == 1:
            return [{"rejection_reason": "all_companies_too_far", "message": "Lamentablemente no contamos con vacantes a menos de 35km de tu ubicacion. \n\n Mira el siguiente link para ver nuestras ubicaciones https://linktr.ee/talentodsw 🙌"}]
        else:
            return [{"rejection_reason": "all_companies_too_far", "message": "Lamentablemente no contamos con vacantes a menos de 35km de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌"}]

def update_candidate_eligible_companies(candidate_id: int, eligible_company_ids: list) -> bool:
    """
    Update the eligible_companies JSON field for a candidate.
    
    Args:
        candidate_id (int): The candidate's ID
        eligible_company_ids (list): List of company IDs the candidate is eligible for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return False
        
        candidate.eligible_companies = eligible_company_ids
        db.session.commit()
        logging.info(f"✅ Updated eligible_companies for candidate {candidate_id}: {eligible_company_ids}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error updating eligible_companies for candidate {candidate_id}: {e}")
        db.session.rollback()
        return False

def get_candidate_eligible_companies(candidate_id: int):
    """
    Fetch the candidate's eligible companies as a list of dicts 
    with company_id, name, and address.
    
    Names are intelligently truncated to 24 characters (WhatsApp title limit)
    with word boundary detection and proper Unicode handling.
    Addresses are truncated to 72 characters (WhatsApp description limit).
    
    Supports accented characters and proper UTF-8 encoding.

    Args:
        candidate_id (int): Candidate's ID

    Returns:
        list[dict]: List of companies with 'company_id', 'name', and 'address'
    """
    try:
        candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not candidate:
            logging.warning(f"No candidate found with ID {candidate_id}")
            return []

        eligible_ids = candidate.eligible_companies or []
        if not eligible_ids:
            return []

        companies = (
            db.session.query(
                CompaniesScreening.company_id,
                CompaniesScreening.name,
                CompaniesScreening.address
            )
            .filter(CompaniesScreening.company_id.in_(eligible_ids))
            .all()
        )

        # Convert to list of dicts, truncate name >24 chars, address >72 chars
        # Handle Unicode characters properly for accented text
        result = []
        for c in companies:
            # Ensure name and address are properly encoded and handle None values
            name = c.name or ""
            address = c.address or ""
            
            try:
                import unicodedata
                name = unicodedata.normalize("NFC", name)
                address = unicodedata.normalize("NFC", address)
            except Exception:
                # If normalization is unavailable for any reason, proceed without it
                pass
            
            # Smart truncation that handles Unicode characters properly
            if len(name) > 24:
                # Reserve 1 char for ellipsis → 23 visible chars max
                visible_limit = 24
                head = name[:visible_limit]
                # Try to truncate at word boundary if possible within limit
                truncated_name = head.rsplit(' ', 1)[0] if ' ' in head else head
                truncated_name = truncated_name.rstrip() + "…"
            else:
                truncated_name = name
            
            # WhatsApp description field can handle more characters (limit ~72)
            if len(address) > 72:
                # Reserve 1 char for ellipsis → 71 visible chars max
                visible_desc_limit = 72
                head_addr = address[:visible_desc_limit]
                truncated_address = head_addr.rsplit(' ', 1)[0] if ' ' in head_addr else head_addr
                truncated_address = truncated_address.rstrip() + "…"
            else:
                truncated_address = address
            
            result.append({
                "company_id": c.company_id,
                "name": truncated_name,
                "address": truncated_address
            })
        

        logging.info(f"✅ Found {len(result)} eligible companies for candidate {candidate_id}")
        return result

    except Exception as e:
        logging.error(f"❌ Error fetching eligible companies for candidate {candidate_id}: {e}")
        return []

def store_checklist_responses(flow_data: dict, candidate_data: dict):
    """
    Stores checklist responses in the OnboardingResponse table.

    :param flow_data: The parsed JSON dictionary from the WhatsApp flow submission.
    :param candidate_data: Candidate info containing candidate_id.
    """
    try:
        survey_name = flow_data.get("survey")
        if not survey_name:
            logging.warning("No survey name found in flow_data.")
            return

        candidate_id = candidate_data.get("candidate_id")
        if not candidate_id:
            logging.warning("No candidate_id provided.")
            return

        # Iterate over all keys in flow_data except survey and flow_token
        for key, value in flow_data.items():
            if key in ["survey", "flow_token"]:
                continue
            
            # Create a new record
            record = OnboardingResponses(
                candidate_id=candidate_id,
                question=key,
                answer=value,
                survey=survey_name
            )
            db.session.add(record)

        db.session.commit()
        logging.info(f"Stored checklist responses for candidate_id {candidate_id} successfully.")

    except Exception as e:
        logging.error(f"Error storing checklist responses for candidate_id {candidate_id}: {e}")
        db.session.rollback()

def get_companies_for_group(group_id):
    """
    Fetches all companies belonging to a given group.

    Args:
        group_id (int): The group identifier.
        session (Session): SQLAlchemy session.

    Returns:
        list[dict]: [{"company_id": int, "name": str}, ...]
    """

    companies = (
        db.session.query(CompaniesScreening.company_id, CompaniesScreening.name)
        .filter(CompaniesScreening.group_id == group_id)
        .all()
    )

    return [{"company_id": c.company_id, "name": c.name} for c in companies]

def get_roles_grouped_by_company(group_id):
    """
    Fetches all active roles grouped by company for a given group.

    Args:
        group_id (int): The group identifier.

    Returns:
        dict[int, list[str]]: { company_id: ["Role 1", "Role 2", ...], ... }
    """
    # Join roles -> companies_screening, filter by group_id and active roles
    roles = (
        db.session.query(Roles.role_name, Roles.company_id)
        .join(CompaniesScreening, Roles.company_id == CompaniesScreening.company_id)
        .filter(CompaniesScreening.group_id == group_id, Roles.active == True)
        .all()
    )

    roles_by_company = {}
    for role_name, company_id in roles:
        roles_by_company.setdefault(company_id, []).append(role_name)

    return roles_by_company
