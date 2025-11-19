import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from baltra_sdk.shared.mixpanel.analytics import track_event
from baltra_sdk.legacy.dashboards_folder.models import db, Candidates, ScreeningMessages, CandidateReferences

def track_candidate_events():
    """
    Fetch candidates created within a date range (7 days before end_date),
    calculate required attributes, and send 'candidate' event to Mixpanel.
    Logs progress every 50 candidates.
    """
    logging.info("Starting to track candidate events.")

    end_date = datetime.now() - timedelta(hours=48)
    start_date = end_date - timedelta(hours=72)

    candidates = fetch_candidates_in_date_range(start_date, end_date)
    if not candidates:
        logging.warning("No candidates found to track in the specified date range.")
        return

    total_candidates = len(candidates)
    logging.info(f"Total candidates to process: {total_candidates}")

    processed_count = 0
    for candidate in candidates:
        conversation_length = count_candidate_messages(candidate.candidate_id)
        has_reference = check_has_reference(candidate.candidate_id)
        reference_completed = check_reference_completed(candidate.candidate_id)
        time_to_finish_conversation = get_user_message_time_delta(candidate.candidate_id)

        send_candidate_to_mixpanel(
            candidate,
            conversation_length,
            has_reference,
            reference_completed,
            time_to_finish_conversation
        )

        processed_count += 1
        if processed_count % 50 == 0:
            logging.info(f"Processed {processed_count}/{total_candidates} candidates...")

    logging.info(f"Finished tracking candidate events. Total processed: {processed_count}")


def fetch_candidates_in_date_range(start_date, end_date):
    """
    Fetch candidates created between start_date and end_date with required fields.
    """
    try:
        candidates = (
            db.session.query(
                Candidates.candidate_id,
                Candidates.company_id,
                Candidates.funnel_state,
                Candidates.rejected_reason,
                Candidates.age,
                Candidates.created_at,
                Candidates.gender,
                Candidates.travel_time_minutes,
                Candidates.grade
            )
            .filter(Candidates.created_at >= start_date)
            .filter(Candidates.created_at < end_date)
            .all()
        )
        return candidates
    except Exception as e:
        logging.error(f"Error querying candidates in date range: {e}")
        return []


def count_candidate_messages(candidate_id):
    """
    Count the number of user messages sent.
    """
    try:
        message_count = (
            db.session.query(func.count(ScreeningMessages.message_serial))
            .filter(
                ScreeningMessages.sent_by == "user",
                ScreeningMessages.candidate_id == candidate_id
            )
            .scalar()
        )
        return message_count or 0
    except Exception as e:
        logging.error(f"Error counting messages for candidate_id={candidate_id}: {e}")
        return 0


def get_user_message_time_delta(candidate_id):
    """
    Returns the time delta in seconds between the first and last user message.
    """
    try:
        timestamps = (
            db.session.query(
                func.min(ScreeningMessages.time_stamp),
                func.max(ScreeningMessages.time_stamp)
            )
            .filter(
                ScreeningMessages.sent_by == "user",
                ScreeningMessages.candidate_id == candidate_id
            )
            .first()
        )
        if timestamps[0] and timestamps[1]:
            return int((timestamps[1] - timestamps[0]).total_seconds()/60)
        return None
    except Exception as e:
        logging.error(f"Error calculating time delta for candidate_id={candidate_id}: {e}")
        return None


def check_has_reference(candidate_id):
    """
    Returns True if candidate has at least one reference.
    """
    try:
        count = (
            db.session.query(CandidateReferences)
            .filter(CandidateReferences.candidate_id == candidate_id)
            .count()
        )
        return count > 0
    except Exception as e:
        logging.error(f"Error checking references for candidate_id={candidate_id}: {e}")
        return False


def check_reference_completed(candidate_id):
    """
    Returns True if candidate has any reference marked complete.
    """
    try:
        count = (
            db.session.query(CandidateReferences)
            .filter(
                CandidateReferences.candidate_id == candidate_id,
                CandidateReferences.reference_complete == True
            )
            .count()
        )
        return count > 0
    except Exception as e:
        logging.error(f"Error checking completed references for candidate_id={candidate_id}: {e}")
        return False


def send_candidate_to_mixpanel(candidate, conversation_length, has_reference, reference_completed, time_to_finish_conversation):
    """
    Sends the candidate event to Mixpanel.
    """
    try:
        track_event(
            distinct_id=str(candidate.candidate_id),
            event_name="candidate",
            properties={
                "company_id": candidate.company_id,
                "funnel_state": candidate.funnel_state,
                "conversation_length": conversation_length,
                "has_reference?": has_reference,
                "reference_completed": reference_completed,
                "rejected_reason": candidate.rejected_reason,
                "age": candidate.age,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                "gender": candidate.gender,
                "travel_time": candidate.travel_time_minutes,
                "grade": candidate.grade,
                "time_to_finish_conversation": time_to_finish_conversation
            }
        )
        logging.debug(f"Tracked candidate event for candidate_id={candidate.candidate_id}")
    except Exception as e:
        logging.error(f"Error tracking candidate event for candidate_id={candidate.candidate_id}: {e}")

def send_funnel_state_mixpanel(candidate_id, funnel_state, company_id, reason = None):
    """
    Sends the candidate event to Mixpanel.
    """
    try:
        track_event(
            distinct_id=str(candidate_id),
            event_name=funnel_state,
            properties={
                "company_id": company_id,
                "reason": reason
            }
        )
        logging.debug(f"[Mixpanel] Tracked status event for candidate_id={candidate_id}")
    except Exception as e:
        logging.error(f"Error tracking candidate event for candidate_id={candidate_id}: {e}")


def track_metrics_screening(current_app):
    """
    Get all metrics with app context and track candidate events.
    """
    with current_app.app_context():
        logging.info("Starting screening metrics tracking.")
        track_candidate_events()
        logging.info("Screening tracking completed.")
