from flask import current_app
import logging
import json
from baltra_sdk.shared.utils.openai_assistant import get_openai_client, add_msg_to_thread
from baltra_sdk.shared.utils.whatsapp_utils import send_message
from baltra_sdk.shared.utils.whatsapp_messages import get_keyword_response
from baltra_sdk.shared.utils.postgreSQL_utils import get_scheduled_messages, get_whatsapp_ids, reschedule_message, cancel_message, get_wa_ids, get_wa_ids_owner, add_msg_to_db
from baltra_sdk.shared.utils.employee_data import Employee
from datetime import datetime, timedelta

"""
Module for scheduling and sending push messages via WhatsApp.

Functions:
- `send_scheduled_messages(current_app)`: Retrieves scheduled messages and processes them.
- `get_updated_send_time(send_time, recurring_interval)`: Calculates the next send time based on interval.
- `send_push_messages(keyword, company_id)`: Sends push messages to employees based on keyword.
- `send_push_messages_owner(keyword, company_id)`: Sends push messages to company owners.
- `send_messages(wa_ids, keyword, sender, campaign_id)`: Sends messages to specified WhatsApp IDs.
"""

#Retrieve and process scheduled messages for sending.
def send_scheduled_messages(current_app):
    """
    Retrieves scheduled messages from the database and processes them.

    Steps:
    1. Queries the `scheduled_messages` database.
    2. If no messages are scheduled, logs and exits.
    3. Iterates through each scheduled message:
       - Retrieves WhatsApp IDs based on company and parameters.
       - Logs the number of notifications to send.
       - Calculates and updates the next send time if the message is recurring.
       - Cancels scheduling if no valid interval is found.
       - Sends messages to each WhatsApp ID.
    """
    with current_app.app_context():
        #query scheduled_messages database
        scheduled_messages = get_scheduled_messages()
        # Check if there are no scheduled messages
        if not scheduled_messages:
            logging.info("No messages due for sending at this time.")
            return  # Exit the function since there's nothing to process
        #set wa_ids as an empty object
        wa_ids = []
        #Process each scheduled message
        for message in scheduled_messages:
            #unpack message tupple
            id, template, company_id, sender, parameters, send_time, recurring_interval = message
            logging.info(f"Triggering Push Messages: company_id: {company_id} - template: {template}")
            #send_time_label = send_time.strftime("%H:%M")  # Format the time to "HH:MM"
            campaign_id = f"{company_id}-{template}"
            #Get whatsapp ids based on conditions
            wa_ids = get_whatsapp_ids(company_id, parameters)
            logging.info(f'{len(wa_ids)} notifications due.')
            new_send_time = get_updated_send_time(send_time, recurring_interval)
            #reschedule message based on interval
            if new_send_time:
                reschedule_message(new_send_time, id)
            #if there is no valid interval cancel scheduling
            else:
                cancel_message(id)
            #send messages to each wa_id
            send_messages(wa_ids, template, sender, campaign_id)

#Compute the next scheduled send time based on the interval.
def get_updated_send_time(send_time, recurring_interval):
    """
    Determines the next scheduled send time based on the recurring interval.

    Args:
        send_time (datetime): The original send time.
        recurring_interval (str): The interval type (daily, weekly, monthly).

    Returns:
        datetime or bool: The new send time if valid, otherwise False.
    """
    if recurring_interval == "weekly":
        new_send_time = send_time + timedelta(weeks=1)
    elif recurring_interval == "daily":
        new_send_time = send_time + timedelta(days=1)
    elif recurring_interval == "monthly":
        new_send_time = send_time + timedelta(weeks=4)  # Approximation for a month
    else:
        logging.warning(f"Not a valid recurring interval : {recurring_interval}\n Set Status as canceled")
        new_send_time = False
    return new_send_time

#Send push messages to employees using a predefined keyword.
def send_push_messages(keyword, company_id):
    """
    Sends push messages to employees in a company based on a given keyword.

    Args:
        keyword (str): The message keyword.
        company_id (int): The company ID.

    """
    logging.info("Triggering notifications")
    #get whatsapp ids
    wa_ids = get_wa_ids(company_id)
    logging.info(f'{len(wa_ids)} notifications due.')
    send_time = datetime.now().strftime("%H:%M")
    campaign_id = f"{company_id}-{keyword}"
    send_messages(wa_ids, keyword, 'wa_id_ID_employee', campaign_id)

#Send push messages to company owners using a predefined keyword.
def send_push_messages_owner(keyword, company_id):
    """
    Sends push messages to company owners based on a given keyword.

    Args:
        keyword (str): The message keyword.
        company_id (int): The company ID.

    Logs:
        - The number of notifications sent.
    """
    logging.info("Triggering notifications")
    #get whatsapp ids
    wa_ids = get_wa_ids_owner(company_id)
    logging.info(f'{len(wa_ids)} notifications due.')
    send_time = datetime.now().strftime("%H:%M")
    campaign_id = f"{company_id}-{keyword}"
    send_messages(wa_ids, keyword, 'wa_id_ID_employee', campaign_id)

#Send WhatsApp messages to a list of recipients.
def send_messages(wa_ids, keyword, sender, campaign_id= None):
    """
    Sends WhatsApp messages to a list of recipients.

    Args:
        wa_ids (list): List of WhatsApp IDs.
        keyword (str): The message keyword.
        sender (str): The sender ID.
        campaign_id (str, optional): The campaign identifier.

    Steps:
    1. Initializes OpenAI client.
    2. Iterates through each recipient:
       - Fetches employee data.
       - Gets a response based on the keyword.
       - Sends the message.
       - Stores the message in the database if successful.
    """
    client = get_openai_client()
    for wa_id in wa_ids:
        employee_data = Employee(wa_id, client, current_app.config[sender]).create_employee_data()
        text, message_data = get_keyword_response(keyword, employee_data)
        status_response = send_message(message_data, current_app.config[sender], campaign_id)
        try:  
            if status_response.status_code == 200:
                response_text = json.loads(status_response.text)
                whatsapp_msg_id = response_text['messages'][0]['id']
                message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], text, "assistant", client)
                #Store in messages table
                add_msg_to_db(message_id, employee_data, sent_by, text, whatsapp_msg_id)

        except AttributeError as e:
            logging.error(f"An AttributeError occurred: {e}")
    logging.info(f'Successfully sent {len(wa_ids)} messages.')


