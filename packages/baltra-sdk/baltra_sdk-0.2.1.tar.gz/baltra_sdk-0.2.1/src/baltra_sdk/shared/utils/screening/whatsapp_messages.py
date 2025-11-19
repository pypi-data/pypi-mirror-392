#import libraries
import json
from flask import current_app
import logging
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from baltra_sdk.legacy.dashboards_folder.models import MessageTemplates, CompaniesScreening
from .sql_utils import get_company_screening_data, get_active_roles_text, get_active_roles_for_company, mark_end_flow_rejected, get_candidate_eligible_roles, get_candidate_eligible_companies, is_slot_available, get_available_dates_and_hours
from .sql_utils import get_company_screening_data, get_active_roles_text, get_active_roles_for_company, mark_end_flow_rejected, get_candidate_eligible_roles, get_candidate_eligible_companies, get_companies_for_group, get_roles_grouped_by_company, update_funnel_state
import re

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

def company_supports_flows(company_id: int, session: Session) -> bool:
    company = session.query(CompaniesScreening).filter_by(company_id=company_id).first()
    return bool(company and company.company_is_verified_by_meta)

#Main function of this file, determines how the message should be built
def get_keyword_response_from_db(keyword: str, candidate_data: dict, session = Session):
    """
    Processes a keyword or button message from the user and returns a corresponding 
    response stored in the database. If no match is found, it returns an empty response.

    Args:
    - session (Session): SQLAlchemy session connected to your database.
    - keyword (str): The keyword or button ID that triggers the response.
    - candidate_data (dict): A dictionary containing employee information.

    Returns:
    - text (str): The plain text message used in the database and OpenAI thread.
    - message_data (json): The formatted JSON message to be sent via WhatsApp.
    """

    company_id = candidate_data.get("company_id")
    supports_flows = company_supports_flows(company_id, session)

    # For reschedule_interview with unverified companies, use the list version instead
    if keyword == "reschedule_interview" and not supports_flows:
        # Try to find the list version first
        message_obj = (
            session.query(MessageTemplates)
            .filter(
                ((MessageTemplates.keyword == "reschedule_interview_list") | 
                 (MessageTemplates.button_trigger == "reschedule_interview_list"))
            )
            .first()
        )
        # If list version not found, log warning and fall back to regular lookup
        if not message_obj:
            logging.warning(f"reschedule_interview_list template not found for unverified company {company_id}. Falling back to regular reschedule template - this may cause errors!")
            message_obj = (
                session.query(MessageTemplates)
                .filter((MessageTemplates.keyword == keyword) | (MessageTemplates.button_trigger == keyword))
                .first()
            )
    else:
        # Regular lookup for all other cases
        message_obj = (
            session.query(MessageTemplates)
            .filter((MessageTemplates.keyword == keyword) | (MessageTemplates.button_trigger == keyword))
            .first()
        )

    if not message_obj:
        logging.warning(f"No keyword matches for keyword: {keyword} and candidate_data: {candidate_data}")
        return None, None

    # Update funnel state to 'phone_interview_cited' when phone interview template is sent
    # This template can be identified by keyword 'phone_interview_cemex' or interactive_type 'cta_url' with this keyword
    if keyword == "phone_interview_cemex" or (message_obj.keyword == "phone_interview_cemex"):
        candidate_id = candidate_data.get("candidate_id")
        current_funnel_state = candidate_data.get("funnel_state")
        
        # Only update if not already in this state or a later state
        if current_funnel_state != "phone_interview_cited":
            success = update_funnel_state(candidate_id, "phone_interview_cited")
            if success:
                logging.info(f"✅ Updated candidate {candidate_id} funnel state to 'phone_interview_cited' (from '{current_funnel_state}') when sending phone interview template")
                # Update the candidate_data dict so the rest of the flow has the updated state
                candidate_data["funnel_state"] = "phone_interview_cited"
            else:
                logging.error(f"❌ Failed to update funnel state for candidate {candidate_id} to 'phone_interview_cited'")

    message_type = message_obj.type
    text = message_obj.text or ""
    
    if '{roles}' in text:
        roles_str = get_active_roles_text(candidate_data.get("company_id"))
    else:
        roles_str = ""
        
    # Add failsafes for None values
    role_value = candidate_data.get("role", "")
    if role_value is None:
        role_value = "trabajo"
        
    name_value = candidate_data.get("first_name", "")
    if name_value is None:
        name_value = " "
        
    text = text.format(
        name=name_value,
        company_name=candidate_data.get("company_name", ""),
        roles=roles_str,
        role=role_value,
        interview_date=candidate_data.get("interview_date",""),
        interview_address=candidate_data.get("interview_address",""),
    )
    text = text.replace('\\n', '\n')
    if message_type == "text":
        message_data = get_text_message_input(candidate_data["wa_id"], text)
    elif message_type == "interactive":
        if message_obj.interactive_type == "button":
                message_data = get_button_message_input(
                candidate_data,
                text,
                message_obj.button_keys,
                message_obj.footer_text,
                message_obj.header_type,
                message_obj.header_content
                )
        elif message_obj.interactive_type == "cta_url":
            message_data = get_ctaurl_message_input(
                candidate_data, 
                text, 
                message_obj.parameters, 
                message_obj.footer_text, 
                message_obj.header_type, 
                message_obj.header_content)
        elif message_obj.interactive_type == "location_request_message":
            message_data = get_location_message(candidate_data, text)

        elif message_obj.interactive_type == "list":
            message_data = get_list_message_input(
                candidate_data,
                text,
                message_obj.flow_cta,
                message_obj.list_section_title,
                message_obj.list_options,
                message_obj.footer_text,
                message_obj.header_type,
                message_obj.header_content
            )
    elif message_type == "roles_list":
        message_data = build_roles_list_message(candidate_data, message_obj, text)

    elif message_type == "eligibility_roles_list":
        message_data = build_eligibility_roles_list_message(candidate_data, message_obj, text)
    
    elif message_type == "eligibility_companies_list":
        message_data = build_eligibility_companies_list_message(candidate_data, message_obj, text)

    elif message_type == "companies_list":
        message_data = build_company_list_message(candidate_data, message_obj, text)

    elif message_type == "education_list":
        message_data = build_academic_grade_message(candidate_data, message_obj, text)

    elif message_type == "job_source_list":
        message_data = build_job_source_message(candidate_data, message_obj, text)

    elif message_type == "rehire_list":
        message_data = build_rehire_list_message(candidate_data, message_obj, text)

    elif message_type == "schedule_interview_list":
        # Allow scheduling for: initial screening, post-phone interview, or rescheduling (missed/scheduled interviews)
        allowed_states = ["screening_in_progress", "phone_interview_passed", "scheduled_interview", "missed_interview"]
        if candidate_data["funnel_state"] in allowed_states:
            message_data = build_schedule_interview_list_message(candidate_data, message_obj, text)
        else:
            # Candidate was rejected or in invalid state for scheduling
            text = "✅ ¡Listo! Esa fue la última pregunta\n📩 Nos pondremos en contacto contigo pronto para contarte si tenemos alguna vacante que se ajuste a tu perfil."
            mark_end_flow_rejected(candidate_data["candidate_id"])
            message_data = get_text_message_input(candidate_data["wa_id"], text)

    elif message_type == "template":
        # Safety check: if company doesn't support flows but template has flow buttons, log error
        if not supports_flows and message_obj.flow_keys:
            logging.error(f"Company {company_id} is not verified by Meta but template '{message_obj.template}' has flow buttons. This will likely fail. Consider using a different template type for unverified companies.")
        
        message_data = get_template_message_input(
            message_obj.template,
            candidate_data,
            message_obj.variables,
            message_obj.button_keys,
            message_obj.header_type,
            message_obj.header_content,
            message_obj.url_keys,
            message_obj.header_base,
            message_obj.flow_keys,
            message_obj.flow_action_data
        )
    elif message_type == "reschedule_appointment":
        if supports_flows:
            message_data = get_template_reschedule_appointment(
                template_name=message_obj.template,
                candidate_data=candidate_data,
                message_obj=message_obj
            )
        else:
            message_data = get_interactive_reschedule_appointment(candidate_data, message_obj, text)

    elif message_type == "generic_template_flow":
        message_data = get_generic_template_message_with_flow(
            template_name=message_obj.template,
            candidate_data=candidate_data,
            message_obj=message_obj
        )

    elif message_type == "document":
        message_data = get_document_message_input(
            candidate_data, message_obj.document_link, 
            text, 
            message_obj.filename
            )
    elif message_type == "appointment_scheduling":
        #Only send appointment scheduling flow if the user was not rejected
        allowed_states_for_scheduling = ["screening_in_progress", "phone_interview_passed"]
        if candidate_data["funnel_state"] in allowed_states_for_scheduling:
            message_data = appointment_booking_flow(
                candidate_data,
                message_obj.flow_name,
                message_obj.header_content,
                text,
                message_obj.footer_text,
                message_obj.flow_cta
            )
        else:
            text = "✅ ¡Listo! Esa fue la última pregunta\n📩 Nos pondremos en contacto contigo pronto para contarte si tenemos alguna vacante que se ajuste a tu perfil."
            mark_end_flow_rejected(candidate_data["candidate_id"])
            message_data = get_text_message_input(candidate_data["wa_id"], text)
    elif message_type == "request_documents":
        message_data = request_documents_flow(
            candidate_data,
            message_obj.flow_name,
            message_obj.header_content,
            text,
            message_obj.footer_text,
            message_obj.flow_cta
        )
    
    else:
        logging.warning(f"Invalid message type: {message_type} for message_obj: {message_obj}")
        return None, None

    return text, message_data

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

#Build an interactive message with buttons
def get_button_message_input(candidate_data: dict, body_text: str, button_pairs: list, footer_text=None, header_type=None, header_content=None):
    """
    Builds an interactive WhatsApp message using button pairs embedded in the message_templates table.

    Args:
    - candidate_data (dict): Employee info, including 'wa_id'.
    - body_text (str): Main text content.
    - button_pairs (list): List of [button_id, button_title] pairs.
    - footer_text (str, optional): Footer text.
    - header_type (str, optional): 'text', 'image', etc.
    - header_content (str, optional): Key to pull content from candidate_data.

    Returns:
    - str: JSON string of WhatsApp message.
    """

    if not button_pairs:
        logging.warning("No buttons defined.")
        return None

    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": btn_id, "title": btn_title}
                    }
                    for btn_id, btn_title in button_pairs
                ]
            }
        }
    }

    if footer_text:
        message["interactive"]["footer"] = {"text": footer_text}

    if header_type and header_content:
        message["interactive"]["header"] = {
            "type": header_type,
            header_type: {"link": header_content}
        }

    return json.dumps(message)

def get_list_message_input(candidate_data: dict, text: str, button_text: str, list_section_title: str, list_options: list, footer_text=None, header_type=None, header_content=None):
    """
    Builds a WhatsApp interactive list message.

    Args:
    - candidate_data (dict): Info including 'wa_id'.
    - text (str): Main content of the message body.
    - button_text (str): The button label (e.g., "Choose Option").
    - list_section_title (str): Title of the list section.
    - list_options (list): List of rows, each is a dict with keys "id", "title", and optional "description".
    - footer_text (str, optional): Footer note.
    - header_type (str, optional): Only "text" is supported in list headers.
    - header_content (str, optional): Text for the header.

    Returns:
    - str: JSON-formatted string for the WhatsApp API.
    """

    # Build the sections list internally
    sections = [
        {
            "title": list_section_title or "Opciones",
            "rows": list_options or []
        }
    ]

    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": text
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }

    # Optional footer
    if footer_text:
        message["interactive"]["footer"] = {"text": footer_text}

    # Optional header
    if header_type == "text" and header_content:
        message["interactive"]["header"] = {
            "type": "text",
            "text": header_content
        }

    return json.dumps(message)

#Takes a series of arguments required to build an interactive message with a url
def get_ctaurl_message_input(candidate_data, body_text, parameters, footer_text=None, header_type=None, header_content=None):
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
        "to": candidate_data['wa_id'],
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
def get_template_message_input(template_name, candidate_data, variables=None, button_keys=None, 
                               header_type=None, header_content=None, url_keys=None,
                                header_base=None, flow_keys=None, flow_action_data = None):
    """
    Objective: Builds a WhatsApp template message with dynamic content such as headers, body variables, 
    buttons, URLs, and flows based on the provided arguments.

    Args:
    - template_name (str): The name of the template to use.
    - candidate_data (dict): Employee data containing the necessary fields for dynamic content.
    - variables (dict, optional): A dictionary where keys are placeholders in the body template, 
    and values are the corresponding fields in `candidate_data` to fill the placeholders.
    - button_keys (list, optional): A list of button keys to add quick reply buttons to the template.
    - header_type (str, optional): The type of header (e.g., 'image'). If provided, the header component is added.
    - header_content (str, optional): The content to use for the header, such as a link or image.
    - url_keys (list, optional): A list of keys that correspond to URLs in `candidate_data` to include as URL buttons.
    - header_base (str, optional): A base URL or template string for the header, used in conjunction with `header_content`.
    - flow_keys (list, optional): A list of flow keys to add flow-based actions as buttons.

    Returns:
    - str: The formatted JSON string with the structured template message to be sent via the WhatsApp API.
    """
    
    # Build the general structure of the template message
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "es_MX"
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
                    link = link.format(candidate_data[header_content])  # Replace {} in header_base
            else:
                link = candidate_data[header_content]  # Use candidate_data directly if no header_base

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
            logging.error(f"KeyError: Missing key '{e.args[0]}' in candidate_data for wa_id={candidate_data.get('wa_id')}")
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
                "text": candidate_data.get(field, "-")
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
                        "text": candidate_data[url]
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
                        "payload": key[0]
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
                    custom_key: candidate_data.get(field_name, "")
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
def get_location_message(candidate_data, text):
    """
    Objective: Builds a WhatsApp location request message, prompting the recipient to send their location.

    Args:
    - candidate_data (dict): A dictionary containing employee data, including the WhatsApp ID ("wa_id").
    - text (str): The body text that will be displayed in the location request message.

    Returns:
    - str: A JSON string with the formatted location request message, ready to be sent via the WhatsApp API.
    """

    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
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

#Send a message with an attahced document such as a pdf
def get_document_message_input(candidate_data, document_link, text, filename):
    """
    Objective: Creates a document message for WhatsApp, including a link, caption, and filename.

    Args:
    - candidate_data (dict): A dictionary containing employee data, including `wa_id`.
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
            "to": candidate_data["wa_id"],
            "type": "document",
            "document": {
                "link": document_link, 
                "caption": text,
                "filename": filename}
            } 
    return json.dumps(message)

#Flow to book and interview
def appointment_booking_flow(candidate_data, flow_name, header, text, footer, flow_CTA):
    company_id = candidate_data.get("company_id")
    company_data = get_company_screening_data(company_id)
    interview_address = company_data.get("interview_address_json", {})

    if not company_data:
        raise ValueError(f"No screening configuration found for company_id {company_id}")
    
    # Manual offset: Mexico is UTC-6
    utc_now = datetime.now()
    mexico_now = utc_now - timedelta(hours=6)

    # 7 day search window starting tomorrow
    tomorrow = mexico_now.date() + timedelta(days=1)
    start_date = tomorrow.strftime('%Y-%m-%d')
    search_end_date = (tomorrow + timedelta(days=7)).strftime('%Y-%m-%d')

    # Get company configuration
    all_hours = company_data["interview_hours"]
    max_capacity = company_data.get("max_interviews_per_slot")
    interview_days = company_data.get("interview_days", [])
    unavailable_dates = company_data.get("unavailable_dates", [])
    
    # Get available dates with per-date hour availability (max 4 days)
    available_dates = get_available_dates_and_hours(
        company_id,
        start_date,
        search_end_date,
        all_hours,
        max_capacity,
        interview_days,
        unavailable_dates,
        max_days=4
    )
    
    # Calculate actual end_date based on the last available date returned (max 4 days)
    # This ensures WhatsApp Flow calendar only shows the dates we're sending
    if available_dates:
        end_date = available_dates[-1]["date"]
    else:
        # Fallback if no dates available
        end_date = start_date
    
    # Build the flow_action_payload data structure
    flow_data = {
        "start_date": start_date,
        "end_date": end_date,
        "dirección": interview_address.get("location_1", "No disponible"),
        "unavailable_dates": unavailable_dates,
        "include_days": interview_days
    }
    
    # Add date_N and hours_N for each available date
    for i, date_info in enumerate(available_dates, start=1):
        flow_data[f"date_{i}"] = date_info["date"]
        flow_data[f"hours_{i}"] = date_info["hours"]
    
    message = {
        "recipient_type": "individual",
        "messaging_product": "whatsapp",
        "to": candidate_data["wa_id"],
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
                    "flow_token": generate_flow_token("appointment_booking", 1),
                    "flow_name": flow_name,
                    "mode": "published",
                    "flow_cta": flow_CTA,
                    "flow_action": "navigate",
                    "flow_action_payload": {
                        "screen": "FECHA",
                        "data": flow_data
                    }
                }
            }
        }
    }

    return json.dumps(message)

def get_interactive_reschedule_appointment(candidate_data, message_obj, text):
    company_id = candidate_data.get("company_id")
    company_data = get_company_screening_data(company_id)
    if not company_data:
        return None

    utc_now = datetime.now()
    mexico_now = utc_now - timedelta(hours=6)
    tomorrow = mexico_now.date() + timedelta(days=1)
    start_date = tomorrow.strftime('%Y-%m-%d')
    search_end_date = (tomorrow + timedelta(days=7)).strftime('%Y-%m-%d')

    all_hours = company_data["interview_hours"]
    max_capacity = company_data.get("max_interviews_per_slot")
    interview_days = company_data.get("interview_days", [])
    unavailable_dates = company_data.get("unavailable_dates", [])

    available_dates = get_available_dates_and_hours(
        company_id,
        start_date,
        search_end_date,
        all_hours,
        max_capacity,
        interview_days,
        unavailable_dates,
        max_days=4
    )
    if not available_dates:
        return None

    def format_time_ampm(t):
        h, m = map(int, t.split(':'))
        p = 'AM' if h < 12 else 'PM'
        dh = h if h <= 12 else h - 12
        dh = 12 if dh == 0 else dh
        return f"{dh}:{m:02d} {p}"

    sections = []
    day_names = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    month_names = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    total_rows = 0

    for date_info in available_dates:
        date_str = date_info["date"]
        hours = date_info["hours"]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = day_names[date_obj.weekday()]
        month_name = month_names[date_obj.month - 1]
        section_title = f"{day_name} {date_obj.day}- {month_name}"
        rows = []
        row_desc = f"{day_name} {date_obj.day} de {month_name}"

        for hour_info in hours:
            if hour_info.get("enabled", False):
                h24 = hour_info["title"]
                rows.append({
                    "id": f"interview_date_time${date_str}T{h24}:00",
                    "title": format_time_ampm(h24),
                    "description": row_desc
                })
                total_rows += 1
                if total_rows >= 10:
                    break

        if rows:
            sections.append({"title": section_title, "rows": rows})
        if total_rows >= 10:
            break

    header_text = message_obj.header_content if message_obj.header_type == "text" and message_obj.header_content else "Reagenda tu Entrevista"
    footer_text = message_obj.footer_text or None
    cta = message_obj.flow_cta or "Reagendar Entrevista"

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": text},
            "action": {"button": cta, "sections": sections}
        }
    }
    if footer_text:
        payload["interactive"]["footer"] = {"text": footer_text}
    if header_text:
        payload["interactive"]["header"] = {"type": "text", "text": header_text}

    return json.dumps(payload)


def get_template_reschedule_appointment(template_name, candidate_data, message_obj):
    """
    Builds a WhatsApp template message that includes a Flow button to reschedule an interview.
    The Flow payload includes dynamic scheduling options fetched from the database.

    Args:
    - template_name (str): Name of the WhatsApp template.
    - candidate_data (dict): Candidate info.
    - message_obj: MessageTemplates ORM object.

    Returns:
    - str: JSON-encoded message ready for WhatsApp API.
    """

    # Main message structure
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "es_MX"
            },
            "components": []
        }
    }

    # Add body parameters
    if message_obj.variables:
        body_component = {
            "type": "body",
            "parameters": []
        }
        for _, field in message_obj.variables.items():
            body_component["parameters"].append({
                "type": "text",
                "text": candidate_data.get(field, "")
            })
        message["template"]["components"].append(body_component)

    # Generate dynamic Flow payload from DB
    company_id = candidate_data.get("company_id")
    company_data = get_company_screening_data(company_id)

    interview_location = candidate_data.get("interview_location") or {}
    direccion_value = (
        candidate_data.get("final_interview_address")
        or interview_location.get("address")
        or (company_data.get("interview_address_json") or {}).get("location_1")
        or "No disponible"
    )

    # Time calculations
    utc_now = datetime.now()
    mexico_now = utc_now - timedelta(hours=6)
    tomorrow = mexico_now.date() + timedelta(days=1)
    start_date = tomorrow.strftime('%Y-%m-%d')
    search_end_date = (tomorrow + timedelta(days=7)).strftime('%Y-%m-%d')

    # Get company configuration
    all_hours = company_data["interview_hours"]
    max_capacity = company_data.get("max_interviews_per_slot")
    interview_days = company_data.get("interview_days", [])
    unavailable_dates = company_data.get("unavailable_dates", [])
    
    # Get available dates with per-date hour availability (max 4 days)
    available_dates = get_available_dates_and_hours(
        company_id,
        start_date,
        search_end_date,
        all_hours,
        max_capacity,
        interview_days,
        unavailable_dates,
        max_days=4
    )

    # Calculate actual end_date based on the last available date returned (max 4 days)
    # This ensures WhatsApp Flow calendar only shows the dates we're sending
    if available_dates:
        end_date = available_dates[-1]["date"]
    else:
        # Fallback if no dates available
        end_date = start_date

    # Build the flow_action_data structure
    flow_action_data = {
        "start_date": start_date,
        "end_date": end_date,
        "dirección": direccion_value,
        "unavailable_dates": unavailable_dates,
        "include_days": interview_days
    }
    
    # Add date_N and hours_N for each available date
    for i, date_info in enumerate(available_dates, start=1):
        flow_action_data[f"date_{i}"] = date_info["date"]
        flow_action_data[f"hours_{i}"] = date_info["hours"]

    # Generate flow_token and button
    flow_token = generate_flow_token(message_obj.flow_keys[0])
    flow_button = {
        "type": "button",
        "sub_type": "flow",
        "index": "0",
        "parameters": [
            {
                "type": "action",
                "action": {
                    "flow_token": flow_token,
                    "flow_action_data": flow_action_data
                }
            }
        ]
    }

    message["template"]["components"].append(flow_button)
    logging.info(f'Message Structure: {json.dumps(message)}')
    return json.dumps(message)


#Flow to request documents
def request_documents_flow(candidate_data, flow_name, header, text, footer, flow_CTA):

    message = {
        "recipient_type": "individual",
        "messaging_product": "whatsapp",
        "to": candidate_data["wa_id"],
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
                    # Encode the specific flow/template name in the token so uploads can be named accordingly
                    "flow_token": generate_flow_token(flow_name, 1),
                    "flow_name": flow_name,
                    "mode": "published",
                    "flow_cta": flow_CTA,
                    "flow_action": "navigate",
                    "flow_action_payload": {
                        "screen": "RFC"
                    }
                }
            }
        }
    }

    return json.dumps(message)

def build_roles_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message showing active roles for the candidate's company.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id' and 'company_id'.
        message_obj (MessageTemplates): Template row from DB.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    company_id = candidate_data.get("company_id")
    if not company_id:
        logging.error("Missing company_id in candidate_data")
        return None

    roles = get_active_roles_for_company(company_id)
    if not roles:
        logging.warning(f"No active roles found for company {company_id}")
        return None

    list_options = [
        {
            "id": f"role_id${role['role_id']}",
            "title": role["role_name"],
            "description": role.get("shift", "")
        }
        for role in roles
    ]

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )

def build_academic_grade_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message with options for highest academic grade.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id' and 'company_id'.
        message_obj (MessageTemplates): Template row from DB.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    academic_grades = [
        "Ninguno",
        "Primaria",
        "Secundaria",
        "Preparatoria",
        "Preparatoria Técnica",
        "Licenciatura"
    ]

    list_options = [
        {
            "id": f"education_level${grade.replace(' ', '_').lower()}",
            "title": grade,
            "description": ""
        }
        for grade in academic_grades
    ]

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )

def build_job_source_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message with options for where the candidate saw the job posting.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id' and 'company_id'.
        message_obj (MessageTemplates): Template row from DB.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    job_sources = [
        {"title": "Facebook", "id": "facebook", "description": ""},
        {"title": "Publicidad en tienda", "id": "publicidad_en_tienda", "description": ""},
        {"title": "Manta o flyer", "id": "publicidad_fuera_de_tienda", "description": "Publicidad fuera de tienda"},
        {"title": "Otra", "id": "otra", "description": ""}
    ]

    list_options = [
        {
            "id": f"source${source['id']}",
            "title": source['title'],
            "description": source['description']
        }
        for source in job_sources
    ]

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )

def build_eligibility_roles_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message showing eligible roles for the candidate.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id' and eligible roles.
        message_obj (MessageTemplates): Template row from DB.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    
    candidate_id = candidate_data.get("candidate_id")
    if not candidate_id:
        logging.error("Missing candidate_id in candidate_data")
        return None

    # Get eligible role IDs
    eligible_role_ids = get_candidate_eligible_roles(candidate_id)
    if not eligible_role_ids:
        logging.warning(f"No eligible roles found for candidate {candidate_id}")
        return None

    # Get role details for eligible roles
    company_id = candidate_data.get("company_id")
    all_roles = get_active_roles_for_company(company_id)
    eligible_roles = [role for role in all_roles if role["role_id"] in eligible_role_ids]

    if not eligible_roles:
        logging.warning(f"No matching active roles found for eligible role IDs {eligible_role_ids}")
        return None

    # Build list options for eligible roles
    list_options = [
        {
            "id": f"role_id${role['role_id']}",
            "title": role["role_name"],
            "description": role.get("shift", "") 
        }
        for role in eligible_roles
    ]

    # Add "no preference" option if multiple roles
    if len(eligible_roles) > 1:
        list_options.append({
            "id": "no_preference",
            "title": "No tengo preferencia",
            "description": "Cualquiera de estos puestos me interesa"
        })

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )

def build_eligibility_companies_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message showing eligible companies for the candidate.
    """

    candidate_id = candidate_data.get("candidate_id")
    if not candidate_id:
        logging.error("Missing candidate_id in candidate_data")
        return None

    # Fetch eligible companies directly
    eligible_companies = get_candidate_eligible_companies(candidate_id)  
    if not eligible_companies:
        logging.warning(f"No eligible companies found for candidate {candidate_id}")
        return None

    # Build list options with address as description
    list_options = [
        {
            "id": f"company_id${company['company_id']}",
            "title": company["name"],
            "description": company.get("address", "")  # address as description
        }
        for company in eligible_companies
    ]

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )

def build_rehire_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message with simple Si/No options for rehire confirmation.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id'.
        message_obj (MessageTemplates): Template row from DB.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    list_options = [
        {
            "id": "worked_here$true",
            "title": "Si",
            "description": ""
        },
        {
            "id": "worked_here$false",
            "title": "No",
            "description": ""
        }
    ]

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,
        message_obj.list_section_title,
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )


def build_schedule_interview_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message with available interview date/time slots.
    Organized by date sections with AM/PM time format
    """
    print("Starting build_schedule_interview_list_message")
    print("candidate_data:", candidate_data)
    print(
        "message_obj.id:", getattr(message_obj, "id", None),
        "type:", getattr(message_obj, "type", None),
        "flow_cta:", getattr(message_obj, "flow_cta", None)
    )

    company_id = candidate_data.get("company_id")
    print("Resolved company_id:", company_id)

    company_data = get_company_screening_data(company_id)
    if not company_data:
        print(f"No screening configuration found for company_id {company_id}")
        return None

    utc_now = datetime.now()
    mexico_now = utc_now - timedelta(hours=6)
    tomorrow = mexico_now.date() + timedelta(days=1)
    start_date = tomorrow.strftime('%Y-%m-%d')
    search_end_date = (tomorrow + timedelta(days=7)).strftime('%Y-%m-%d')
    print("Date window:", start_date, "→", search_end_date)

    all_hours = company_data["interview_hours"]
    max_capacity = company_data.get("max_interviews_per_slot")
    interview_days = company_data.get("interview_days", [])
    unavailable_dates = company_data.get("unavailable_dates", [])
    print(
        "Company config → max_capacity:", max_capacity,
        "interview_days:", interview_days,
        "unavailable_dates:", unavailable_dates
    )

    available_dates = get_available_dates_and_hours(
        company_id,
        start_date,
        search_end_date,
        all_hours,
        max_capacity,
        interview_days,
        unavailable_dates,
        max_days=7
    )
    print("Available dates count:", len(available_dates) if available_dates else 0)

    if not available_dates:
        print(f"No available interview slots for company_id={company_id}")
        return None

    def format_time_ampm(time_24h):
        hour, minute = map(int, time_24h.split(':'))
        period = 'AM' if hour < 12 else 'PM'
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour}:{minute:02d} {period}"

    sections = []
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    total_rows = 0

    for date_info in available_dates:
        date_str = date_info["date"]
        hours = date_info["hours"]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = day_names[date_obj.weekday()]
        month_name = month_names[date_obj.month - 1]
        section_title = f"{day_name} {date_obj.day}- {month_name}"
        rows = []
        row_description = f"{day_name} {date_obj.day} de {month_name}"

        print(f"Processing date {date_str} with {len(hours)} hours")

        for hour_info in hours:
            if hour_info.get("enabled", False):
                hour_24h = hour_info["title"]
                hour_ampm = format_time_ampm(hour_24h)
                slot_id = f"interview_date_time${date_str}T{hour_24h}:00"
                rows.append({
                    "id": slot_id,
                    "title": hour_ampm,
                    "description": row_description
                })
                total_rows += 1
                print(f"Added slot: {hour_ampm} ({slot_id}) → total_rows={total_rows}")
                if total_rows >= 10:
                    print("WhatsApp row limit (10) reached, stopping accumulation")
                    break

        if rows:
            sections.append({"title": section_title, "rows": rows})
            print(f"Added section: {section_title} with {len(rows)} rows")

        if total_rows >= 10:
            break

    if not sections:
        print(f"No sections built for company_id={company_id}")
        return None

    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": text},
            "action": {"button": message_obj.flow_cta, "sections": sections}
        }
    }

    if message_obj.footer_text:
        message["interactive"]["footer"] = {"text": message_obj.footer_text}
    if message_obj.header_type == "text" and message_obj.header_content:
        message["interactive"]["header"] = {"type": "text", "text": message_obj.header_content}

    print(f"Message built with {len(sections)} sections and {total_rows} total rows")
    print("Final payload:", json.dumps(message, indent=2))
    return json.dumps(message)

def get_generic_template_message_with_flow(template_name, candidate_data, message_obj):
    """
    Builds a WhatsApp template message with a Flow button.
    Generic version: only includes the flow_token in the action.
    Does not build flow_action_data.

    Args:
    - template_name (str): Name of the WhatsApp template.
    - candidate_data (dict): Candidate info (must include "wa_id").
    - message_obj: MessageTemplates ORM object (must include flow_keys).

    Returns:
    - str: JSON-encoded message ready for WhatsApp API.
    """

    # Main message structure
    message = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": candidate_data["wa_id"],
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "es_MX"
            },
            "components": []
        }
    }

    # Add body parameters if defined in message_obj
    if message_obj and getattr(message_obj, "variables", None):
        body_component = {
            "type": "body",
            "parameters": []
        }
        for _, field in message_obj.variables.items():
            body_component["parameters"].append({
                "type": "text",
                "text": candidate_data.get(field, "")
            })
        message["template"]["components"].append(body_component)

    # Add flow button (generic, no flow_action_data)
    flow_token = generate_flow_token(message_obj.flow_keys[0])
    flow_button = {
        "type": "button",
        "sub_type": "flow",
        "index": "0",
        "parameters": [
            {
                "type": "action",
                "action": {
                    "flow_token": flow_token
                }
            }
        ]
    }
    message["template"]["components"].append(flow_button)

    logging.info(f'Message Structure: {json.dumps(message)}')
    return json.dumps(message)

def build_company_list_message(candidate_data, message_obj, text):
    """
    Builds a WhatsApp interactive list message showing companies and their available roles.

    Args:
        candidate_data (dict): Candidate info, including 'wa_id'.
        message_obj (MessageTemplates): Template row from DB with WhatsApp config fields.
        text (str): The formatted message text with placeholders already resolved.

    Returns:
        str: JSON-formatted WhatsApp message ready to send.
    """
    logging.info(f'Building List companies message for group_id {candidate_data.get("company_group_id")}')
    companies = get_companies_for_group(candidate_data.get("company_group_id"))
    
    if not companies:
        logging.warning(f"No companies found for group {candidate_data.get('company_group_id')}")
        return None

    roles_by_company = get_roles_grouped_by_company(candidate_data.get("company_group_id"))

    list_options = []
    for company in companies:
        company_id = company["company_id"]
        company_name = company["name"]
        roles = roles_by_company.get(company_id, [])
        roles_str = ", ".join(roles) if roles else "Sin roles disponibles"
        description = roles_str[:72]

        list_options.append({
            "id": f"company_id${company_id}",
            "title": company_name,
            "description": description
        })
    logging.info(f'Company Options: {list_options}')

    return get_list_message_input(
        candidate_data,
        text,
        message_obj.flow_cta,               # e.g. "Seleccionar"
        message_obj.list_section_title,     # e.g. "Empresas disponibles"
        list_options,
        message_obj.footer_text,
        message_obj.header_type,
        message_obj.header_content
    )


#Generate a unique flow identifier
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

    #line breaks
    whatsapp_style_text = whatsapp_style_text.replace('\\n', '\n')

    return whatsapp_style_text
