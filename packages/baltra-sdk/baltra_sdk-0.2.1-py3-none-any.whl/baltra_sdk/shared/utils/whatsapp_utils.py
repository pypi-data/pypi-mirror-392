import logging
from flask import current_app
from .openai_assistant import main_flow
from .postgreSQL_utils import store_sent_message, store_rejected_message, add_msg_to_db, delete_temp_database
from .screening.screening_flow import screening_flow, store_message, store_message_reference
import requests
from datetime import datetime, timedelta
import json

"""
This module handles the processing and sending of WhatsApp messages using the WhatsApp API.

Key functionalities:
- Sending messages via the WhatsApp API (`send_message`)
- Processing incoming WhatsApp messages (`process_whatsapp_message`)
- Validating the structure of incoming messages (`is_valid_whatsapp_message`)
- Filtering out old messages to prevent redundant processing (`should_run_app`)
- Concatenating multiple message bodies from a temporary database (`concatenate_message_bodies`)

It integrates with:
- OpenAI assistant for generating responses (`main_flow`)
- PostgreSQL utilities for storing message logs (`store_sent_message`, `store_rejected_message`, `add_msg_to_db`)
"""

def get_account_config(wa_id_system):
    """
    All wa_id numbers now use the same primary account configuration
    Returns: dict with access_token, app_secret, and account_type
    """
    return {
        "access_token": current_app.config["ACCESS_TOKEN"],
        "app_secret": current_app.config["META_APP_SECRET"], 
        "account_type": "PRIMARY",
        "version": current_app.config["VERSION"]
    }

#Configure http logging
def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

#Takes json formated for whatsapp API and sends it via the API
def send_message(data, sender, campaign_id = None):
    """
    objective: Send a whatsapp message
    args: 
        Data: Json object formated for whatsapp with information of outbound message
        Sender: whastapp id of the sender number to be used 
    """
    # Validate input data
    if data is None:
        logging.error(f"Cannot send message: data parameter is None for sender {sender}")
        return None
    
    # Get account configuration based on sender wa_id
    account_config = get_account_config(sender)
    if not account_config:
        logging.error(f"[Account: UNKNOWN] Could not determine account configuration for sender: {sender}")
        return None
    
    payload = data
    if isinstance(payload, (dict, list)):
        payload = json.dumps(payload, ensure_ascii=False)

    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {account_config['access_token']}",
    }

    url = f"https://graph.facebook.com/{account_config['version']}/{sender}/messages"
    
    try:
        logging.debug(f'[Account: {account_config["account_type"]}] Whatsapp Message Structure: {data}')
        response = requests.post(
            url, data=data, headers=headers, timeout=30
        )  # 30 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error(f"[Account: {account_config['account_type']}] Timeout occurred while sending message")
        log_http_response(response)
        return response
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"[Account: {account_config['account_type']}] Request failed due to: {e} - Response: {response.text}")
        log_http_response(response)
        
        # Safely extract wa_id from data for logging and storage
        try:
            wa_id = json.loads(data)["to"] if data else "unknown"
        except (json.JSONDecodeError, TypeError, KeyError):
            wa_id = "unknown"
            
        logging.info(f'[Account: {account_config["account_type"]}] Storing rejected message for wa_id {wa_id}')
        store_rejected_message(response, campaign_id, wa_id)
        return response
    else:
        # Process the response as normal
        log_http_response(response)
        store_sent_message(response, campaign_id)
        
        # Safely extract wa_id from data for logging
        try:
            wa_id = json.loads(data)["to"] if data else "unknown"
        except (json.JSONDecodeError, TypeError, KeyError):
            wa_id = "unknown"
            
        logging.info(f'[Account: {account_config["account_type"]}] Message sent successfully to wa_id {wa_id}')
        return response

#Extracts the wa_id and message from the json, gets a response and sends message 
def process_whatsapp_message(body, app_context):
    """
    Processes an incoming WhatsApp message by extracting relevant details, generating a response, and sending a reply.

    New routing logic:
    - If wa_id_system == wa_id_ID_employee: routes to main_flow() (existing employee flow)
    - All other wa_id_system: routes to screening_flow() (company screening numbers)

    Steps:
    1. Extracts the message object from the incoming JSON payload.
    2. Checks if the message is new using `should_run_app` to prevent processing old messages.
    3. Extracts the sender's WhatsApp ID (`wa_id_user`) and the system's WhatsApp ID (`wa_id_system`).
    4. Routes to appropriate flow based on wa_id_system.
    5. Calls appropriate flow to generate a response message.
    6. Checks if the generated response contains the "<end conversation>" keyword to avoid unnecessary replies.
    7. If the response is valid, sends the message using `send_message`.
    8. If successful, logs the sent message details in the database.

    Args:
        body (dict): JSON payload received from the WhatsApp webhook.

    Returns:
        None
    """
    with app_context:

        #get the message object, a json with the information of the message
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]    
        #Check if the timestamp is from a new or old message, this solves the random message sending bug
        run = should_run_app(message["timestamp"])
        if run:
            #get whatsapp id of the user/sender (should be his phone number)
            wa_id_user = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            #get whatsapp id of the number that was contacted, this is not a phone number but a whatsapp identifier 
            wa_id_system = body["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
            #get whatsapp id
            whatsapp_msg_id =  body["entry"][0]["changes"][0]["value"]["messages"][0] ['id']
            
            # Get account configuration (now all wa_id use the same primary account)
            account_config = get_account_config(wa_id_system)
            
            # Route based on wa_id_system: employee flow vs screening flow
            if wa_id_system == current_app.config.get("wa_id_ID_employee"):
                logging.info(f"[Account: {account_config['account_type']}] Processing employee message through main_flow")
                #get Json formated to be sent via whatsapp + parameters for database
                data, message_id, employee_data, sent_by, text= main_flow(wa_id_user, message, wa_id_system, whatsapp_msg_id)
                #check if text contains keyword to kill conversation
                if "<end conversation>" in text: 
                    logging.info(f"[Account: {account_config['account_type']}] Keyword '<end conversation>' found: Won't send an answer")
                else:
                    #Send message
                    status_response = send_message(data, wa_id_system)            
                    #extract whatsapp_id of the message generated
                    try: 
                        if status_response and status_response.status_code == 200:
                            response_text = json.loads(status_response.text)
                            whatsapp_msg_id = response_text['messages'][0]['id']
                            #Store in messages table
                            add_msg_to_db(message_id, employee_data, sent_by, text, whatsapp_msg_id)
                    except AttributeError as e:
                        logging.error(f"[Account: {account_config['account_type']}] An AttributeError occurred: {e}")
            else:
                _handle_screening_branch(body, account_config, wa_id_user, wa_id_system, message, whatsapp_msg_id)
        #delete_temp_database(body)


def _handle_screening_branch(body, account_config, wa_id_user, wa_id_system, message, whatsapp_msg_id):
    logging.info(f"[Account: {account_config['account_type']}] Processing screening message through legacy screening_flow for wa_id: {wa_id_system}")
    data, message_id, candidate_data, sent_by, text = screening_flow(wa_id_user, message, wa_id_system, whatsapp_msg_id)
    if "<end conversation>" in text:
        logging.info(f"[Account: {account_config['account_type']}] Keyword '<end conversation>' found: Won't send an answer")
        return
    status_response = send_message(data, wa_id_system)
    try:
        if status_response and status_response.status_code == 200:
            response_text = json.loads(status_response.text)
            outbound_id = response_text["messages"][0]["id"]
            if 'reference_id' in candidate_data:
                store_message_reference(message_id, candidate_data, sent_by, text, outbound_id)
            else:
                store_message(message_id, candidate_data, sent_by, text, outbound_id)
    except AttributeError as error:
        logging.error(f"[Account: {account_config['account_type']}] Error storing legacy screening message: {error}")


#Check if the event has a valid whatsapp structure
def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

#Evaluates if the app should run or not based on when the message was sent, solves random message bug
def should_run_app(timestamp: str) -> bool:
    """
    Determines whether the app should process an incoming message based on its timestamp.

    Steps:
    1. Converts the provided timestamp into a `datetime` object.
    2. Computes the time difference between the current time and the message timestamp.
    3. Compares the time difference against a predefined cutoff time (`OLD_MESSAGE_CUTOFF`) from the app's config.
    4. If the message is older than the cutoff, it is ignored to prevent processing outdated messages.
    5. Logs the decision and returns a boolean indicating whether the message should be processed.

    Args:
        timestamp (str): The Unix timestamp (in seconds) of the incoming message.

    Returns:
        bool: True if the message is recent and should be processed, False otherwise.
    """
    # Calculate the time difference
    time_difference = datetime.now() - datetime.fromtimestamp(int(timestamp))
    # Check if the difference is more than the CUTOFF time hardcoded in config
    if time_difference > timedelta(minutes=current_app.config["OLD_MESSAGE_CUTOFF"]):
        logging.warning(f"Old Message sent at {timestamp}, will not generate response")
        return False  # Do not run the app
    else:
        logging.info(f"New message sent at {timestamp}, generating response")
        return True  # Run the app


#Concatenates all message bodies found in the temporary messages database. Used by response lag
def concatenate_message_bodies(messages):
    """
    Concatenates all message bodies found in the temporary messages database. It is only used by response lag function
    Whenever many messages are sent they're all concatenated and a single response is triggered

    Steps:
    1. Iterates through a list of message tuples, extracting the message body from each.
    2. Concatenates all extracted message bodies into a single string, separating them with spaces.
    3. Uses the last message in the list as the base structure for the final JSON.
    4. Updates the last message's text body with the concatenated message.
    5. Returns the updated JSON object containing the concatenated message.

    Args:
        messages (list of tuples): Each tuple contains message-related data, with the JSON body at index 3.

    Returns:
        dict: A JSON object representing the last message with an updated text body containing all concatenated messages.
    """

    # Initialize an empty list to collect message bodies
    concatenated_body = ""
    # Iterate over each tuple to concatenate message bodies
    for message in messages:
        # Load the JSON body
        body = message[3]

        # Extract and concatenate the message body
        message_body = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        concatenated_body += message_body + " "  # Add a space between messages
    # Use the data from the last tuple for static fields
    last_message = messages[-1]

    # Load the JSON body of the last tuple
    last_body = last_message[3]

    # Update the text body with concatenated messages
    last_body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = concatenated_body.strip()  # Remove trailing space
    return last_body
