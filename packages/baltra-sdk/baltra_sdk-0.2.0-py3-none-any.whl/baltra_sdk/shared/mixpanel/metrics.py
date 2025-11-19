from flask import current_app
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
import json
from baltra_sdk.shared.mixpanel.analytics import track_event
from baltra_sdk.legacy.dashboards_folder.models import (
    db, Employees, Messages, 
    Points, Sentiment, FlaggedConversations,
    WhatsappStatusUpdates
)
from baltra_sdk.shared.utils.employee_data import Employee

"""
This module is responsible for tracking various employee-related events, flagged conversations,
failed messages, and other relevant metrics, sending the data to Mixpanel for further analysis.
"""

def track_employee_events():
    """
    Query the database for employee data, calculate required properties,
    and send the `employee` event to Mixpanel.
    """
    logging.debug("Starting to track employee events.")
    
    employees = fetch_active_employees()
    if not employees:
        logging.warning("No active employees found.")
        return

    for employee in employees:
        longevity = calculate_longevity(employee.start_date)
        satisfaction = calculate_satisfaction(employee)
        requested_reward = check_requested_reward(employee)
        conversation_length = calculate_conversation_length(employee)

        max_points_didnt_redeem = check_max_points_didnt_redeem(employee)

        # Send the event to Mixpanel
        send_employee_to_mixpanel(
            employee, longevity, satisfaction, conversation_length, requested_reward, 
            max_points_didnt_redeem
        )
    
    logging.debug("Finished tracking employee events.")

def fetch_active_employees():
    """
    Fetch the data of active employees from the database.
    """
    try:
        employees = (
            db.session.query(
                Employees.employee_id,
                Employees.company_id,
                Employees.start_date,
            )
            .filter(Employees.active == True)  # Only active employees
            .all()
        )
        return employees
    except Exception as e:
        logging.error("Error querying employee data: %s", e)
        return []

def calculate_conversation_length(employee):
    """
    Classify the number of messages sent by the user in the last week into ranges:
    '<5', '5-10', '10-20', or '20+'.
    """
    try:
        one_week_ago = datetime.now() - timedelta(weeks=1)

        # Query for the number of messages sent by the user in the last 7 days
        message_count = (
            db.session.query(db.func.count(Messages.message_serial))
            .filter(
                Messages.sent_by == "user",
                Messages.employee_id == employee.employee_id,
                Messages.time_stamp >= one_week_ago
            )
            .scalar()
        )

        # Classify based on the message count
        if message_count is None:
            return "0"
        elif message_count < 5:
            return "<5"
        elif 5 <= message_count <= 10:
            return "5-10"
        elif 10 < message_count <= 20:
            return "10-20"
        else:
            return "20+"
    except Exception as e:
        logging.error("Error fetching and classifying message count for employee_id=%s: %s", employee.employee_id, e)
        return "0"

def calculate_longevity(start_date):
    """
    Calculate the longevity of an employee based on their start date.
    """
    if not start_date:
        return "unknown"

    # Convert start_date to a datetime object
    if isinstance(start_date, datetime):
        start_date_datetime = start_date
    else:
        start_date_datetime = datetime.combine(start_date, datetime.min.time())

    now = datetime.now()
    longevity_days = (now - start_date_datetime).days
    if longevity_days <= 90:
        return "0-3 months"
    elif 90 < longevity_days <= 180:
        return "3-6 months"
    elif 180 < longevity_days <= 365:
        return "6-12 months"
    elif longevity_days > 365:
        return ">12 months"
    else:
        return "unkown"

def calculate_satisfaction(employee):
    """
    Calculate employee satisfaction based on their latest sentiment scores.
    """
    try:
        latest_date = (
            db.session.query(db.func.max(Sentiment.date))
            .filter(Sentiment.employee_id == employee.employee_id)
            .scalar()
        )

        if latest_date:
            sentiment_scores = (
                db.session.query(Sentiment.score)
                .filter(
                    Sentiment.employee_id == employee.employee_id,
                    Sentiment.date == latest_date,
                )
                .all()
            )

            scores = [float(score[0]) for score in sentiment_scores if score[0]]
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > 8:
                    return "high satisfaction"
                elif 5 <= avg_score <= 8:
                    return "normal"
                else:
                    return "low satisfaction"
            else:
                return "no_answer"
    except Exception as e:
        logging.error("Error calculating satisfaction for employee_id=%s: %s", employee.employee_id, e)

    return "no_answer"

def check_requested_reward(employee):
    """
    Determine if a reward was requested based on the latest "points redeemed" transaction.
    Checks the Points table for the latest date where the transaction was "points redeemed".
    """
    try:
        # Use the current date instead of querying from the database
        latest_date = datetime.now().date()
        interval_start_date = latest_date - timedelta(weeks=1)

        # Check if there is a "points redeemed" transaction in the latest week for the employee
        transaction_found = (
            db.session.query(Points.transaction)
            .filter(
                Points.employee_id == employee.employee_id,
                Points.date >= interval_start_date,
                Points.date <= latest_date,
                Points.transaction == "points redeemed",
            )
            .first()
        )

        return "yes" if transaction_found else "no"
    
    except Exception as e:
        logging.error("Error checking requested reward for employee_id=%s: %s", employee.employee_id, e)
        return "no"  # Default to "no" in case of an error
    
def check_max_points_didnt_redeem(employee):
    """
    Check if the employee has enough points to redeem the largest reward for their company.
    """
    try:
        rewards = Employee().format_prizes_legacy(company_id=employee.company_id)
        if rewards:
            largest_reward = max(rewards, key=lambda x: x['points'])
            largest_reward_points = largest_reward['points']
            logging.debug(f"Largest Rewards: {largest_reward_points}")
        else:
            largest_reward_points = 0  # Default to 0 if no rewards exist for the company
            logging.warning("Did not find rewards")
        
        # Sum all points for the employee
        total_points = (
            db.session.query(db.func.sum(Points.points))
            .filter(Points.employee_id == employee.employee_id, Points.company_id == employee.company_id)
            .scalar() or 0
        )
        logging.debug(f'Total Points: {total_points}')
        # Check if employee points exceed the largest reward points
        if total_points >= largest_reward_points:
            return "yes"
        else:
            return "no"
    except Exception as e:
        logging.error("Error checking max points for employee_id=%s: %s", employee.employee_id, e)
        return "no"  # Default to "no" in case of an error

def send_employee_to_mixpanel(employee, longevity, satisfaction, conversation_length, requested_reward, max_points_didnt_redeem):
    """
    Send the employee event to Mixpanel with the calculated properties, including the classified number of messages.
    """
    try:
        track_event(
            distinct_id=str(employee.employee_id),  # Use employee_id as the unique identifier
            event_name="employee",
            properties={
                "company_id": employee.company_id,
                "longevity": longevity,
                "satisfaction": satisfaction,
                "conversation_length": conversation_length,
                "requested_reward": requested_reward,
                "max_points_didn't_redeem": max_points_didnt_redeem
            },
        )
        logging.debug("Successfully tracked event for employee_id=%s.", employee.employee_id)
    except Exception as e:
        logging.error("Error tracking event for employee_id=%s: %s", employee.employee_id, e)

def track_flagged_conversations():
    """
    Query the database for flagged conversations from the last 7 days,
    calculate required properties, and send the `flagged_conversation` event to Mixpanel.
    """
    logging.info("Starting to track flagged conversations.")

    recent_flagged_conversations = fetch_recent_flagged_conversations()
    if not recent_flagged_conversations:
        logging.warning("No flagged conversations found in the last 7 days.")
        return

    for conversation in recent_flagged_conversations:

        # Send the event to Mixpanel
        send_red_flag_to_mixpanel(conversation)

    logging.info("Finished tracking flagged conversations.")

def fetch_recent_flagged_conversations():
    """
    Fetch the flagged conversations from the database that were created in the last 7 days.
    """
    try:
        # Get current time in UTC
        now_utc = datetime.now(timezone.utc)
        seven_days_ago = now_utc - timedelta(weeks=1)

        # Query for flagged conversations from the last 7 days
        conversations = (
            db.session.query(
                FlaggedConversations.id,
                FlaggedConversations.employee_id,
                FlaggedConversations.company_id,
                FlaggedConversations.action,
                FlaggedConversations.assistant_id,
                FlaggedConversations.requested_reward,
                FlaggedConversations.created_at,
            )
            .filter(FlaggedConversations.created_at >= seven_days_ago)
            .all()
        )
        logging.debug("Fetched flagged conversation data successfully.")
        return conversations
    except Exception as e:
        logging.error("Error querying flagged conversation data: %s", e)
        return []

def send_red_flag_to_mixpanel(conversation):
    """
    Send the employee event to Mixpanel with the calculated properties, including the classified number of messages.
    """
    try:
        track_event(
            distinct_id=str(conversation.employee_id),  # Use employee_id as the unique identifier
            event_name="red_flag",
            properties={
                "company_id": conversation.company_id,
                "action": conversation.action,
                "assistant_id": conversation.assistant_id,
                "requested_reward": conversation.requested_reward,
                "created_at": conversation.created_at,
            },
        )
        logging.debug("Successfully tracked event for employee_id=%s.", conversation.employee_id)
    except Exception as e:
        logging.error("Error tracking event for employee_id=%s: %s", conversation.employee_id, e)

def track_failed_messages():
    """
    Query the database for failed messages from the last 7 days,
    calculate required properties, and send the `failed_message` event to Mixpanel.
    """
    logging.info("Starting to track failed messages.")
    
    failed_messages = fetch_failed_messages()
    if not failed_messages:
        logging.warning("No failed messages found in the last 7 days.")
        return

    for message in failed_messages:
        send_failed_message_to_mixpanel(message)

    logging.info(f"Successfully tracked {len(failed_messages)} failed messages.")

def fetch_failed_messages():
    """
    Fetch the failed messages from the database that occurred in the last 7 days
    and send them to Mixpanel.
    """
    try:
        now_utc = datetime.now(timezone.utc)
        seven_days_ago = now_utc - timedelta(days=7)  # Calculate the timestamp for 7 days ago

        # Query for failed messages in the last 7 days
        failed_messages = (
            db.session.query(
                WhatsappStatusUpdates.wa_id,
                WhatsappStatusUpdates.error_info,
                WhatsappStatusUpdates.status,
                WhatsappStatusUpdates.timestamp,
            )
            .filter(WhatsappStatusUpdates.timestamp >= seven_days_ago.timestamp())  # Using timestamp conversion
            .filter(or_(WhatsappStatusUpdates.status == 'failed', WhatsappStatusUpdates.status == 'rejected'))  # OR condition
            .all()
        )
        return failed_messages

    except Exception as e:
        logging.error("Error querying failed message data: %s", e)

def send_failed_message_to_mixpanel(message):
    """
    Send the failed message event to Mixpanel.
    """
    try:
        # Convert epoch timestamp to datetime
        timestamp = datetime.fromtimestamp(message.timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        error_info = message.error_info
        if isinstance(error_info, str):
            error_info = json.loads(error_info)
        # Prepare properties for Mixpanel
        properties = {
            "wa_id": message.wa_id,
            "error_info": error_info if message.error_info else {},
            "status": message.status,
            "timestamp": timestamp,  # Now it's in human-readable format
        }

        track_event(
            distinct_id=str(message.wa_id),  # Use wa_id as the unique identifier
            event_name="failed_message",
            properties=properties,
        )
        logging.debug(f"Successfully tracked failed message for wa_id={message.wa_id}")
    except Exception as e:
        logging.error(f"Error tracking failed message for wa_id={message.wa_id}: {e}")

def track_metrics(current_app):
    """
    Get all metrics with app context and track employee events, flagged conversations,
    and failed messages.
    """
    with current_app.app_context():
        logging.info("Starting metrics tracking.")
        track_employee_events()
        track_flagged_conversations()
        track_failed_messages()
        logging.info("Metrics tracking completed.")

