from flask import current_app
from .sql_utils import (
    get_candidates_to_remind,
    get_company_wa_id,
    store_message,
    get_candidates_to_remind_application,
    log_funnel_state_change,
    update_funnel_state,
)
from baltra_sdk.legacy.dashboards_folder.models import db, Candidates, CompaniesScreening, CandidateFunnelLog
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast, literal_column
from .whatsapp_messages import get_keyword_response_from_db
from .candidate_data import CandidateDataFetcher
from .openai_utils import add_msg_to_thread, get_openai_client
from .whatsapp_utils import send_message
import logging
import json
from datetime import datetime, timedelta, time
import pytz



#Reminders to finish flow
def send_application_reminders(current_app):
    with current_app.app_context():
        candidates_to_remind = get_candidates_to_remind_application()

        for candidate in candidates_to_remind:
            try:
                wa_id_system = get_company_wa_id(candidate.company_id)
                if not wa_id_system:
                    logging.warning(f"No wa_id found for company_id {candidate.company_id}, skipping candidate {candidate.candidate_id}")
                    continue

                candidate_data = CandidateDataFetcher(candidate.phone, get_openai_client(), wa_id_system).get_data()

                text, formatted_response = get_keyword_response_from_db(
                    session=db.session,
                    keyword="application_reminder",  # make sure this template exists
                    candidate_data=candidate_data,
                )

                message_id, sent_by = add_msg_to_thread(candidate_data['thread_id'], text, "assistant", get_openai_client())

                status_response = send_message(formatted_response, wa_id_system, "application_reminder")
                if status_response.status_code == 200:
                    try:
                        response_text = json.loads(status_response.text)
                        whatsapp_msg_id = response_text['messages'][0]['id']
                        store_message(message_id, candidate_data, sent_by, text, whatsapp_msg_id)
                        logging.info(f"Application Reminder sent to candidate_id {candidate_data['candidate_id']}")
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logging.error(f"Error parsing WhatsApp response or storing message for candidate_id {candidate_data['candidate_id']}: {e}")

                candidate.application_reminder_sent = True
                db.session.commit()

            except Exception as e:
                logging.error(f"❌ Error sending application reminder to {candidate.phone}: {e}")

#Send message template to specific candidate
def send_message_template_to_candidate(template_keyword, candidate_id, current_app):
    """
    Send a message template to a specific candidate using their candidate_id.
    
    Args:
        template_keyword (str): The keyword/name of the message template to send
        candidate_id (int): The ID of the candidate to send the message to
        current_app: Flask application context
    """
    with current_app.app_context():
        try:
            # Get candidate from database
            candidate = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
            if not candidate:
                logging.error(f"No candidate found with candidate_id {candidate_id}")
                return False
            
            # Get company's WhatsApp ID
            wa_id_system = get_company_wa_id(candidate.company_id)
            if not wa_id_system:
                logging.error(f"No wa_id found for company_id {candidate.company_id}")
                return False
            
            # Get candidate data in the proper format
            candidate_data = CandidateDataFetcher(candidate.phone, get_openai_client(), wa_id_system).get_data()
            if not candidate_data:
                logging.error(f"Could not fetch candidate data for candidate_id {candidate_id}")
                return False
            
            # Add comprehensive debugging for candidate_data
            logging.info(f"DEBUG: Processing template '{template_keyword}' for candidate {candidate_id}")
            logging.info(f"DEBUG: candidate_data keys: {list(candidate_data.keys()) if candidate_data else 'None'}")
            
            # Check required fields for interview reminder template specifically
            if template_keyword == "interview_reminder":
                required_fields = ["role", "company_name", "interview_date", "interview_address"]
                missing_fields = []
                empty_fields = []
                
                logging.info(f"DEBUG: Checking required fields for interview_reminder template")
                for field in required_fields:
                    value = candidate_data.get(field)
                    logging.info(f"DEBUG: Field '{field}' = '{value}' (type: {type(value)})")
                    
                    if value is None:
                        missing_fields.append(field)
                    elif value == "":
                        empty_fields.append(field)
                
                if missing_fields:
                    logging.warning(f"Missing (None) fields for candidate {candidate_id}: {missing_fields}")
                if empty_fields:
                    logging.warning(f"Empty string fields for candidate {candidate_id}: {empty_fields}")
            
            # Also log general candidate data for context
            logging.info(f"DEBUG: candidate basic info - name: '{candidate_data.get('first_name')}', company: '{candidate_data.get('company_name')}', phone: '{candidate_data.get('wa_id')}'")
            
            # Get the message template from the database
            logging.info(f"DEBUG: About to call get_keyword_response_from_db with keyword '{template_keyword}'")
            text, formatted_response = get_keyword_response_from_db(
                session=db.session,
                keyword=template_keyword,
                candidate_data=candidate_data,
            )
            
            logging.info(f"DEBUG: get_keyword_response_from_db returned - text: {text is not None}, formatted_response: {formatted_response is not None}")
            if formatted_response:
                logging.info(f"DEBUG: formatted_response length: {len(formatted_response)}")
                # Log first 500 characters to see the structure without overwhelming logs
                logging.info(f"DEBUG: formatted_response preview: {formatted_response}")
            
            if not text or not formatted_response:
                logging.error(f"No message template found for keyword '{template_keyword}' or formatting failed")
                return False
            
            # Add message to OpenAI thread
            message_id, sent_by = add_msg_to_thread(candidate_data['thread_id'], text, "assistant", get_openai_client())
            
            # Send the message via WhatsApp
            status_response = send_message(formatted_response, wa_id_system, template_keyword)
            
            if status_response and status_response.status_code == 200:
                try:
                    response_text = json.loads(status_response.text)
                    whatsapp_msg_id = response_text['messages'][0]['id']
                    store_message(message_id, candidate_data, sent_by, text, whatsapp_msg_id)
                    logging.info(f"Message template '{template_keyword}' sent successfully to candidate_id {candidate_id}")

                    # If this is the FIRST onboarding message, move candidate to 'onboarding'
                    try:
                        tk = (template_keyword or '').strip().lower()
                        if tk.startswith('onboarding') and (candidate.funnel_state or '').lower() != 'onboarding':
                            previous_state = candidate.funnel_state
                            # Log funnel change and update candidate state
                            log_funnel_state_change(candidate.candidate_id, previous_state, 'onboarding')
                            candidate.funnel_state = 'onboarding'
                            db.session.commit()
                            logging.info(f"Candidate {candidate_id} moved to 'onboarding' (prev='{previous_state}') after onboarding message '{template_keyword}'")
                        # If this is the phone interview template, move candidate to 'phone_interview_cited'
                        elif tk == 'phone_interview_cemex' and (candidate.funnel_state or '').lower() != 'phone_interview_cited':
                            previous_state = candidate.funnel_state
                            # Update funnel state using the proper function (which also logs the change)
                            success = update_funnel_state(candidate.candidate_id, 'phone_interview_cited')
                            if success:
                                logging.info(f"✅ Candidate {candidate_id} moved to 'phone_interview_cited' (prev='{previous_state}') after phone interview template '{template_keyword}'")
                            else:
                                logging.error(f"❌ Failed to update funnel state for candidate {candidate_id} to 'phone_interview_cited'")
                    except Exception as e:
                        # Do not fail the message send flow if funnel update fails
                        logging.warning(f"Could not update funnel_state for candidate {candidate_id}: {e}")
                    return True
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logging.error(f"Error parsing WhatsApp response for candidate_id {candidate_id}: {e}")
                    return False
            else:
                logging.error(f"Failed to send message to candidate_id {candidate_id}. Status code: {status_response.status_code if status_response else 'None'}")
                return False
           
        except Exception as e:
            logging.error(f"❌ Error sending message template '{template_keyword}' to candidate_id {candidate_id}: {e}")
            return False


# NEW FLEXIBLE REMINDER SYSTEM
def send_flexible_interview_reminders(current_app):
    """
    Send interview reminders based on each company's reminder_schedule configuration.
    Supports both 'fixed' (daily at specific time) and 'flexible' (hours before interview) schedules.
    """
    with current_app.app_context():
        try:
            # Get all companies with their reminder schedules
            companies = db.session.query(CompaniesScreening).filter(
                CompaniesScreening.reminder_schedule.isnot(None),
                cast(CompaniesScreening.reminder_schedule, JSONB) != literal_column("'{}'::jsonb")
            ).all()
            
            mexico_tz = pytz.timezone('America/Mexico_City')
            utc_now = datetime.now(pytz.UTC)
            mexico_now = utc_now.astimezone(mexico_tz)
            
            for company in companies:
                reminder_config = company.reminder_schedule
                if not reminder_config:
                    continue
                    
                reminder_type = reminder_config.get('type')
                
                if reminder_type == 'fixed':
                    # Process fixed schedule reminders
                    _process_fixed_schedule_reminders(company, reminder_config, mexico_now)
                    
                elif reminder_type == 'flexible':
                    # Process flexible schedule reminders (hours before interview)
                    _process_flexible_schedule_reminders(company, reminder_config, utc_now)
                    
                else:
                    logging.warning(f"Unknown reminder type '{reminder_type}' for company {company.company_id}")
                    
        except Exception as e:
            logging.error(f"❌ Error in send_flexible_interview_reminders: {e}")


def _process_fixed_schedule_reminders(company, reminder_config, current_mexico_time):
    """
    Process fixed schedule reminders for a company.
    Sends reminders at a specific time each day for interviews on a target day.
    """
    try:
        schedule_time_str = reminder_config.get('time')  # e.g., "20:00" or "06:30"
        when = reminder_config.get('when', 'night_before')  # 'night_before' or 'morning_of'
        
        if not schedule_time_str:
            logging.warning(f"No time specified in fixed schedule for company {company.company_id}")
            return
            
        # Parse the scheduled time
        schedule_hour, schedule_minute = map(int, schedule_time_str.split(':'))
        schedule_time = time(schedule_hour, schedule_minute)
        
        # Check if we're within the sending window (±10 minutes of scheduled time)
        current_time = current_mexico_time.time()
        time_diff = _time_difference_minutes(current_time, schedule_time)
        
        if abs(time_diff) <= 10:  # Within 10 minutes of scheduled time
            # Determine which day's interviews to remind about
            if when == 'night_before':
                target_date = (current_mexico_time + timedelta(days=1)).date()
            else:  # morning_of
                target_date = current_mexico_time.date()
                
            # Get candidates for this company and target date
            candidates = _get_candidates_for_fixed_schedule(company.company_id, target_date)
            
            # Send reminders to all candidates
            for candidate in candidates:
                _send_individual_reminder(candidate, company.company_id)
                
            if candidates:
                when_text = "night before" if when == 'night_before' else "morning of"
                logging.info(f"Sent {len(candidates)} fixed schedule reminders for company {company.company_id} ({when_text} at {schedule_time_str})")
                
    except Exception as e:
        logging.error(f"❌ Error processing fixed schedule for company {company.company_id}: {e}")


def _process_flexible_schedule_reminders(company, reminder_config, current_utc_time):
    """
    Process flexible schedule reminders for a company.
    Sends reminders a specific number of hours before each interview.
    """
    try:
        hours_before = reminder_config.get('hours_before', 3)
        
        # Convert UTC time to Mexico local time (interview_date_time is stored in Mexico local time)
        mexico_now = current_utc_time - timedelta(hours=6)  # Mexico is UTC-6
        
        # Calculate the time window for interviews that need reminders now (in Mexico local time)
        reminder_time_start = mexico_now + timedelta(hours=hours_before - 0.17)  # 10 minute window
        reminder_time_end = mexico_now + timedelta(hours=hours_before + 0.17)
        
        # Get candidates whose interviews are in this time window
        candidates = _get_candidates_for_flexible_schedule(
            company.company_id, 
            reminder_time_start, 
            reminder_time_end
        )
        
        # Send reminders to these candidates
        for candidate in candidates:
            _send_individual_reminder(candidate, company.company_id)
            
        if candidates:
            logging.info(f"Sent {len(candidates)} flexible schedule reminders for company {company.company_id} ({hours_before} hours before interviews)")
            
    except Exception as e:
        logging.error(f"❌ Error processing flexible schedule for company {company.company_id}: {e}")


def _get_candidates_for_fixed_schedule(company_id, target_date):
    """
    Get candidates for fixed schedule reminders on a specific date.
    """
    # Build datetime range for the target date (in local time)
    start_time = datetime.combine(target_date, time.min)
    end_time = datetime.combine(target_date, time.max)
    
    return db.session.query(Candidates).filter(
        Candidates.company_id == company_id,
        Candidates.interview_date_time >= start_time,
        Candidates.interview_date_time <= end_time,
        Candidates.interview_reminder_sent == False,
        Candidates.funnel_state == "scheduled_interview",
        Candidates.phone.isnot(None)
    ).all()


def _get_candidates_for_flexible_schedule(company_id, start_time, end_time):
    """
    Get candidates for flexible schedule reminders within a time window.
    """
    return db.session.query(Candidates).filter(
        Candidates.company_id == company_id,
        Candidates.interview_date_time >= start_time,
        Candidates.interview_date_time <= end_time,
        Candidates.interview_reminder_sent == False,
        Candidates.funnel_state == "scheduled_interview",
        Candidates.phone.isnot(None)
    ).all()


def _send_individual_reminder(candidate, company_id):
    """
    Send an individual reminder to a candidate.
    This is the core reminder sending logic extracted for reuse.
    """
    try:
        wa_id_system = get_company_wa_id(company_id)
        if not wa_id_system:
            logging.warning(f"No wa_id found for company_id {company_id}, skipping candidate {candidate.candidate_id}")
            return False

        candidate_data = CandidateDataFetcher(candidate.phone, get_openai_client(), wa_id_system).get_data()

        # Validate required fields for interview reminder template
        required_fields = ["role", "company_name", "interview_date", "interview_address"]
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            value = candidate_data.get(field)
            if value is None:
                missing_fields.append(field)
            elif value == "":
                empty_fields.append(field)
        
        if missing_fields:
            logging.warning(f"Missing (None) fields for candidate {candidate.candidate_id}: {missing_fields}")
        if empty_fields:
            logging.warning(f"Empty string fields for candidate {candidate.candidate_id}: {empty_fields}")

        text, formatted_response = get_keyword_response_from_db(
            session=db.session,
            keyword="interview_reminder",
            candidate_data=candidate_data,
        )

        if not text or not formatted_response:
            logging.error(f"No message template found for interview_reminder or formatting failed for candidate {candidate.candidate_id}")
            return False

        message_id, sent_by = add_msg_to_thread(candidate_data['thread_id'], text, "assistant", get_openai_client())

        status_response = send_message(formatted_response, wa_id_system, "interview_reminder")
        if status_response and status_response.status_code == 200:
            try:
                response_text = json.loads(status_response.text)
                whatsapp_msg_id = response_text['messages'][0]['id']
                store_message(message_id, candidate_data, sent_by, text, whatsapp_msg_id)
                
                # Mark reminder as sent
                candidate.interview_reminder_sent = True
                db.session.commit()
                
                logging.info(f"Flexible Interview Reminder sent to candidate_id {candidate_data['candidate_id']} (company_id: {company_id})")
                return True
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logging.error(f"Error parsing WhatsApp response or storing message for candidate_id {candidate_data['candidate_id']}: {e}")
                return False
        else:
            logging.error(f"Failed to send reminder to candidate_id {candidate.candidate_id}. Status code: {status_response.status_code if status_response else 'None'}")
            return False

    except Exception as e:
        logging.error(f"❌ Error sending reminder to candidate {candidate.candidate_id}: {e}")
        return False


def _time_difference_minutes(time1, time2):
    """
    Calculate difference in minutes between two time objects.
    Returns positive if time1 is after time2, negative if before.
    """
    dt1 = datetime.combine(datetime.today(), time1)
    dt2 = datetime.combine(datetime.today(), time2)
    return (dt1 - dt2).total_seconds() / 60
