from flask import current_app
import requests
import logging
import json
from datetime import datetime
from .sql_utils import (
    get_company_location_info, 
    update_candidate_interview_address_and_link, 
    store_checklist_responses, update_funnel_state, add_interview_date_time,
    get_company_additional_info, is_slot_available, get_company_screening_data
)

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
        
        # Safely extract wa_id from data for logging
        try:
            wa_id = json.loads(data)["to"] if data else "unknown"
        except (json.JSONDecodeError, TypeError, KeyError):
            wa_id = "unknown"
        
        logging.info(f'[Account: {account_config["account_type"]}] Storing rejected message for wa_id {wa_id}')
        return response
    else:
        # Process the response as normal
        log_http_response(response)
        
        # Safely extract wa_id from data for logging
        try:
            wa_id = json.loads(data)["to"] if data else "unknown"
        except (json.JSONDecodeError, TypeError, KeyError):
            wa_id = "unknown"
        
        logging.info(f'[Account: {account_config["account_type"]}] Message sent successfully to wa_id {wa_id}')
        return response

def send_typing_indicator(sender: str, whatsapp_msg_id: str):
    """
    Sends a "read" receipt + "typing" indicator back to WhatsApp Cloud API.
    Params:
      - phone_id: your WhatsApp Business Phone Number ID (the sender ID)
      - whatsapp_msg_id: the 'id' from the incoming webhook message payload
    """
    account_config = get_account_config(sender)
    url = f"https://graph.facebook.com/{account_config['version']}/{sender}/messages"
    headers = {
        "Authorization": f"Bearer {account_config['access_token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": whatsapp_msg_id,
        "typing_indicator": { "type": "text" }
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logging.info(f"Sent typing indicator for msg {whatsapp_msg_id}")
    except Exception as e:
        logging.error(f"Failed to send typing indicator: {e}, response: {getattr(resp, 'text', None)}")
        # Optionally store or alert this error


def upload_media_to_meta(audio_bytes: bytes, mime_type="audio/mpeg", meta_id: str = None) -> str:
    # Get account configuration based on meta_id
    account_config = get_account_config(meta_id)
    if not account_config:
        logging.error(f"[Account: UNKNOWN] Could not determine account configuration for meta_id: {meta_id}")
        return None
    
    url = f"https://graph.facebook.com/v22.0/{meta_id}/media"
    files = {
        "file": ("voice.wav", audio_bytes, mime_type),
        "type": (None, mime_type),
        "messaging_product": (None, "whatsapp"),
    }
    headers = {
        "Authorization": f"Bearer {account_config['access_token']}",
    }
    response = requests.post(url, files=files, headers=headers)
    if response.status_code != 200:
        logging.error(f"[Account: {account_config['account_type']}] Error uploading media to Meta: {response.text}")
        raise ValueError(f"Error uploading media to Meta")
    return response.json()["id"]
  
  
def get_media_url(media_id: str) -> str:
    """
    Get media URL using primary account configuration
    """
    url = f"https://graph.facebook.com/v23.0/{media_id}"
    
    headers = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"[Account: PRIMARY] Successfully retrieved media URL for media_id: {media_id}")
        return response.json()["url"]
    
    logging.error(f"[Account: PRIMARY] Error getting media URL for media_id {media_id}: {response.text}")
    raise ValueError(f"Error getting media URL")
  
def download_audio_file_from_meta(download_url: str) -> bytes:
    """
    Download audio file using primary account configuration
    """
    headers = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        logging.info(f"[Account: PRIMARY] Successfully downloaded audio file from URL")
        content_type = response.headers["Content-Type"]
        
        content_type_to_ext = {
          "audio/wav": ".wav",
          "audio/mpeg": ".mp3",
          "audio/ogg": ".ogg",
          "audio/webm": ".webm",
          "audio/aac": ".aac",
          "audio/amr": ".amr",
          "audio/3gpp": ".3gp",
          "audio/mp4": ".mp4",
          "audio/x-wav": ".wav",
        }
        
        ext = content_type_to_ext.get(content_type.lower(), "")
        return response.content, ext
    
    logging.error(f"[Account: PRIMARY] Error downloading audio file from Meta: {response.text}")
    raise ValueError(f"Error downloading audio file from Meta")


def download_media_file_from_meta(media_url: str, media_id: str) -> tuple:
    """
    Download media file from WhatsApp/Meta servers.
    Similar to download_audio_file_from_meta but for images/documents.
    
    Args:
        media_url (str): URL to download the media from
        media_id (str): WhatsApp media ID for logging
        
    Returns:
        tuple: (file_content_bytes, file_extension, file_size)
    """
    try:
        # Get account configuration for headers
        account_config = get_account_config(None)  # Use primary account
        
        headers = {
            "Authorization": f"Bearer {account_config['access_token']}"
        }
        
        response = requests.get(media_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Get file content
        file_content = response.content
        file_size = len(file_content)
        
        # Determine file extension from content-type
        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            file_extension = 'jpg'
        elif 'png' in content_type:
            file_extension = 'png'
        elif 'pdf' in content_type:
            file_extension = 'pdf'
        elif 'msword' in content_type or 'wordprocessingml' in content_type:
            file_extension = 'docx'
        else:
            # Fallback to generic extension
            file_extension = 'bin'
            
        logging.info(f"Downloaded media {media_id}: {file_size} bytes, type: {content_type}")
        return file_content, file_extension, file_size
        
    except Exception as e:
        logging.error(f"Error downloading media {media_id}: {e}")
        return None, None, None


def get_message_body(message):
    """
    Extracts message body and type from a WhatsApp message payload.

    Handles:
    - Text
    - Interactive buttons
    - Template button replies
    - WhatsApp Flow (nfm_reply) - including document flows
    - Unknown/sticker/image/video messages

    Returns:
    - message_body (str)
    - message_type (str)
    """
    try:
        if message["type"] == "interactive":
            interactive_type = message['interactive']['type']
            if interactive_type == "nfm_reply":
                response_json = message["interactive"]["nfm_reply"]["response_json"]
                
                # Check if this is a document upload flow
                if isinstance(response_json, str):
                    try:
                        response_data = json.loads(response_json)
                    except json.JSONDecodeError:
                        response_data = response_json
                else:
                    response_data = response_json
                
                # Check for document/image uploads in flow response
                if isinstance(response_data, dict) and ("images" in response_data or "documents" in response_data):
                    return response_data, "flow_documents"
                
                return response_json, interactive_type
            elif interactive_type == "button_reply":
                return message["interactive"]["button_reply"]["title"], interactive_type
            elif interactive_type == "list_reply":
                return message["interactive"]["list_reply"]["title"], interactive_type
            else:
                logging.warning(f"Unknown interactive type: {interactive_type}")
                return json.dumps(message["interactive"]), interactive_type

        elif message["type"] == "text":
            return message["text"]["body"], message["type"]

        elif message["type"] == "button":
            return message["button"]["payload"], message["type"]
        
        elif message["type"] == "location":
            return f"Latitud: {message['location']['latitude']}, Longitud {message['location']['longitude']}", message["type"]
        
        elif message["type"] == "audio":
            if message['audio'] is None or message['audio']['id'] is None:
                logging.error(f"\n\n Audio is None \n for message_obj: {message} \n\n")
                
            return f"Audio: {message['audio']['id']}", message["type"]
        
        elif message["type"] == "reaction":
            emoji = message.get("reaction", {}).get("emoji", "👍")
            reacted_to_msg_id = message.get("reaction", {}).get("message_id", "unknown_id")
            return f"Reacción: {emoji} al mensaje {reacted_to_msg_id}", "reaction"

        elif message["type"] == "contacts":
            try:
                # Grab the shared contact info
                shared_contact = message.get("contacts", [{}])[0]

                # Extract name
                name_info = shared_contact.get("name", {})
                name = name_info.get("formatted_name") or f"{name_info.get('first_name', '')} {name_info.get('last_name', '')}".strip()
                if not name:
                    name = "Nombre desconocido"

                # Extract wa_id from phone list
                wa_id = None
                for phone in shared_contact.get("phones", []):
                    if "wa_id" in phone:
                        wa_id = phone["wa_id"]
                        break

                wa_id = wa_id or "WA ID desconocido"

                # Return a synthetic message body
                return f"Referencia compartida: {name} (Teléfono: {wa_id})", "text"
            except Exception as e:
                logging.error(f"Error parsing contact reference: {e} — message: {message}")
                return "Referencia inválida", "text"

        else:
            logging.error(f"\n\n Unknown message type {message['type']} \n for message_obj: {message} \n\n")
            return "unkown_message_type", "unkown_message_type"

    except KeyError as e:
        logging.error(f"\n\n Missing key in message payload: {e} for message_obj: {message} \n\n")
        return "missing_key_error", "missing_key_error"
    except Exception as e:
        logging.error(f"Unexpected error parsing message: {e}")
        return 'unknown_error', 'unknown_error'
    

# Processes and generates a user-friendly response based on a WhatsApp flow submission.
def get_nfm_reply_response(message_body, candidate_data):
    """
    Formats a JSON dictionary into a nicely structured response string.

    :param message_body: Dictionary containing the keys and values to format.
    :param candidate_data: Data for the employee related to the response.
    :return: Formatted string response.
    """
    try:
        # Parse the JSON string into a dictionary
        flow_data = json.loads(message_body)
        # Extract flow token and other relevant details
        flow_token_str = flow_data.get("flow_token")
        flow_token = json.loads(flow_token_str)
        if flow_token:
            # Assuming flow_token is a structured object with flow_type and expiration_date
            flow_type = flow_token.get("flow_type")
            expiration_date = datetime.fromisoformat(flow_token.get("expiration_date"))  # Convert timestamp to datetime
            
            # Expiry check
            if datetime.now() > expiration_date:
                return "Disculpa, este formulario ha expirado. Intentalo nuevamente"
            
            # Handle based on flow type
            if flow_type == "appointment_booking":
                # Extract selected date and hour
                selected_date = flow_data.get("fecha")
                selected_hour = flow_data.get("hora")
                company_id = candidate_data.get("company_id")
                
                # Get company capacity settings
                company_data = get_company_screening_data(company_id)
                max_capacity = company_data.get("max_interviews_per_slot") if company_data else None
                
                # Check if the selected slot is still available
                if not is_slot_available(company_id, selected_date, selected_hour, max_capacity):
                    # Slot is full - return error without saving
                    return "slot_full"
                
                #Get company location info
                interview_location = candidate_data.get("interview_location") or {}
                direccion_default = (
                    candidate_data.get("final_interview_address")
                    or interview_location.get("address")
                )
                location_link_default = (
                    candidate_data.get("final_interview_map_link")
                    or interview_location.get("url")
                )

                if (
                    (candidate_data["company_id"] == 3 and flow_data.get("hora") == "09:00") or
                    (candidate_data["company_id"] == 11 and candidate_data.get("role") == "Supervisor") or
                    (candidate_data["company_id"] == 158 and candidate_data.get("role") == "Marinero")
                ):
                    # Safely access JSON fields with fallbacks
                    maps_link_json = candidate_data.get("maps_link_json", {})
                    interview_address_json = candidate_data.get("interview_address_json", {})
                    
                    location_link = maps_link_json.get("location_link_2") or location_link_default or "No disponible"
                    direccion = interview_address_json.get("location_2") or direccion_default or "No disponible"

                elif candidate_data["company_id"] == 158 and candidate_data.get("role") == "Cajero Playa del Carmen":
                    # Safely access JSON fields with fallbacks
                    maps_link_json = candidate_data.get("maps_link_json", {})
                    interview_address_json = candidate_data.get("interview_address_json", {})
                    
                    location_link = maps_link_json.get("location_link_3") or location_link_default or "No disponible"
                    direccion = interview_address_json.get("location_3") or direccion_default or "No disponible"

                else:
                    if direccion_default or location_link_default:
                        location_link = location_link_default or "No disponible"
                        direccion = direccion_default or "No disponible"
                    else:
                        location_link, direccion = get_company_location_info(candidate_data)

                ##Store here the appointment booking in the database 
                update_candidate_interview_address_and_link(candidate_data["candidate_id"], direccion, location_link)
                update_funnel_state(candidate_data["candidate_id"], "scheduled_interview")
                add_interview_date_time(candidate_data, message_body)
                

                response = "Gracias por agendar tu entrevista:\n\n"
                response += f"*Fecha de la entrevista*: {flow_data.get('fecha', 'N/A')}\n"
                response += f"*Hora de la entrevista*: {flow_data.get('hora', 'N/A')}\n\n"
                response += f"*Direccion*: {direccion}\n"
                response += f"*Ubicacion*: {location_link}"

                additional_info = get_company_additional_info(candidate_data.get("company_id"))
                if additional_info:
                    response += f"\n\n{additional_info}"

            elif flow_type in ["checklist_1", "checklist_2", "pulso"]:
                response = 'Muchas gracias por tus comentarios!'
                store_checklist_responses(flow_data, candidate_data)
            else:
                response = "Muchas gracias por tu respuesta."
        else:
            response = "Ocurrió un error al procesar tu formulario. Por favor, inténtalo nuevamente."

    except json.JSONDecodeError as e:
        error_message = "Ocurrió un error al procesar tu formulario. Por favor, inténtalo nuevamente."
        logging.error(f"JSON decoding error: {e}")
        return error_message
    except Exception as e:
        error_message = "Ocurrió un error al procesar tu formulario. Por favor, inténtalo nuevamente."
        logging.error(f"Unexpected error: {e}")
        return error_message

    return response
