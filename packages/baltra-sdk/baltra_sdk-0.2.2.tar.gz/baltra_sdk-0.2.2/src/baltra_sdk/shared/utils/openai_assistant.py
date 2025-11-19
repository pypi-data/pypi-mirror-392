# Import necessary libraries
from openai import OpenAI, AssistantEventHandler, APITimeoutError
import re
from flask import current_app
from datetime import datetime, timedelta
from .whatsapp_messages import *
import logging
import unicodedata
from .postgreSQL_utils import store_flag, add_msg_to_db, log_response_time, get_company_9_weekly_stats, process_employee_metrics, clean_prizes
import json
from baltra_sdk.shared.utils.employee_data import Employee
import time
from typing_extensions import override

"""
This script integrates OpenAI's API with WhatsApp messaging to facilitate automated responses 
and interactions with employees. It handles message parsing, AI-generated responses, 
and predefined responses for specific inputs. 

Key functionalities:
- Retrieves and processes WhatsApp messages.
- Identifies message types (text, button, interactive, etc.).
- Interacts with OpenAI's API for AI-generated responses.
- Stores messages and responses in a PostgreSQL database.
- Manages employee data and reward redemption tracking.
- Detects specific keywords and triggers predefined responses.
- Ensures messages follow business logic, such as scheduling and validation.

"""

#get openai client with API key
def get_openai_client():
    """
    Initialize and return an OpenAI client using the API key from the app config.
    """
    client = OpenAI(api_key = current_app.config["OPENAI_KEY"]) #set client with API key
    return client

#Function to generate context for specific conversation
def get_context(conversation_type, employee_data):
    """
    Generate a context string based on the conversation type (employee or owner).
    For employee, it returns a json containing all employee data build in employee_data.py
    For owner, it has a hardcoded context that helps the recruting bot rolled out in pollos and co
    """
    if conversation_type == "employee":
        # Create a new dictionary with only the required fields
        context_data = {
            "first_name": employee_data.get("first_name", "Unknown"),
            "last_name": employee_data.get("last_name", "Unknown"), 
            "company_name": employee_data.get("company_name", "Unknown"),
            "area": employee_data.get("area", "Unknown"),
            "sub_area": employee_data.get("sub_area", "Unknown"),
            "role": employee_data.get("role", "Unknown"),
            "rewards_description": employee_data.get("rewards_description", "No rewards description"),
            "start_date": employee_data.get("start_date", "Unknown"),
            "total_points": employee_data.get("total_points", 0),
            "prizes": clean_prizes(employee_data.get("prizes", {})),
            "performance": process_employee_metrics(employee_data.get("performance", [])),
            "points_cutoff": employee_data.get("points_cutoff", []),
            "current_date": employee_data.get("current_date", (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M")),
            "redemptions": employee_data.get("redemptions", [])[-3:]
        }
        # Si la compañía es la 9, agrega las estadísticas adicionales
        if employee_data.get("company_id") == 9:
            stats = get_company_9_weekly_stats(employee_data.get("employee_id"))
            context_data.update({
                "venta_total_semana_actual": stats.get("venta_total_semana_actual", 0),
                "venta_total_semana_pasada": stats.get("venta_total_semana_pasada", 0),
                "total_tickets_semana_actual": stats.get("total_tickets_semana_actual", 0),
                "total_tickets_semana_pasada": stats.get("total_tickets_semana_pasada", 0),
                "ticket_promedio_semana_actual": stats.get("ticket_promedio_semana_actual", 0),
                "ticket_promedio_semana_pasada": stats.get("ticket_promedio_semana_pasada", 0),
                "skus_por_ticket_semana_actual": stats.get("skus_por_ticket_semana_actual", 0),
                "skus_por_ticket_semana_pasada": stats.get("skus_por_ticket_semana_pasada", 0),
                "venta_total_dia_anterior": stats.get("venta_total_dia_anterior", 0),
                "total_tickets_dia_anterior": stats.get("total_tickets_dia_anterior", 0),
                "ticket_promedio_dia_anterior": stats.get("ticket_promedio_dia_anterior", 0),
                "sku_promedio_dia_anterior": stats.get("sku_por_ticket_dia_anterior", 0),
            })
        context = json.dumps(context_data)
    elif conversation_type == "owner":
        # Get today's date
        today = datetime.now()
        
        context = (
            f"Fecha actual: {today.strftime('%Y-%m-%d')}\n"
        )
    return context

#Checks if there are active runs for a particular thread
def wait_for_free_run(client, thread_id, max_attempts=5, base_wait=2, timeout=30):
    """
    Waits until there are no active runs on a given thread.

    Args:
        client (OpenAI Client): OpenAI client instance.
        thread_id (str): Thread ID to check.
        max_attempts (int): Maximum number of retry attempts.
        base_wait (int): Base wait time in seconds (exponential backoff).
        timeout (int): Timeout for each API call in seconds.

    Returns:
        bool: True if no active runs were found after retries, False otherwise.
    """

    # Wait until no active runs are on the thread -> This loop fixes the following error 
    # openai.BadRequestError: Error code: 400 - {'error': {'message': 'Thread XX already has an active run XX.', 'type': 'invalid_request_error', 'param': None, 'code': None}}

    for attempt in range(max_attempts):
        try:
            # Add timeout and specific exception handling
            active_runs = client.beta.threads.runs.list(thread_id=thread_id, timeout=timeout)
            # Check if any run has a status indicating it's active
            is_active = any(run.status in ['active', 'queued', 'in_progress', 'cancelling'] for run in active_runs.data)

            if is_active:
                wait_time = base_wait ** attempt
                logging.warning(
                    f"[wait_for_free_run][Attempt {attempt+1}] Active run found on thread {thread_id}. "
                    f"Waiting {wait_time} seconds before retrying..."
                )
                time.sleep(wait_time)
            else:
                return True # No active runs
        except APITimeoutError:
            logging.error(f"[wait_for_free_run] Timeout error ({45}s) checking active runs for thread {thread_id} on attempt {attempt + 1}.")
            # Continue to next attempt after timeout
            if attempt < max_attempts - 1:
                 time.sleep(base_wait ** attempt) # Apply backoff before retrying after timeout
            else:
                 logging.error(f"[wait_for_free_run] All attempts failed after timeout checking runs for thread {thread_id}.")
                 return False # Failed after all attempts including timeouts
        except Exception as e:
            logging.error(f"[wait_for_free_run] Error checking active runs on attempt {attempt + 1}: {e}")
            # Decide if you want to retry on general errors or return False immediately
            # For now, let's return False on unexpected errors to avoid infinite loops on persistent issues
            return False
        except BaseException as e:
            logging.critical(f"[wait_for_free_run] Critical BaseException caught: {e} - Thread ID: {thread_id}")
            return False

    # This part is reached if max_attempts is exceeded without returning True
    logging.error(f"[wait_for_free_run] Max attempts reached waiting for thread {thread_id} to be free.")
    return False

#Helper for streaming assistant responses
class EventHandler(AssistantEventHandler):
    """
    Minimal event handler for streaming assistant responses.
    It collects text fragments (deltas) into a single string buffer,
    so you get the full message after streaming completes.
    """

    def __init__(self):
        super().__init__()
        self.full_text = ""  # Buffer to accumulate all text chunks

    @override
    def on_text_delta(self, delta, snapshot):
        # Called each time a new chunk of text is received.
        # Append the new chunk to the full_text buffer.
        self.full_text += delta.value

    # Other event hooks can be added if you want to handle special cases like tool calls.

#Run assistant in openai with streaming
def run_assistant_stream(client, employee_data):
    """
    Execute the OpenAI assistant with the provided employee data and return the full response.
    Uses streaming with a simple buffering EventHandler to accumulate the full answer.

    Args:
        client: OpenAI client instance
        employee_data: dict containing employee info and context

    Returns:
        response_text: full assistant message string
        message_id: the ID of the last assistant message
        sent_by: always "assistant"
    """
    thread_id = employee_data["thread_id"]
    context = get_context(employee_data["conversation_type"], employee_data)

    # Ensure the thread has no active runs before proceeding
    if not wait_for_free_run(client, thread_id):
        return current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "error", "assistant"

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            start_time = datetime.now()

            handler = EventHandler()
            with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=employee_data["assistant_id"],
                additional_instructions=context,
                event_handler=handler,
            ) as stream:
                stream.until_done()

            end_time = datetime.now()
            time_delta = (end_time - start_time).total_seconds()

            log_response_time(
                employee_data["employee_id"],
                employee_data["company_id"],
                start_time,
                end_time,
                time_delta,
            )

            # After streaming finishes, fetch the latest assistant message metadata
            messages = client.beta.threads.messages.list(thread_id=thread_id, timeout=30)
            # Find the most recent assistant message
            assistant_messages = [m for m in messages.data if m.role == "assistant"]
            if not assistant_messages:
                raise Exception("No assistant messages found after streaming.")
            last_message = assistant_messages[0]

            return handler.full_text, last_message.id, last_message.role

        except APITimeoutError:
            logging.warning(
                f"[run_assistant_stream] Attempt {attempt + 1}/{max_attempts} failed due to timeout."
            )
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                logging.error("[run_assistant_stream] All attempts failed due to timeout.")
                break
        except Exception as e:
            logging.warning(
                f"[run_assistant_stream] Attempt {attempt + 1}/{max_attempts} failed with error: {e}"
            )
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                logging.error("[run_assistant_stream] All attempts to run assistant failed.")
                break
        except BaseException as critical_error:
            logging.critical(
                f"[run_assistant_stream] Critical error encountered: {critical_error} - Employee ID: {employee_data['employee_id']} - Thread ID: {thread_id}"
            )
            break

    # Fallback response if all attempts fail
    return current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "error", "assistant"

# Function to add message to thread in OpenAI
def add_msg_to_thread(thread_id, message_body, role, client):
    """
    Add a message to an OpenAI thread and return message ID and sender role.
    Retries once if a failure occurs, waiting for any active runs to complete.

    Args:
        thread_id (str): OpenAI thread ID.
        message_body (str): Message received from the user or sent by the system.
        role (str): "user" or "assistant".
        client (OpenAI Client): OpenAI client instance.

    Returns:
        message_id (str): Unique identifier used by OpenAI.
        sent_by (str): Role of the sender ("user" or "assistant").
                       Returns ("error", role) on failure.
    """
    if not wait_for_free_run(client, thread_id):
        return "error", role

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Add timeout and specific exception handling for message creation
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=message_body,
                timeout=45
            )
            # Add timeout and specific exception handling for listing messages
            messages = client.beta.threads.messages.list(thread_id=thread_id, timeout=30)
            return messages.data[0].id, messages.data[0].role

        except APITimeoutError:
            logging.warning(
                 f"[add_msg_to_thread] Attempt {attempt + 1}/{max_attempts} failed due to Timeout ({45}s)."
            )
            if attempt < max_attempts - 1:
                # Ensure thread is free before retrying after timeout
                if not wait_for_free_run(client, thread_id):
                     logging.error("[add_msg_to_thread] Thread still busy after timeout, aborting retry.")
                     return "error", role # Abort if thread isn't free
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error("[add_msg_to_thread] All attempts failed after timeout.")
                break # Exit loop after final timeout
        except Exception as e:
            # Existing general exception handling
            logging.warning(
                f"[add_msg_to_thread] Attempt {attempt + 1}/{max_attempts} failed: {e}"
            )
            if attempt < max_attempts - 1:
                 # Ensure thread is free before retrying after general error
                if not wait_for_free_run(client, thread_id):
                     logging.error("[add_msg_to_thread] Thread still busy after error, aborting retry.")
                     return "error", role # Abort if thread isn't free
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error("[add_msg_to_thread] All attempts to add message failed.")
        except BaseException as critical_error:
            # Existing critical error handling
            logging.critical(
                f"[add_msg_to_thread] Critical error encountered: {critical_error} - Thread ID: {thread_id}"
            )
            # No retry. Immediately break.
            break

    # Fallback if all attempts fail
    return "error", role

#Function that gets whatsapp message Json as input and returns message type and message body
def get_message_body(message):
    """
    Determine if the given WhatsApp message is: 
    - interactive: results from a button reply to an interactive message
    - text 
    - button:  results from a template button reply,
    - nfm_reply: results from a whatsapp flow 
    - location: useful for attendance tracking
    - unkown: can be a sticker, voicenote, image, video, etc.
    
    Args: Json message from whatsapp API
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    
    Returns:
    message_body: Body of user inputed messsage as a string
    message_type: Type of message
    """
    try:
        # Check if the message type is interactive (which means the user clicked a button)
        if message["type"] == "interactive":
            if message['interactive']['type'] == "nfm_reply":
                return message["interactive"]["nfm_reply"]["response_json"], message["interactive"]["type"]
            else:
                return message["interactive"]["button_reply"]["title"], message["type"]
        
        #Check if the message has a text component
        elif message["type"] == "text":
            return message["text"]["body"], message["type"]
        #Handle template responses
        elif message["type"] == "button":
            return message["button"]["payload"], message["type"] 
        else:
            logging.error(f"Unkown message type {message['type']} for message {message}")
            return "unkown_message_type", "unkown_message_type"
    except KeyError:
        return "missing_key_error", "missing_key_error"
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return 'unknown_error', 'unknown_error'

#Generate response with all the logic included in the application
def main_flow(wa_id_user, message, wa_id_system, whatsapp_msg_id):
    """
    Processes an incoming WhatsApp message by handling message storage, AI response generation, 
    and message formatting for the WhatsApp API.

    Steps:
    1. Extracts message content and type from the WhatsApp API message.
    2. Retrieves employee data based on the sender's WhatsApp ID.
    3. Stores the user message in the OpenAI thread and database.
    4. Determines the appropriate response based on message type:
       - If the company ID is 9999, return an error message or a predefined response.
       - If it's a button or interactive message, check for hardcoded responses or trigger AI.
       - If it's a text message, check for keywords, otherwise run the AI assistant.
       - If it's a location message, acknowledge the check-in.
       - If it's an unknown type, return an error message.
    5. Logs AI-generated keywords, overwriting responses if necessary.
    6. Records prize redemptions for reward-related messages.
    7. Runs a check for flagged words in the message.
    8. Returns the formatted WhatsApp API response along with metadata.

    Args:
        wa_id_user (str): WhatsApp ID of the sender.
        message (dict): WhatsApp message payload.
        wa_id_system (str): WhatsApp ID of the receiving number (employee or owner).
        whatsapp_msg_id (str): Unique ID of the received WhatsApp message.

    Returns:
        tuple: (formatted WhatsApp message, message ID, employee data, sender type, raw response)
    """


    # Get openai client to interact with openai api
    client = get_openai_client()
    # Get incoming message type & body
    message_body, message_type = get_message_body(message)
    # Get employee data json
    employee_data = Employee(wa_id_user, client, wa_id_system).create_employee_data()
    logging.debug(f'New Employee Data: {employee_data}')

    # Append user message body to thread and get message_id and sent_by tag
    message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], message_body, "user", client)
    # Add user message to database
    add_msg_to_db(message_id, employee_data, sent_by, message_body, whatsapp_msg_id)
    
    # If user is in company_id 9999, send a hardoced message to update his phone number or contact support
    if employee_data["company_id"] == 9999:
        response, text_message_input = get_keyword_response("cambiar_numero", employee_data)
        message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    # If message_type is button returns hardcoded response
    elif message_type == "button":
        response, text_message_input = get_keyword_response(message["button"]["payload"], employee_data)
        #Handle an exception where the interactive response should trigger the ai assistant
        if response is None:
            response, message_id, sent_by = run_assistant_stream(client, employee_data)
            text_message_input = get_text_message_input(wa_id_user, response)
        #For the interactive messages where there is a hardcoded text response follow a different path
        else: 
            message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    # If message_type is interactive, returns hardcoded response or triggers the AI bot
    elif message_type == "interactive":
        response, text_message_input = get_keyword_response(message["interactive"]["button_reply"]["id"], employee_data)
        #Handle an exception where the interactive response should trigger the ai assistant
        if response is None:
            response, message_id, sent_by = run_assistant_stream(client, employee_data)
            text_message_input = get_text_message_input(wa_id_user, response)
        #For the interactive messages where there is a hardcoded text response follow a different path
        else: 
            message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    #Handle cases when a whatsapp flow was returned by the user
    elif message_type == "nfm_reply":
        response = get_nfm_reply_response(message_body, employee_data)
        message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
        text_message_input = get_text_message_input(wa_id_user, response)
    # if type is text call the openai assitant
    elif message_type == "text":
        #check if text is a keyword to return hardcoded response
        response, text_message_input = get_keyword_response(message_body, employee_data)
        #Trigger AI assistant if response is none
        if response is None:
            response, message_id, sent_by = run_assistant_stream(client, employee_data)
            #Intercept message if AI agent produced a keyword in between <> brackets
            ai_keyword = is_keyword_in_brackets(response)
            if ai_keyword and ai_keyword != 'end conversation':
                logging.info(f'AI Generated keyword <{ai_keyword}> found. Overwriting AI response with hardcoded response')
                response, text_message_input = get_keyword_response(ai_keyword, employee_data)

            else:
                text_message_input = get_text_message_input(wa_id_user, response)
        #For keywords where there is a hardcoded text response follow a different path
        else: 
            message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    elif message_type == "location":
        response = "Gracias por marcar tu llegada!"
        text_message_input = get_text_message_input(wa_id_user, response)
        message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    #If message_type is not interactive or text, return error hardcoded response
    elif message_type == "unkown_message_type":
        response = "Disculpa solo puedo entender mensajes de texto, me lo podrías repetir?"
        text_message_input = get_text_message_input(wa_id_user, response)
        message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    else:
        response = "Ocurrió un error disculpa"
        text_message_input = get_text_message_input(wa_id_user, response)
        message_id, sent_by = add_msg_to_thread(employee_data["thread_id"], response, "assistant", client)
    check_red_flags(message_body, response, client, employee_data)
    return text_message_input, message_id, employee_data, sent_by, response

#Function to check if there is a keyword wrapped in <>, function is used after ai agent generates a response
def is_keyword_in_brackets(message_body):
    """Return the text inside < > brackets if present."""
    logging.debug(f'Checking for keywords in brackets, this is the message body. {message_body}')
    match = re.search(r'<([^>]+)>', message_body)
    return match.group(1) if match else None

#Scan for red flags
def check_red_flags(message_body, response, client, employee_data):
    """
    Checks the message and response for red flags using moderation and keyword detection.
    It stores separate entries for moderation and keyword flags independently.

    Parameters:
        message_body (str): The user's message.
        response (str): The assistant's response.
        client (OpenAI client): The OpenAI client used to interact with the moderation API.
        employee_id (int or str): The ID of the employee sending the message.
        company_id (int or str): The ID of the company the employee belongs to.
        assistant_id (str, optional): Identifier for the assistant handling the conversation.

    Returns:
        None: It stores flagged objects independently if flagged by moderation or keywords.
    """

    analyze_text = f"user: {message_body} assistant: {response}"

    # Check for moderation flags
    moderation = check_moderation(analyze_text, client)
    keywords = detect_keywords(analyze_text)
    if moderation:
        logging.info(f"Moderation: {moderation}")
    if keywords:
        logging.info(f"Keywords: {keywords}")

    # If moderation flags are present, store them
    if moderation:
        # Create a formatted string for each category and its score
        flagged_info = ", ".join(f"{category}: {score:.2f}" for category, score in moderation.items())
        flag_data_moderation = {
            "assistant_id": "OpenAI Moderation",
            "employee_id": employee_data["employee_id"],
            "company_id": employee_data["company_id"],
            "action": "Moderation",
            "requested_reward": None,
            "justification": f"Moderation flagged categories: {flagged_info}"
        }
        store_flag(flag_data_moderation)  # Store the moderation flag

    # If keywords flags are present, store them
    if keywords:
        flag_data_keywords = {
            "assistant_id": "Keyword Match",
            "employee_id": employee_data["employee_id"],
            "company_id": employee_data["company_id"],
            "action": "Keyword",
            "requested_reward": None,
            "justification": f"Keywords detected: {', '.join(keywords)}"
        }
        store_flag(flag_data_keywords)  # Store the keyword flag

#Call OpenAi moderation API
def check_moderation(message, client):
    """
    Checks the moderation status of a given text and returns only the flagged categories with their scores.

    This function interacts with OpenAI's moderation API to evaluate the input message.
    It identifies and returns categories that are flagged as inappropriate by the moderation model, 
    along with their respective scores. The function can optionally apply a custom threshold 
    for flagging, but by default, it uses OpenAI's built-in threshold.

    Parameters:
        message (str): The input text to check for moderation.
        client (OpenAI client): The OpenAI client used to interact with the moderation API.

    Returns:
        dict: A dictionary of flagged categories with their respective scores.
              The categories are those that have been flagged as inappropriate by the API.
    """
    
    try:
        # Add timeout and specific exception handling for moderation call
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=message,
            timeout=30  # Added 45-second timeout
        )
    except APITimeoutError:
        logging.error(f"[check_moderation] Timeout error ({30}s) calling moderation API.")
        return {} # Return empty dict on timeout
    except Exception as e:
        # Existing general exception handling
        logging.error(f"[check_moderation] Moderation API call failed: {e}")
        return {}  # Safe fallback to prevent app crash
    
    # Uncomment to overwrite default threshold set by OpenAI (0.5) to make it more/less sensitive
    moderation_result = response.results[0]

    # Get flagged categories (categories marked as True)
    flagged_categories = {
        category: getattr(moderation_result.category_scores, category)
        for category, is_flagged in vars(moderation_result.categories).items()
        if is_flagged
    }
    
    #uncomment to overwrite the OpenAI default threshold of 0.5 to a more/less sensitive one
    #threshold = 0.1  
    #flagged_categories = {
    #    category: score
    #    for category, score in vars(response.results[0].category_scores).items()
    #    if score > threshold
    #}

    return flagged_categories

#Look for keywords to raise red flags
def detect_keywords(message):
    """
    Detects the presence of specified keywords in the given message, considering accents.

    This function efficiently checks if any of the keywords are present in the input message.
    It normalizes both the message and keywords to ensure consistent accent-insensitive matching
    and uses a regular expression for case-insensitive keyword detection.

    Parameters:
        message (str): The input message in which to search for keywords.
        keywords (set): A set of keywords to detect in the message.

    Returns:
        set: A set of detected keywords present in the message.
              If no keywords are detected, returns an empty set.
    """
    with open('app/utils/data/flagged_words.json', "r", encoding="utf-8") as file:
            keywords = set(json.load(file))

    normalized_message = ''.join(c for c in unicodedata.normalize('NFD', message) if unicodedata.category(c) != 'Mn')
    normalized_keywords = {''.join(c for c in unicodedata.normalize('NFD', keyword) if unicodedata.category(c) != 'Mn') for keyword in keywords}

    # Compile the pattern for case-insensitive matching
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, normalized_keywords)) + r')\b', re.IGNORECASE)

    # Find all matches and return them as a set of detected keywords
    matches = pattern.findall(normalized_message)
    return set(matches) if matches else {}
