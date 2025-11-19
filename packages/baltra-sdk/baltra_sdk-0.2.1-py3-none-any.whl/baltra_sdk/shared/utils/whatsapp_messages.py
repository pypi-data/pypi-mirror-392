#import libraries
import json
from flask import current_app
import logging
import re
import base64
import requests
from baltra_sdk.shared.utils.postgreSQL_utils import fetch_campaign_data, fetch_due_messages, fetch_attendance_data, record_prize_redemption
from datetime import datetime, timedelta, date
from io import BytesIO
from PIL import Image
import math


"""
Description: This file handles the generation of various types of messages
to be sent via WhatsApp using the WhatsApp API. The messages are dynamically 
created based on templates and customized for individual employees. The 
types of messages include text, interactive buttons, CTA URLs, templates, 
location requests, and document attachments.

The main function, `get_keyword_response`, processes incoming keywords and
retrieves the corresponding message from a JSON file (`message_templates.json`).
The generated messages are then formatted based on employee data and sent 
through the WhatsApp API.
"""

# main flow of this file, gets called from openai_assistant
def get_keyword_response(keyword, employee_data):
    """
    Objective: Processes a keyword or button message from the user and returns a corresponding 
    response stored in `message_templates.json`. If no match is found, it returns an empty response 
    to allow the AI agent to take over.

    Args: 
    - keyword (str): The keyword or button ID that triggers the response.
    - employee_data (dict): A dictionary containing employee information, including 
    'first_name', 'company_name', 'rewards_description', and 'wa_id' (WhatsApp ID).

    Returns:
    - text (str): The plain text message that is used in the database and OpenAI thread.
    - message_data (json): The formatted JSON message to be sent via WhatsApp.
    """

    # Load the JSON data from the file
    with open('app/utils/data/message_templates.json', 'r', encoding='utf-8') as file: 
        messages = json.load(file)
    
    # Flatten messages from all companies into one dictionary, since message_templates.json is nested by company
    all_messages = {}
    for category, category_messages in messages.items():
        if category != "read_me":  # Ignore the documentation section
            all_messages.update(category_messages)  # Merge messages from different categories

    # Search for the keyword in the JSON data
    for message_key, message_obj in all_messages.items():
        # Skip if message_obj is not a dictionary (defensive programming)
        if not isinstance(message_obj, dict):
            logging.warning(f"Skipping non-dictionary message_obj for key '{message_key}': {message_obj}")
            continue
            
        if message_obj.get("keyword") == keyword or message_obj.get("button_trigger") == keyword:
            # Check the type of the message
            message_type = message_obj.get("type")
            text = replace_placeholder_functions(message_obj.get("text"), employee_data)
            text = text.format(
                name=employee_data.get("first_name", ""),
                company_name=employee_data.get("company_name", ""),
                context=employee_data.get("context", "") or "",
                rewards_description=(employee_data.get("rewards_description", "") or "").replace('\\n', '\n'),
                recargas=employee_data.get("recargas", ""),
                soriana=employee_data.get("soriana", ""),
                cinepolis=employee_data.get("cinepolis", "")
            )
            
            message_types = ["text", "interactive", "template", "document", "flow"]
            if message_type not in message_types:
                logging.warning(f"Invalid message type: {message_type} for message_obj: {message_obj}")

            if message_type == "text":
                message_data = get_text_message_input(employee_data["wa_id"], text)
            elif message_type == "interactive":
                interactive_type = message_obj.get("interactive_type")
                if interactive_type == "button":
                    button_keys = message_obj.get("button_keys")
                    footer_text = message_obj.get("footer_text", None)
                    header_type = message_obj.get("header_type", None)
                    header_content = message_obj.get("header_content", None)
                    message_data = get_button_message_input(employee_data,text, button_keys, footer_text, header_type, header_content)
                elif interactive_type == "cta_url": 
                    parameters = message_obj.get("parameters")
                    button_keys = message_obj.get("button_keys")
                    footer_text = message_obj.get("footer_text", None)
                    header_type = message_obj.get("header_type", None)
                    header_content = message_obj.get("header_content", None)
                    message_data = get_ctaurl_message_input(employee_data["wa_id"], text, parameters, footer_text, header_type, header_content)
                elif interactive_type =="location_request_message":
                    message_data = get_location_message(employee_data, text)
            elif message_type == "template":
                template_name = message_obj.get("template")
                button_keys = message_obj.get("button_keys")
                url_keys = message_obj.get("url_keys", None)
                variables = message_obj.get("variables")
                header_type = message_obj.get("header_type", None)
                header_content = message_obj.get("header_content", None)
                header_base = message_obj.get("header_base", None)
                flow_keys = message_obj.get("flow_keys", None)
                flow_action_data = message_obj.get("flow_action_data", None)
                message_data = get_template_message_input(template_name, employee_data, variables, button_keys, header_type, header_content, url_keys, header_base, flow_keys, flow_action_data)
            elif message_type == "document":
                link = message_obj.get("link")
                filename = message_obj.get("filename", None)
                message_data = get_document_message_input(employee_data, link, text, filename)
            elif message_type == "flow":
                header_content = message_obj.get("header_content", None)
                footer_text = message_obj.get("footer_text", None)
                flow_name = message_obj.get("flow_name", None)
                flow_CTA = message_obj.get("flow_CTA", None)
                message_data = personalized_flow(employee_data, flow_name, header_content, text, footer_text, flow_CTA)

            return text, message_data
    
    # Return None if no keyword matches
    return None, None

#Takes a string and wa_id and structures message as Json for whatsapp API, only works for text messages
def get_text_message_input(recipient, text):
    """
    Objective: Takes a string message and WhatsApp ID, processes the text, and structures 
    it as a JSON message for the WhatsApp API. This function only works for text messages.

    Args:
    - recipient (str): The recipient's WhatsApp ID.
    - text (str): The message content to be sent.

    Returns:
    - str: The formatted JSON string to be sent via the WhatsApp API.
    """
    text = process_text_for_whatsapp(text)
    message = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
            } 
    return json.dumps(message)

#Takes a series of arguments required to build an interactive message with buttons
def get_button_message_input(employee_data ,body_text, button_keys, footer_text=None, header_type=None, header_content=None):
    """
    Objective: Builds an interactive message with buttons for the WhatsApp API, 
    allowing for customizable body text, footer, and header content.

    Args:
    - employee_data (dict): Contains employee information such as the WhatsApp ID (wa_id).
    - body_text (str): The main text content of the message.
    - button_keys (list): A list of keys used to fetch button data from a JSON file.
    - footer_text (str, optional): The footer text to include in the message.
    - header_type (str, optional): The type of header (e.g., "image", "text").
    - header_content (str, optional): The content for the header (e.g., a URL or image link).

    Returns:
    - str: The formatted JSON string with the structured message to be sent via WhatsApp API.
    """
    
    #Load buttons from json file
    with open('app/utils/data/button_data.json', 'r', encoding="utf-8") as file:
        buttons_list = json.load(file)
    
    #select relevant buttons
    buttons = [buttons_list[key] for key in button_keys]

    #Build general structure of interactive message
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": employee_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "footer": {"text": footer_text},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": button_id, "title": button_title}} for button_id, button_title in buttons]
            }
        }
    }
    
    #Add footer if needed
    if footer_text:
        message["interactive"]["footer"] = {"text": footer_text}

    #Add header if needed
    if header_type and header_content:
        message["interactive"]["header"] = {
            "type": header_type,
            header_type: {"link": employee_data[header_content]}
    }
    
    #return Json with message structure
    return json.dumps(message)

#Takes a series of arguments required to build an interactive message with a cta url
def get_ctaurl_message_input(recipient, body_text, parameters, footer_text=None, header_type=None, header_content=None):
    """
    Objective: Builds an interactive message with a CTA (Call-to-Action) URL for the WhatsApp API, 
    allowing customization of the body text, footer, and header content, along with a parameterized CTA.

    Args:
    - recipient (str): The recipient's WhatsApp ID.
    - body_text (str): The main text content of the message.
    - parameters (dict): A dictionary of parameters that define the CTA URL action.
    - footer_text (str, optional): The footer text to include in the message.
    - header_type (str, optional): The type of header (e.g., "image", "text").
    - header_content (str, optional): The content for the header (e.g., a URL or image link).

    Returns:
    - str: The formatted JSON string with the structured message to be sent via WhatsApp API.
    """
    #Build general structure of interactive message
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "body": {"text": body_text},
            "footer": {"text": footer_text},
            "action": {
                "name": "cta_url",
                "parameters": parameters
            }

        }
    }
    
    #Add footer if needed
    if footer_text:
        message["interactive"]["footer"] = {"text": footer_text}

    #Add header if needed
    if header_type and header_content:
        message["interactive"]["header"] = {
            "type": header_type,
            header_type: header_content
    }
    
    #return Json with message structure
    return json.dumps(message)

#Takes a series of arguments required to build a template message which is required to start a conversation
def get_template_message_input(template_name, employee_data, variables=None, button_keys=None, 
                               header_type=None, header_content=None, url_keys=None,
                                header_base=None, flow_keys=None, flow_action_data = None):
    """
    Objective: Builds a WhatsApp template message with dynamic content such as headers, body variables, 
    buttons, URLs, and flows based on the provided arguments.

    Args:
    - template_name (str): The name of the template to use.
    - employee_data (dict): Employee data containing the necessary fields for dynamic content.
    - variables (dict, optional): A dictionary where keys are placeholders in the body template, 
    and values are the corresponding fields in `employee_data` to fill the placeholders.
    - button_keys (list, optional): A list of button keys to add quick reply buttons to the template.
    - header_type (str, optional): The type of header (e.g., 'image'). If provided, the header component is added.
    - header_content (str, optional): The content to use for the header, such as a link or image.
    - url_keys (list, optional): A list of keys that correspond to URLs in `employee_data` to include as URL buttons.
    - header_base (str, optional): A base URL or template string for the header, used in conjunction with `header_content`.
    - flow_keys (list, optional): A list of flow keys to add flow-based actions as buttons.

    Returns:
    - str: The formatted JSON string with the structured template message to be sent via the WhatsApp API.
    """
    language_code = "es" if template_name == "encuesta_1_ut" else "es_MX"

    # Build the general structure of the template message
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": employee_data["wa_id"],
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            },
            "components": []
        }
    }

    # Add header if provided
    if header_type == 'image':
        try:
            if header_base:  # Check if header_base has content
                link = header_base
                if header_content:
                    link = link.format(employee_data[header_content])  # Replace {} in header_base
            else:
                link = employee_data[header_content]  # Use employee_data directly if no header_base

            header_component = {
                "type": "header",
                "parameters": [
                    {
                        "type": header_type,
                        header_type: {"link": link}  # Use the resolved link
                    }
                ]
            }
            message["template"]["components"].append(header_component)

        except KeyError as e:
            logging.error(f"KeyError: Missing key '{e.args[0]}' in employee_data for wa_id={employee_data.get('wa_id')}")
        except Exception as e:
            logging.error(f"Unexpected error building header image: {e}")


    # Add body component with dynamic variables if provided
    if variables:
        body_component = {
            "type": "body",
            "parameters": []
        }

        # Iterate over the variables to populate the body component
        for placeholder, field in variables.items():
            body_component["parameters"].append({
                "type": "text",
                "text": employee_data[field]
            })
        
        message["template"]["components"].append(body_component)

    # Add urls if provided
    if url_keys:
        for index, url in enumerate(url_keys):
            url_component = {
                "type": "button",
                "sub_type": "url",
                "index": str(index),
                "parameters": [
                    {
                        "type": "text",
                        "text": employee_data[url]
                    }
                ]
            }
            message["template"]["components"].append(url_component)
    
    # Add buttons if provided
    if button_keys:
        offset = len(url_keys) if url_keys else 0
        for index, key in enumerate(button_keys):
            button_component = {
                "type": "button",
                "sub_type": "quick_reply",
                "index": str(index + offset),
                "parameters": [
                    {
                        "type": "payload",
                        "payload": key
                    }
                ]
            }
            message["template"]["components"].append(button_component)
    

    if flow_keys:
        for index, flow_key in enumerate(flow_keys):
            #Initialize action dict with the flow token stored in message_templates.json
            action_dict = {
                "flow_token": generate_flow_token(flow_key)
            }
     
            
            # If flow_action_data is provided and has corresponding entry
            if flow_action_data and index < len(flow_action_data):
                raw_data = flow_action_data[index]
                action_dict["flow_action_data"] = {
                    custom_key: employee_data.get(field_name, field_name)
                    for custom_key, field_name in raw_data.items()
                }

            flow_component = {
                "type": "button",
                "sub_type": "flow",
                "index": str(index),
                "parameters": [{"type": "action", 
                                "action": action_dict
                                }
                                ]
            }
            message["template"]["components"].append(flow_component)

    # Return JSON with message structure
    return json.dumps(message)

#Send a message requesting the user to provide his location, useful for attendance
def get_location_message(employee_data, text):
    """
    Objective: Builds a WhatsApp location request message, prompting the recipient to send their location.

    Args:
    - employee_data (dict): A dictionary containing employee data, including the WhatsApp ID ("wa_id").
    - text (str): The body text that will be displayed in the location request message.

    Returns:
    - str: A JSON string with the formatted location request message, ready to be sent via the WhatsApp API.
    """

    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": employee_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "location_request_message",
            "body": {
                "text": text
            },
            "action": {
                "name": "send_location"
            }

        }
    }
    #return Json with message structure
    return json.dumps(message)

#Process text for whatsapp to avoid errors
def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

#Send a message with an attahced document such as a pdf
def get_document_message_input(employee_data, link, text, filename):
    """
    Objective: Creates a document message for WhatsApp, including a link, caption, and filename.

    Args:
    - employee_data (dict): A dictionary containing employee data, including `wa_id`.
    - link (str): The URL of the document to be sent.
    - text (str): The caption text for the document.
    - filename (str): The name of the file to be sent.

    Returns:
    - str: A JSON string representing the WhatsApp document message, ready to be sent via the WhatsApp API.
    """

    text = process_text_for_whatsapp(text)
    message = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": employee_data["wa_id"],
            "type": "document",
            "document": {
                "link": link, 
                "caption": text,
                "filename": filename}
            } 
    return json.dumps(message)

#Call functions required to get input for messages
def replace_placeholder_functions(text, employee_data):
    # Define a dictionary with placeholder functions or values
    placeholder_functions = {
        "{scheduled_messages_due}": fetch_due_messages,  # Function for scheduled messages
        "{campaign_summary}": fetch_campaign_data,  # Function for campaign summary (example)
        "{attendance_data}": lambda: fetch_attendance_data(employee_data["company_id"])  # Extract company_id dynamically
    }

    # Loop through the placeholders and replace them if found
    for placeholder, func in placeholder_functions.items():
        if placeholder in text:
            # Call the function and replace the placeholder in the text
            replacement_value = func()  # Call the corresponding function
            text = text.replace(placeholder, replacement_value)
    return text

#Convert images from url to base64, required for whatsapp flows
def get_image_as_base64(url):
    """
    Fetch the image from 'url', compress it to below 100KB, and return Base64-encoded string.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if download fails
        
        # Load image into PIL
        img = Image.open(BytesIO(response.content))
        
        # Initial quality setting
        quality = 95
        max_size = 50 * 1024  # 100KB in bytes
        
        # Compress image
        output = BytesIO()
        
        # Convert RGBA to RGB if needed (JPEG doesn't support alpha channel)
        if img.mode == 'RGBA' or img.mode == 'P':
            img = img.convert('RGB')
        
        # Save with initial quality
        img.save(output, format='JPEG', quality=quality, optimize=True)
        
        # Iteratively reduce quality until size is below max_size
        while output.tell() > max_size and quality > 10:
            output = BytesIO()
            quality -= 5
            img.save(output, format='JPEG', quality=quality, optimize=True)
        
        # If still too large, resize the image
        if output.tell() > max_size:
            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            ratio = min(1.0, math.sqrt(max_size / (output.tell() * 1.1)))
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Resize and compress again
            img = img.resize((new_width, new_height), Image.LANCZOS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
        
        # Get the compressed image bytes
        compressed_image = output.getvalue()
        
        # Log compression results
        original_size = len(response.content) / 1024
        compressed_size = len(compressed_image) / 1024
        logging.debug(f"Image compressed from {original_size:.2f}KB to {compressed_size:.2f}KB (quality={quality})")
        
        # Encode in Base64
        encoded = base64.b64encode(compressed_image).decode('utf-8')
        return encoded
        
    except Exception as e:
        logging.error(f"Error processing image from {url}: {str(e)}")
        # Return a placeholder or empty string in case of error
        return ""

# Calculate the second Friday of the next month for delivery date
def get_second_friday_next_month():
    today = datetime.now()
        # Get the first day of next month
    if today.month == 12:
        next_month = 1
        year = today.year + 1
    else:
        next_month = today.month + 1
        year = today.year
            
    first_day = datetime(year, next_month, 1)
        
    # Find the first Friday (weekday 4 in Python's datetime)
    days_until_first_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=days_until_first_friday)
        
    # Add 7 days to get the second Friday
    second_friday = first_friday + timedelta(days=7)
        
    # Format the date in Spanish
    months_in_spanish = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
        
    return f"{second_friday.day} de {months_in_spanish[second_friday.month]}"

# Helper function to calculate the date of the second Friday of a given month and year.
# This can be placed before or near your existing get_second_friday_next_month function.
def _get_second_friday_date(year, month):
    """Calculates the date object for the second Friday of a given month and year."""
    first_day_of_month = date(year, month, 1)
    # weekday() returns 0 for Monday, ..., 4 for Friday, ..., 6 for Sunday
    days_until_first_friday = (4 - first_day_of_month.weekday() + 7) % 7
    first_friday = first_day_of_month + timedelta(days=days_until_first_friday)
    second_friday = first_friday + timedelta(days=7)
    return second_friday

##Creates a personalized flow message for WhatsApp, including dynamic content like prizes, points, and a custom delivery date
## Not limited to 3 prizes but flexible to any number (up to 20)
def personalized_flow(employee_data, flow_name, header, text, footer, flow_CTA):
    ## Normalize prizes from dict to list of dicts
    raw_prizes = employee_data.get("prizes", {})
    if isinstance(raw_prizes, dict) and "premio_1" in raw_prizes:
        prize_list = []
        i = 1
        while f"premio_{i}" in raw_prizes:
            prize = {
                "premio": raw_prizes.get(f"premio_{i}", ""),
                "puntos": raw_prizes.get(f"puntos_{i}", ""),
                "desc": raw_prizes.get(f"desc_{i}", ""),
                "boolean": raw_prizes.get(f"boolean_{i}", False),
                "link": raw_prizes.get(f"link_{i}", ""),
                "image": raw_prizes.get(f"image_{i}", ""),
            }
            prize_list.append(prize)
            i += 1
        employee_data["prizes"] = prize_list
    
    default_delivery_date_str = get_second_friday_next_month()
    premios_array = []

    for idx, prize in enumerate(employee_data.get("prizes", []), start=1):
        # Set defaults
        prize_name = prize.get("premio", "")
        puntos = prize.get("puntos", "")
        desc = prize.get("desc", "")
        boolean = prize.get("boolean", False)
        delivery_date = default_delivery_date_str
        image_base64 = ""

        # Convert link to base64 if provided
        if "link" in prize and prize["link"]:
            try:
                image_base64 = get_image_as_base64(prize["link"])
            except Exception as e:
                logging.error(f"Error converting image for prize {idx}: {e}")
        else:
            image_base64 = prize.get("image", "")

        # Handle special logic for Vales de Despensa
        if employee_data.get("company_id") == 5: 
            # Hardcoded delivery date for company_id 5
            delivery_date = "19 de Septiembre"
            # Check if this is the Vales de Despensa prize (prize_id 11)
            if prize_name == "Tarjeta $600 Vales de Despensa" and boolean:
                can_claim = vales_claimed_exception(employee_data)
                boolean = can_claim
            
            

        premios_array.append({
            "id": str(idx),
            "title": prize_name,
            "description": f"{puntos} puntos" if puntos else "",
            "image": image_base64,
            "enabled": boolean,
            "on-select-action": {
                "name": "update_data",
                "payload": {
                    "premio": prize_name,
                    "descripcion": desc,
                    "fecha": delivery_date,
                    "puntos": f"{puntos} puntos" if puntos else "",
                    "image": image_base64
                }
            }
        })

    message = {
        "recipient_type": "individual",
        "messaging_product": "whatsapp",
        "to": employee_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": text
            },
            "footer": {
                "text": footer
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": generate_flow_token("prize_claim", 1),
                    "flow_name": flow_name,
                    "mode": "published",
                    "flow_cta": flow_CTA,
                    "flow_action": "navigate",
                    "flow_action_payload": {
                        "screen": "SELECCIONA",
                        "data": {
                            "premios": premios_array,
                            "premio": "",
                            "descripcion": "",
                            "fecha": "",
                            "puntos": "",
                            "image": "",
                            "total_points": f"{employee_data['total_points']}"
                        }
                    }
                }
            }
        }
    }
    return json.dumps(message)

# Processes and generates a user-friendly response based on a WhatsApp flow submission.
def get_nfm_reply_response(message_body, employee_data):
    """
    Formats a JSON dictionary into a nicely structured response string.

    :param message_body: Dictionary containing the keys and values to format.
    :param employee_data: Data for the employee related to the response.
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
            if flow_type == "prize_claim":
                response = "Muchas felicidades, tu premio ha sido canjeado con éxito:\n"
                response += f"*Premio Seleccionado*: {flow_data.get('premio_seleccionado', 'N/A')}\n"
                response += f"*Puntos Canjeados*: {flow_data.get('puntos', 'N/A')}\n"
                response += f"*Fecha de Entrega*: {flow_data.get('delivery_date', 'N/A')}"
                
                # Clean and process the points
                try:
                    points_str = str(flow_data.get('puntos', '0'))
                    points_cleaned = points_str.replace('puntos', '').strip()
                    points_redeemed = int(points_cleaned)
                    date_str = str(flow_data.get('delivery_date', '1 de Enero')).strip()
                    record_prize_redemption(employee_data, points_redeemed, date_str)
                except (ValueError, TypeError) as e:
                    error_message = "Ocurrió un error al procesar tu formulario. Por favor, inténtalo nuevamente."
                    logging.error(f"Error processing points redemption: {e}")
                    return error_message

            elif flow_type == "ECPI":
                response = "Muchas gracias por tu evaluación. Aquí tienes un resumen de tus respuestas:\n"
                response += f"Soluciones a Tiempo: {flow_data.get('screen_0_Tiempo_0', 'N/A')}\n"
                response += f"Soluciones Efectivas: {flow_data.get('screen_0_Efectividad_1', 'N/A')}\n"
                response += f"Disposición a Ayudar: {flow_data.get('screen_0_Actitud_2', 'N/A')}\n"
                response += f"Sugerencias: {flow_data.get('screen_1_Deja_tu_sugerencia_0', 'N/A')}"
                
            elif flow_type == "ECPI-mtto" or flow_type == "calidad":
                response = "Muchas gracias por tu evaluación. Tus comentarios son muy valiosos para la empresa!"
            elif flow_type == "pulse":
                response = "Muchas gracias por tu respuesta! Que sientes que te hace falta para dar tu 100% en la empresa"
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


def vales_claimed_exception(employee_data):
    """
    Checks if an employee from company_id 5 has claimed prize_id 11 (Tarjeta $600 Vales de Despensa)
    within the last 10 days. Returns False if a claim exists in this period (meaning they can't claim again),
    True otherwise.

    Returns:
        bool: True if the prize can be claimed, False otherwise.
    """
    if not employee_data.get("redemptions"):
        # No redemptions, so the prize couldn't have been claimed
        return True

    # Calculate the date 10 days ago
    ten_days_ago = date.today() - timedelta(days=15)
    
    for redemption in employee_data["redemptions"]:
        if redemption.get("prize_name") == 'Tarjeta $600 Vales de Despensa':
            date_requested_str = redemption.get("date_requested")
            if not date_requested_str:
                logging.warning("Skipping 'Tarjeta $600 Vales de Despensa' redemption due to missing date_requested.")
                continue

            try:
                # date_requested could be a full ISO datetime string (e.g., "2023-10-26T10:00:00").
                # Convert to date object. date.fromisoformat expects "YYYY-MM-DD".
                if 'T' in date_requested_str: # Handle datetime strings by taking only the date part
                    date_requested_str = date_requested_str.split('T')[0]
                redemption_date = date.fromisoformat(date_requested_str)
                
                if redemption_date >= ten_days_ago:
                    logging.info(f"Employee {employee_data['wa_id']} has claimed prize_id 11 within the last 10 days. Date: {redemption_date}")
                    return False  # Cannot claim
            except ValueError:
                logging.warning(f"Could not parse date_requested: '{date_requested_str}' for prize_id 11 check.")
                continue
    
    logging.debug(f"Employee {employee_data['wa_id']} has NOT claimed prize_id 11 within the last 30 days.")
    return True  # Can claim


def generate_flow_token(flow_type, expiration_days=7):
    """
    Generates a flow_token with a flow type and a calculated expiration date.

    Args:
    - flow_type (str): Identifier for the type of flow (e.g., 'ECPI', 'prize_claim').
    - expiration_days (int): The number of days until the token expires.

    Returns:
    - str: JSON-encoded flow_token string.
    """
    expiration_date = datetime.now() + timedelta(days=expiration_days)  # Calculate expiration date
    token_data = {
        "flow_type": flow_type,
        "expiration_date": expiration_date.isoformat()  # Store expiration date as ISO format string
    }
    return json.dumps(token_data)
