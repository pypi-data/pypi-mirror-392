import logging
from flask import current_app
import json
from .sql_utils import (store_message, store_screening_answer, store_reference_contact, 
    store_message_reference, update_funnel_state, apply_candidate_updates, save_candidate_grade,
    update_list_reply, update_flow_state, get_eligibility_questions_and_answers, 
    get_company_roles_with_criteria, update_candidate_eligible_roles, handle_role_selection, add_interview_date_time,
    update_screening_rejection, mark_interview_confirmed, log_funnel_state_change, get_candidate_origin,
    get_top5_locations_by_transit, get_roles_for_location_ids, get_top5_locations_by_transit_company, update_candidate_eligible_companies,
    mark_end_flow_rejected)

from .candidate_data import CandidateDataFetcher
from .openai_utils import (get_openai_client, add_msg_to_thread, transcribe_audio, run_assistant_stream, 
                          copy_last_messages_to_new_thread, build_additional_instructions, evaluate_role_eligibility)
from .google_maps import get_location_json
from .whatsapp_utils import get_media_url, download_audio_file_from_meta, get_message_body, send_message, get_nfm_reply_response, send_typing_indicator
from .whatsapp_messages import get_text_message_input, get_keyword_response_from_db
from .media_handler import ScreeningMediaHandler
from baltra_sdk.legacy.dashboards_folder.models import db, QuestionSets, ScreeningQuestions, ScreeningMessages
from .reference_data import ReferenceDataFetcher
import re
from .reference_flow import reference_flow
import threading
from baltra_sdk.shared.mixpanel.metrics_screening import send_funnel_state_mixpanel
from .document_verification import handle_document_verification_message, handle_document_verification_flow

#Defult messages
ERROR_MESSAGE = 'Disculpa, ocurrió un error técnico'
END_CHAT = "Muchas gracias por tu tiempo, si quisieras continuar tu aplicación más tarde nos puedes volver a escribir en cualquier momento"
DEFAULT_WELCOME = "¡Hola! Gracias por contactarnos. Comenzaremos con algunas preguntas para conocerte mejor."
THANK_YOU = "Muchas gracias por tomarte el tiempo de completar el formulario! 🙌"

def run_eligibility_evaluation_background(candidate_data, client, wa_id_system, app_context):
    """
    Background function to evaluate candidate eligibility and send results.
    Runs in a separate thread to avoid blocking the main flow.
    """
    with app_context:
        
        candidate_id = candidate_data.get("candidate_id")
        company_id = candidate_data.get("company_id")
        wa_id_user = candidate_data.get("wa_id")
        
        #set flag to run in progress so it avoids duplicating eligibility runs. Run will be stopped in if existing_eligible_roles:
        update_candidate_eligible_roles(candidate_id,['run_in_progress'])

        try:
            logging.info(f"Starting background eligibility evaluation for candidate {candidate_id}")
            
            # Get all active roles for the company
            company_roles = get_company_roles_with_criteria(company_id)
            
            if not company_roles:
                logging.warning(f"No active roles found for company {company_id}")
                wa_formatted_msg = get_text_message_input(wa_id_user, ERROR_MESSAGE)
                message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], ERROR_MESSAGE, "assistant", client)
                store_message(message_id, candidate_data, sent_by, ERROR_MESSAGE, "")
                send_message(wa_formatted_msg, wa_id_system)
                update_candidate_eligible_roles(candidate_id,[])
                return
            
            # Evaluate candidate against each role
            eligible_role_ids = []
            eligible_role_names = []
            
            for role_data in company_roles:
                # Get eligibility questions and candidate's answers
                questions_and_answers = get_eligibility_questions_and_answers(candidate_id, company_id, role_data)
                
                if not questions_and_answers:
                    logging.warning(f"No eligibility questions found for candidate {candidate_id}, company {company_id}, role_id{role_data['role_id']}")
                    continue

                try:
                    is_eligible = evaluate_role_eligibility(
                        client, 
                        role_data, 
                        questions_and_answers, 
                        candidate_id,
                        company_id
                    )
                    
                    if is_eligible:
                        eligible_role_ids.append(role_data["role_id"])
                        eligible_role_names.append(role_data["role_name"])
                        logging.info(f"Candidate {candidate_id} is eligible for role: {role_data['role_name']} (ID: {role_data['role_id']})")
                    else:
                        logging.info(f"Candidate {candidate_id} is NOT eligible for role: {role_data['role_name']} (ID: {role_data['role_id']})")
                        
                except Exception as e:
                    logging.error(f"Error evaluating role {role_data['role_id']} for candidate {candidate_id}: {e}")
                    continue
            
            # Update candidate's eligible roles in database
            success = update_candidate_eligible_roles(candidate_id, eligible_role_ids)
            
            if not success:
                logging.error(f"Failed to update eligible roles for candidate {candidate_id}")
                wa_formatted_msg = get_text_message_input(wa_id_user, ERROR_MESSAGE)
                message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], ERROR_MESSAGE, "assistant", client)
                store_message(message_id, candidate_data, sent_by, ERROR_MESSAGE, "")
                send_message(wa_formatted_msg, wa_id_system)
                update_candidate_eligible_roles(candidate_id,[])
                return
            
            # Generate results message and role selection
            if eligible_role_ids:
                # Always show role selection for user confirmation (whether 1 or multiple roles)
                try:
                    keyword = candidate_data["next_question"]
                    role_selection_text, role_selection_msg = get_keyword_response_from_db(session=db.session, keyword=keyword, candidate_data=candidate_data)
                    logging.info(f"DEBUGGING: Role selection message lookup - text: {role_selection_text}, msg type: {type(role_selection_msg)}, msg value: {role_selection_msg}")
                    
                    if role_selection_msg and role_selection_text:
                        
                        # ADVANCE QUESTION POSITION - This is the key fix!
                        # Update candidate's current question to point to role selection
                        candidate_data["question_id"] = candidate_data.get('next_question_id')
                        
                        # Update the candidate in database with new position
                        apply_candidate_updates(candidate_id, [{"question_id": candidate_data["question_id"]}])
                        
                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], role_selection_text, "assistant", client)
                        store_message(message_id, candidate_data, sent_by, role_selection_text, "")
                        logging.info(f"DEBUGGING: About to send role selection message - type: {type(role_selection_msg)}, value: {role_selection_msg}")
                        send_message(role_selection_msg, wa_id_system)
                        logging.info(f"Sent role selection message to candidate {candidate_id} for {len(eligible_role_names)} eligible role(s) and advanced question position")
                        return  # Return early since we sent the selection message
                    else:
                        logging.warning(f"No role selection template found for keyword 'select_eligibility_role'. Sending fallback message.")
                except Exception as e:
                    logging.error(f"Error sending role selection message for candidate {candidate_id}: {e}")
            else:
                results_message = "Después de revisar tus respuestas, lamentablemente no calificas para ninguno de los puestos disponibles en este momento. Te agradecemos tu interés y te animamos a aplicar nuevamente en el futuro."
                # Update funnel state to rejected if no eligible roles
                if candidate_data["funnel_state"] == "screening_in_progress": 
                    update_funnel_state(candidate_id, "rejected")
                    candidate_data["funnel_state"] = "rejected"
                    update_screening_rejection(candidate_data["candidate_id"], "No califica para ningún puesto")
                
            logging.info(f"Eligibility evaluation completed for candidate {candidate_id}. Eligible for {len(eligible_role_ids)} roles: {eligible_role_names}")
            
            # Send results message
            wa_formatted_msg = get_text_message_input(wa_id_user, results_message)
            logging.info(f"DEBUGGING: Background thread sending message - wa_formatted_msg type: {type(wa_formatted_msg)}, value: {wa_formatted_msg}")
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], results_message, "assistant", client)
            store_message(message_id, candidate_data, sent_by, results_message, "")
            send_message(wa_formatted_msg, wa_id_system)
            
        except Exception as e:
            logging.error(f"Error in background eligibility evaluation for candidate {candidate_id}: {e}")
            wa_formatted_msg = get_text_message_input(wa_id_user, ERROR_MESSAGE)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], ERROR_MESSAGE, "assistant", client)
            store_message(message_id, candidate_data, sent_by, ERROR_MESSAGE, "")
            send_message(wa_formatted_msg, wa_id_system)
            update_candidate_eligible_roles(candidate_id,[])

# screening_handler.py
# Purpose: Handle the screening conversation flow for a candidate interacting via WhatsApp.

def screening_flow(wa_id_user, message, wa_id_system, whatsapp_msg_id):
    """
    Main entry point for handling screening messages.

    Steps:
    - Parses message type
    - Retrieves or creates candidate and thread info
    - Adds user message to thread
    - Runs classifier assistant to identify intent
    - Depending on intent, either responds or stores answer and proceeds to next question
    - Returns a formatted WhatsApp message to send back

    Parameters:
    - wa_id_user: WhatsApp user ID
    - message: WhatsApp message payload (dict)
    - wa_id_system: WhatsApp system sender ID
    - whatsapp_msg_id: ID of the incoming WhatsApp message

    Returns:
    - Formatted WhatsApp response, message_id, candidate_data, sender role, and raw response
    """
    
    # Initialize OpenAI client for API calls
    client = get_openai_client()

    # Extract message content and type from WhatsApp payload
    message_body, message_type = get_message_body(message)
    
    #Hardcoded reference wa_id is set to Baltra Empresario Whatsapp phone_id (+5215662421576) 
    reference_wa_id = current_app.config["wa_id_ID_owner"]
    #If message was sent to Baltra Empresario Whatsapp phone_id (+5215662421576), then treat converesation asa reference conversation
    if wa_id_system == reference_wa_id:
        reference_data = ReferenceDataFetcher(wa_id_user, client).get_data()
    
        return reference_flow(reference_data, message_body, client, wa_id_user, whatsapp_msg_id)

    # Flag to specific data for candidate_data (role, location, etc)
    data_flag = "none"

    # Fetch or create candidate data including thread and assistant IDs
    candidate_data = CandidateDataFetcher(wa_id_user, client, wa_id_system).get_data()
    if not candidate_data:
        logging.error(f"Candidate data not found or incomplete for {wa_id_user}")
        return None, None, None, None, "error_retrieving_candidate"
    
    #Do not generate a response for whatsapp reactions
    if message_type == "reaction":
        return "<end conversation>", "", candidate_data, "assistant", "<end conversation>"

    # Send whatsapp typing indicator
    send_typing_indicator(wa_id_system, whatsapp_msg_id)
    
    # If message is audio, transcribe it to text
    if message_type == "audio":
        message_body = get_voice_to_text(message)
    
    # If message contains documents/images from WhatsApp Flow, handle based on funnel state
    if message_type == "flow_documents":
        # Check if candidate is in document_verification funnel state
        if candidate_data.get("funnel_state") == "document_verification":
            # Use new document verification flow
            result = handle_document_verification_flow(candidate_data, message_body, wa_id_user, wa_id_system, whatsapp_msg_id, client)
            # If result is None, message was already sent
            if result[0] is None:
                return None, None, None, None, None
            return result
        else:
            # Legacy document upload flow for screening questions
            response, _, _, _, _ = handle_document_upload(candidate_data, message_body, client, wa_id_user, whatsapp_msg_id)
            # Convert to text message and let normal flow continue (treat as "respuesta")
            message_body = response
            message_type = "text"
            
    logging.info(f"Received message of type '{message_type}' with body: {message_body}")    
    logging.debug(f'Candidate Data: {json.dumps(candidate_data)}')
    
    # Check if this whatsapp_msg_id has already been processed to prevent duplicate webhook handling
    if whatsapp_msg_id:
        existing_message = db.session.query(ScreeningMessages).filter_by(whatsapp_msg_id=whatsapp_msg_id).first()
        if existing_message:
            logging.warning(f"⚠️ Duplicate webhook detected for whatsapp_msg_id={whatsapp_msg_id}. Ignoring.")
            return None, None, None, None, None
    
    # Add user message to OpenAI thread for context
    message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], message_body, "user", client)
    logging.debug(f"User message added to OpenAI thread {candidate_data['thread_id']} with ID {message_id}")

    store_message(message_id, candidate_data, sent_by, message_body, whatsapp_msg_id)
    #Handle nfm_reply to schedule interview without going through classifier = respuesta
    if message_type == "nfm_reply":
        data_flag = "nfm_reply"
        response = get_nfm_reply_response(message_body, candidate_data)
        
        # Handle case where selected time slot is full
        if response == "slot_full":
            error_message = "Lo sentimos, el horario que seleccionaste ya no está disponible. Por favor, selecciona otro horario."
            wa_formatted_msg = get_text_message_input(wa_id_user, error_message)
            wa_response = send_message(wa_formatted_msg, wa_id_system)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_message, "assistant", client)
            store_message(message_id, candidate_data, sent_by, error_message, "")
            
            # Resend the appointment booking flow (use the candidate's current question keyword)
            current_question_keyword = candidate_data.get("current_question")
            flow_response_text, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword=current_question_keyword, candidate_data=candidate_data)
            
            if wa_formatted_msg:
                wa_response = send_message(wa_formatted_msg, wa_id_system)
                # For interactive flows, the response text might be None/empty, use a descriptive message instead
                thread_message = flow_response_text if flow_response_text else "Enviando formulario de agendamiento"
                message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], thread_message, "assistant", client)
                store_message(message_id, candidate_data, sent_by, thread_message, "")
                logging.info(f'Slot was full - resent appointment scheduling flow with keyword: {current_question_keyword}')
                # Return early to prevent further processing
                return None, None, None, None, None
            else:
                logging.error(f'Failed to generate appointment scheduling flow for candidate {candidate_data["candidate_id"]} - keyword "{current_question_keyword}" not found in message_templates')
        else:
            wa_formatted_msg = get_text_message_input(wa_id_user, response)
            wa_response = send_message(wa_formatted_msg, wa_id_system)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
            store_message(message_id, candidate_data, sent_by, response, "")
            logging.info(f'nfm_reply response sent') 

    if message_type == "button":
        if message["button"]["payload"] == "confirm-button":
            mark_interview_confirmed(candidate_data["candidate_id"])
        elif message["button"]["payload"] == "reagendar-button":
            response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword="reschedule_interview", candidate_data=candidate_data)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
            return wa_formatted_msg, message_id, candidate_data, sent_by, response

    # Handle list_reply BEFORE checking funnel states - important for rescheduling!
    # List replies (like interview time selection) should be processed regardless of funnel state
    if message_type == "list_reply":
        list_id = message["interactive"]["list_reply"]["id"]
        logging.info(f'List response detected: {list_id}')

        # Handle role selection for eligibility questions
        if (list_id.startswith("role_id$") or list_id == "no_preference"):
            success, selected_role_id, selection_message = handle_role_selection(candidate_data["candidate_id"], list_id)
            candidate_data = CandidateDataFetcher(wa_id_user, client, wa_id_system).get_data()
            
        else:
            # Regular list_reply handling
            confirmation_msg = update_list_reply(list_id, candidate_data)
            
            # If this was an interview scheduling, prepare confirmation and return early
            if confirmation_msg and list_id.startswith("interview_date_time$"):
                # Refresh candidate data
                candidate_data = CandidateDataFetcher(wa_id_user, client, wa_id_system).get_data()
                wa_formatted_msg = get_text_message_input(wa_id_user, confirmation_msg)
                message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], confirmation_msg, "assistant", client)
                store_message(message_id, candidate_data, sent_by, confirmation_msg, "")
                # Don't send here - let whatsapp_utils.py handle sending (normal pattern)
                logging.info(f'Interview confirmation prepared for candidate {candidate_data["candidate_id"]}, returning to whatsapp_utils for sending')
                get_grade(candidate_data, client)
                return wa_formatted_msg, message_id, candidate_data, sent_by, confirmation_msg
            
            # For non-interview list_replies, refresh data and continue to classifier
            candidate_data = CandidateDataFetcher(wa_id_user, client, wa_id_system).get_data()
            logging.info(f'List response updated in DB: {list_id}')

    if candidate_data["funnel_state"] == "document_verification":
        # Handle document verification state with after_flow_assistant
        return handle_document_verification_message(candidate_data, message_body, client, wa_id_user, wa_id_system)
    
    if candidate_data["funnel_state"] == "scheduled_interview" or candidate_data["funnel_state"] == "missed_interview":
        
        # Use post-screening assistant to handle interview-related questions
        response, message_id, sent_by = run_assistant_stream(
            client, 
            candidate_data, 
            current_app.config["POST_SCREENING_ASSISTANT_ID"], 
            build_additional_instructions("post_screening", candidate_data)
        )

        wa_formatted_msg = get_text_message_input(wa_id_user, response)
        #Check if AI response contains a keyword in between <> brackets that need to be overrriden by a template message
        ai_keyword = is_keyword_in_brackets(response)
        if ai_keyword and ai_keyword != 'end conversation':
            response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword=ai_keyword, candidate_data=candidate_data)
        
        return wa_formatted_msg, message_id, candidate_data, sent_by, response
    
    elif candidate_data["funnel_state"] == "verified":
        
        # Use post-screening assistant to handle interview-related questions
        response, message_id, sent_by = run_assistant_stream(
            client, 
            candidate_data, 
            current_app.config["POST_SCREENING_VERIFIED_ASSISTANT_ID"], 
            ""
        )

        wa_formatted_msg = get_text_message_input(wa_id_user, response)
        #Check if AI response contains a keyword in between <> brackets that need to be overrriden by a template message
        ai_keyword = is_keyword_in_brackets(response)
        if ai_keyword and ai_keyword != 'end conversation':
            response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword=ai_keyword, candidate_data=candidate_data)
        
        return wa_formatted_msg, message_id, candidate_data, sent_by, response
    
    if candidate_data["end_flow_rejected"]:
        
        # Use post-screening assistant to handle interview-related questions
        response, message_id, sent_by = run_assistant_stream(
            client, 
            candidate_data, 
            current_app.config["POST_SCREENING_REJECTED_ASSISTANT_ID"], 
            build_additional_instructions("post_screening_rejected", candidate_data)
        )
        wa_formatted_msg = get_text_message_input(wa_id_user, response)
        
        return wa_formatted_msg, message_id, candidate_data, sent_by, response

    #Handle button response edge cases
    if message_type == "button_reply":
        if message["interactive"]["button_reply"]["id"] == "no-button":
            response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword="confirm_exit", candidate_data=candidate_data)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
            return wa_formatted_msg, message_id, candidate_data, sent_by, response
        elif message["interactive"]["button_reply"]["id"] == "yes-exit-button":
            wa_formatted_msg = get_text_message_input(wa_id_user, END_CHAT)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], END_CHAT, "assistant", client)
            return wa_formatted_msg, message_id, candidate_data, sent_by, END_CHAT           

    # Check if this is the first message from a new candidate
    if candidate_data["first_question_flag"]:
        get_candidate_origin(candidate_data["candidate_id"], candidate_data["company_id"])
        log_funnel_state_change(candidate_data["candidate_id"], "", "screening_in_progress")
        send_funnel_state_mixpanel(candidate_data["candidate_id"], "screening_in_progress", candidate_data["company_id"])
        # For first-time candidates, automatically send the first screening question
        keyword = candidate_data["current_question"]
        response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword=keyword, candidate_data=candidate_data) 

        if response is None:
            wa_formatted_msg = get_text_message_input(candidate_data["wa_id"], DEFAULT_WELCOME)
            logging.warning(f"No first question found for candidate {candidate_data['candidate_id']}, using default greeting")
        
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
        logging.info(f"Sent first screening question to new candidate {candidate_data['candidate_id']}")

        candidate_data["current_position"] += 1
    
    else:
        # For returning candidates (not first question), run classifier assistant to determine message intent
        json_response, message_id, sent_by = run_assistant_stream(client, candidate_data, candidate_data['classifier_assistant_id'], build_additional_instructions("classifier", candidate_data))

        # Add error handling for invalid JSON responses
        if not json_response or not json_response.strip():
            logging.error(f"Empty or None response from classifier assistant for user {wa_id_user}")
            wa_formatted_msg = get_text_message_input(wa_id_user, current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"])
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "assistant", client)
            return wa_formatted_msg, message_id, candidate_data, sent_by, current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"]
        #if json_response == "<run_killed_lag>":
            #return "", "", candidate_data, "", "<run_killed_lag>" 
        try:
            classifier_data = json.loads(json_response)
            classifier = classifier_data.get("intent")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response from classifier assistant for user {wa_id_user}: {json_response}. Error: {e}")
            wa_formatted_msg = get_text_message_input(wa_id_user, current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"])
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "assistant", client)
            return wa_formatted_msg, message_id, candidate_data, sent_by, current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"]

        logging.info(f"Classifier intent: {classifier}")

        if classifier == "rechazar_candidato":
            #Update funnel to rejected only if the question has an end_interview_answers that is not null/none/''
            if candidate_data.get("end_interview_answer"):
                update_funnel_state(candidate_data["candidate_id"], "rejected")
                candidate_data["funnel_state"] = "rejected"
                update_screening_rejection(candidate_data["candidate_id"], candidate_data.get("current_question","No Identificado"))
            #Classifier is updated to respuesta to carry on with interview 
            classifier = "respuesta"
            logging.info(f'Rejected candidate due to game stopper answer')
        
        if classifier in ["aclaracion", "pregunta"]:
            # For questions or clarifications, use general purpose assistant
            response, message_id, sent_by = run_assistant_stream(client, candidate_data, candidate_data['general_purpose_assistant_id'], build_additional_instructions("candidate", candidate_data))
            wa_formatted_msg = get_text_message_input(wa_id_user, response)
            logging.info("Handled intent with general purpose assistant")
        
        elif classifier =="interrumpir_chat":
            response = END_CHAT
            wa_formatted_msg = get_text_message_input(wa_id_user, END_CHAT)
            logging.info("interrumpir_chat found, trigger hardcoded response")
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], END_CHAT, "assistant", client)
            
        elif classifier == "respuesta":
            #if current response type is location, use google maps function to get distance to company and travel time. Save this information to the answer_json column.
            # if type voice, save message body in answer raw and answer json. (decidir si esto tiene sentido)
            json_body = None
            
            #Check the state of the previous question to determine which question to fire next
            if candidate_data["flow_state"] in ["respuesta", "aclaracion"]:
                # Handle location questions - either from WhatsApp location or text address
                if candidate_data.get("current_response_type") in ["location", "location_critical"]:
                    json_body = get_location_json(candidate_data, message, message_body, message_type)
                    
                    # Check if there was an error processing the location
                    if json_body and json_body.get("error"):
                        logging.error(f"Location processing error for candidate {candidate_data['candidate_id']}: {json_body}")
                        
                        # Provide user-friendly error message based on error type
                        if json_body.get("error") == "address_not_found":
                            error_response = "No pude encontrar esa dirección. ¿Podrías intentar con una dirección más específica? Por ejemplo: 'Calle 123, Colonia, Ciudad'"
                        elif json_body.get("error") == "geocoding_failed":
                            error_response = "Hubo un problema al procesar tu dirección. ¿Podrías intentar de nuevo con una dirección más detallada?"
                        elif json_body.get("error") == "no_location_data":
                            error_response = "No recibí información de ubicación. Por favor comparte tu ubicación usando el botón de ubicación de WhatsApp o escribe tu dirección completa."
                        else:
                            error_response = "Hubo un problema al procesar tu ubicación. ¿Podrías intentar de nuevo?"
                        
                        # Send error message and return early without storing the answer
                        wa_formatted_msg = get_text_message_input(wa_id_user, error_response)
                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_response, "assistant", client)
                        return wa_formatted_msg, message_id, candidate_data, sent_by, error_response
                    
                    data_flag = "location"  

                    # If this is a location_critical question, compute nearest roles by transit
                    if candidate_data.get("current_response_type") == "location_critical":
                        try:
                            # Extract candidate coordinates from json_body
                            def extract_coords(d: dict):
                                emp = d.get("employee_coordinates") or {}
                                if emp and emp.get("latitude") is not None and emp.get("longitude") is not None:
                                    return float(emp["latitude"]), float(emp["longitude"]) 
                                pos = d.get("position") or {}
                                if pos and pos.get("lat") is not None and pos.get("lng") is not None:
                                    return float(pos["lat"]), float(pos["lng"])
                                return None

                            coords = extract_coords(json_body or {})
                            if coords:
                                lat, lon = coords
                                if candidate_data.get("company_id"):
                                    top5 = get_top5_locations_by_transit(lat, lon, company_id=candidate_data["company_id"]) or []
                                    
                                    # Check if the response indicates all locations are too far
                                    if top5 and len(top5) == 1 and top5[0].get("rejection_reason") == "all_locations_too_far":
                                        # All locations are too far - reject candidate
                                        rejection_message = top5[0].get("message", "No contamos con vacantes a menos de 3 horas de tu ubicacion")
                                        mark_end_flow_rejected(candidate_data["candidate_id"])
                                        update_funnel_state(candidate_data["candidate_id"], "rejected")
                                        candidate_data["funnel_state"] = "rejected"
                                        update_screening_rejection(candidate_data["candidate_id"], "Muy lejos de vacante")
                                        
                                        # Send rejection message and return early
                                        wa_formatted_msg = get_text_message_input(wa_id_user, rejection_message)
                                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], rejection_message, "assistant", client)
                                        return wa_formatted_msg, message_id, candidate_data, sent_by, rejection_message
                                    
                                    elif top5:
                                        location_ids = [int(x["location_id"]) for x in top5]
                                        loc_roles = get_roles_for_location_ids(candidate_data["company_id"], location_ids)

                                        nearest_roles = []
                                        for item in top5:
                                            role_info = loc_roles.get(int(item["location_id"]))
                                            if role_info:
                                                nearest_roles.append({
                                                    "role_id": role_info["role_id"],
                                                    "role_name": role_info["role_name"],
                                                    "eta_seconds": item.get("eta_seconds"),
                                                })

                                        if nearest_roles:
                                            candidate_data["nearest_roles"] = nearest_roles
                                            top_role_ids = [r["role_id"] for r in nearest_roles][:5]
                                            update_candidate_eligible_roles(candidate_data["candidate_id"], top_role_ids)
                                            candidate_data["eligible_roles"] = top_role_ids
                                            logging.info(
                                                f"Nearest roles (by transit) set for candidate {candidate_data['candidate_id']}: {nearest_roles}"
                                            )
                                elif candidate_data.get("company_group_id"):
                                    top5 = get_top5_locations_by_transit_company(lat, lon, company_group_id=candidate_data["company_group_id"])
                                    
                                    # Check if the response indicates all companies are too far
                                    if top5 and len(top5) == 1 and top5[0].get("rejection_reason") == "all_companies_too_far":
                                        # All companies are too far - reject candidate
                                        rejection_message = top5[0].get("message", "No contamos con vacantes a menos de 3 horas de tu ubicacion")
                                        mark_end_flow_rejected(candidate_data["candidate_id"])
                                        update_funnel_state(candidate_data["candidate_id"], "rejected")
                                        candidate_data["funnel_state"] = "rejected"
                                        update_screening_rejection(candidate_data["candidate_id"], "Muy lejos de vacante")
                                        
                                        # Send rejection message and return early
                                        wa_formatted_msg = get_text_message_input(wa_id_user, rejection_message)
                                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], rejection_message, "assistant", client)
                                        return wa_formatted_msg, message_id, candidate_data, sent_by, rejection_message
                                    
                                    elif top5:
                                        nearest_companies = []
                                        for item in top5:
                                            nearest_companies.append({
                                                "company_id": item["company_id"],
                                                "name": item["name"],
                                                "eta_seconds": item.get("eta_seconds"),
                                            })
                                        if nearest_companies:
                                            candidate_data["nearest_companies"] = nearest_companies
                                            top_company_ids = [r["company_id"] for r in nearest_companies][:5]
                                            update_candidate_eligible_companies(candidate_data["candidate_id"], top_company_ids)
                                            
                                            # Create readable log message with travel times in minutes
                                            readable_companies = []
                                            for company in nearest_companies:
                                                eta_seconds = company.get("eta_seconds")
                                                if eta_seconds is not None:
                                                    try:
                                                        # Ensure eta_seconds is numeric (handle both int and string cases)
                                                        eta_seconds_num = float(eta_seconds) if isinstance(eta_seconds, str) else eta_seconds
                                                        eta_minutes = eta_seconds_num / 60
                                                        readable_companies.append({
                                                            "company_id": company["company_id"],
                                                            "name": company["name"],
                                                            "travel_time": f"{eta_minutes:.1f} minutes"
                                                        })
                                                    except (ValueError, TypeError) as e:
                                                        logging.warning(f"Invalid eta_seconds value for company {company.get('company_id')}: {eta_seconds} (type: {type(eta_seconds)})")
                                                        readable_companies.append({
                                                            "company_id": company["company_id"],
                                                            "name": company["name"],
                                                            "travel_time": "Unknown"
                                                        })
                                                else:
                                                    readable_companies.append({
                                                        "company_id": company["company_id"],
                                                        "name": company["name"],
                                                        "travel_time": "Unknown"
                                                    })
                                            
                                            logging.info(f"✅ Nearest companies (≤200min) set for candidate {candidate_data['candidate_id']}: {readable_companies}")
                                        
                        except Exception as e:
                            logging.error(f"Nearest roles computation failed for candidate {candidate_data['candidate_id']}: {e}")
            
                elif message_type == "location":
                    # Fallback for legacy location handling if response type not set
                    json_body = get_location_json(candidate_data, message, message_body, message_type)
                    
                    # Check for errors in fallback case too
                    if json_body and json_body.get("error"):
                        logging.error(f"Location processing error (fallback) for candidate {candidate_data['candidate_id']}: {json_body}")
                        error_response = "Hubo un problema al procesar tu ubicación. ¿Podrías intentar de nuevo?"
                        wa_formatted_msg = get_text_message_input(wa_id_user, error_response)
                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_response, "assistant", client)
                        return wa_formatted_msg, message_id, candidate_data, sent_by, error_response
                        
                    data_flag = "location"

                if candidate_data["current_response_type"] == "phone_reference":
                    contact_reference(candidate_data, message_body, client)
                
                store_screening_answer(candidate_data, message_body, json_body, data_flag)
                next_question_type = candidate_data.get('next_question_response_type')
            
                #Conditional to switch between question sets (example: from general set to role specific set)
                #Checks if there is a next question and if there is a next set_id that is distinct
                if next_question_type == None and candidate_data.get("next_set_id") != candidate_data.get("set_id"):
                    next_question_type = candidate_data.get('next_set_first_question_type')
                    candidate_data["set_id"] = candidate_data["next_set_id"]
                    candidate_data["next_question_id"] = candidate_data["next_set_first_question_id"]
                    candidate_data["next_question"] = candidate_data["next_set_first_question"] 

            #This is triggered when the current classifier is respuesta, but a question earliear
            #had a different state like aclaración o cregunta
            else:
                next_question_type = candidate_data.get("current_response_type", "")    
                candidate_data["next_question_id"] = candidate_data.get("question_id", "")
                candidate_data["next_question"] = candidate_data.get("current_question")
            
            if next_question_type in ['text', 'phone_reference', 'name']:
                response = candidate_data.get('next_question')
                if response is None:
                    response = THANK_YOU
                    get_grade(candidate_data, client)
                wa_formatted_msg = get_text_message_input(wa_id_user, response)
            elif next_question_type in ['location', 'interactive', 'location_critical']:
                keyword = candidate_data.get('next_question')

                if keyword == 'select_eligibility_role' or keyword == 'select_eligibility_role_integer' or keyword == 'select_eligibility_role_generic':
                    # Check if candidate already has eligible roles to avoid re-evaluation
                    existing_eligible_roles = candidate_data.get('eligible_roles', [])
                    
                    if existing_eligible_roles:
                        # Candidate already has eligible roles, skip evaluation and proceed with normal flow
                        logging.info(f"Candidate {candidate_data['candidate_id']} already has eligible roles: {existing_eligible_roles}. Skipping re-evaluation.")
                    else:
                        # Candidate doesn't have eligible roles yet, run evaluation
                        logging.info(f"Triggering  eligibility evaluation for candidate {candidate_data['candidate_id']} (no existing eligible roles)")
                        # Send initial message and start eligibility evaluation in background
                        if candidate_data['company_id'] == 3:
                            response = "¡Muchas gracias por completar las preguntas iniciales! 🙌\n\nAhora vamos a analizar tus respuestas para determinar qué puestos son los más adecuados para ti. Te enviaremos los resultados en un momento... ⏳"
                        else: #Company 6
                            response = "¡Muchas gracias por completar todas las preguntas! 🙌\n\nAhora vamos a analizar tus respuestas para determinar qué puestos son los más adecuados para ti. Te enviaremos los resultados en un momento... ⏳"
                        wa_formatted_msg = get_text_message_input(wa_id_user, response)
                        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
                        update_flow_state(candidate_data, classifier)
                        
                        # Start eligibility evaluation in background thread
                        threading.Thread(
                            target=run_eligibility_evaluation_background, 
                            args=(candidate_data, client, wa_id_system, current_app.app_context())
                        ).start()
                        
                        logging.info(f"Started eligibility evaluation process for candidate {candidate_data['candidate_id']}")
                        
                        # Return early to send wait for eligibility evaluation message
                        return wa_formatted_msg, message_id, candidate_data, sent_by, response
                if keyword is None:
                    response = THANK_YOU
                    wa_formatted_msg = get_text_message_input(wa_id_user, response)
                    get_grade(candidate_data, client)
                else:
                    response, wa_formatted_msg = get_keyword_response_from_db(session=db.session, keyword=keyword, candidate_data=candidate_data)
            
            else:
                # End of questions - standard completion message
                response = THANK_YOU
                get_grade(candidate_data, client)
                wa_formatted_msg = get_text_message_input(wa_id_user, response)    

            # Proceed to next question
            candidate_data["question_id"] = candidate_data.get('next_question_id')
            logging.debug(f"Candidate data after incrementing position: {candidate_data}")
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
            logging.info("Stored answer and moved to next question")

        else:
            logging.warning(f"Unhandled intent '{classifier}' for user {wa_id_user}")
            response = current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"]
            wa_formatted_msg = get_text_message_input(wa_id_user, response)
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
        threading.Thread(target=update_data, args=(client, candidate_data, current_app.app_context())).start()
        update_flow_state(candidate_data, classifier)
    
    # Add debugging for return values
    logging.info(f"DEBUGGING: screening_flow final return - wa_formatted_msg type: {type(wa_formatted_msg)}, value: {wa_formatted_msg}")
    logging.info(f"DEBUGGING: screening_flow final return - response: {response}")
    return wa_formatted_msg, message_id, candidate_data, sent_by, response

#AI driven database update based on new messages
def update_data(client, candidate_data, app_context):
    # Use the Flask app context so DB sessions and config are available
    with app_context:
        # Create a new thread with the last 3 messages (or fewer if not enough)
        candidate_data["thread_id"] = copy_last_messages_to_new_thread(client, candidate_data["thread_id"])

        # Run the assistant using the updated thread_id and get the response
        updates_json, message_id, sent_by = run_assistant_stream(client, candidate_data, current_app.config["UPDATE_DB_ASSISTANT_ID"], build_additional_instructions("update_database", candidate_data))

        # Try to parse the JSON response from the assistant
        try:
            updates = json.loads(updates_json)
            logging.info(f'Updates to Candidates Table: {updates}')
        except json.JSONDecodeError:
            logging.error(f"[update_data] Failed to parse assistant response: {updates_json}")
            return  # Exit early on JSON parsing failure

        # Check if the assistant returned any updates to apply
        if updates.get("updates"):
            # Apply the updates to the candidate record
            updated_fields = apply_candidate_updates(candidate_data["candidate_id"], updates["updates"])

            # Log what fields were updated, or log if no updates were made
            if updated_fields:
                logging.info(f"[update_data] Candidate {candidate_data['candidate_id']} updated fields: {updated_fields}")

def get_voice_to_text(message: dict):
    """
    Returns the transcription of the audio message.

    Args:
    - employee_data (dict): Contains employee information such as the candidate ID and company ID.
    - message (dict): The message object containing the location data.

    Returns:
    - dict: A JSON object with the transcription of the audio message.    
    """
    media_id = message.get('audio').get('id')
    
    meta_download_url = get_media_url(media_id)

    audio_from_meta, ext = download_audio_file_from_meta(meta_download_url)

    transcription = transcribe_audio(audio_from_meta, ext)
    logging.info(f"Transcription: {transcription}")

    if transcription:
        return transcription
    
    return None
    
def contact_reference(candidate_data, message_body, client):
    """
    Extracts contact reference from a WhatsApp message payload.
    Args:
    - message_body (str): The message body containing the contact reference.

    Returns:
    - None   
    """    
    reference_wa_id = message_body
    
    reference_wa_id = re.sub(r'[^0-9]', '', reference_wa_id)  # Remove everything except numbers
    if reference_wa_id.startswith("521") and len(reference_wa_id) == 13:
        pass  # Already normalized
    elif reference_wa_id.startswith("52") and len(reference_wa_id) == 12:
        reference_wa_id = "521" + reference_wa_id[2:]
    else:
        reference_wa_id = "521" + reference_wa_id

    
    store_reference_contact(candidate_data, reference_wa_id)
    logging.info(f"[contact_reference] Stored reference contact for {reference_wa_id}")
    
    reference_data = ReferenceDataFetcher(reference_wa_id, client).get_data()
    
    text, formatted_response = get_keyword_response_from_db(session=db.session , keyword="contact_reference", candidate_data=reference_data)
    
    message_id, sent_by = add_msg_to_thread(reference_data['thread_id'], text, "assistant", client)
    
    status_response = send_message(formatted_response, current_app.config["wa_id_ID_owner"], "reference_check")
    
    if status_response.status_code == 200:
        response_text = json.loads(status_response.text)
        whatsapp_msg_id = response_text['messages'][0]['id']
        
        if 'reference_id' in reference_data:
            try:
                store_message_reference(message_id, reference_data, sent_by, text, whatsapp_msg_id)
                logging.info(f"[contact_reference] Stored message for reference_id={reference_data['reference_id']}")
            except Exception as e:
                logging.error(f"[contact_reference] Error storing message for reference_id={reference_data['reference_id']}: {e}")
        else:
            logging.warning(f"[contact_reference] reference_id not in reference_data: {reference_data}")
    
    return status_response

def get_grade(candidate_data, client):
    grade_json, message_id, sent_by = run_assistant_stream(client, candidate_data, current_app.config["CANDIDATE_GRADING_ASSISTANT_ID"])
    try:
        experience_grade = json.loads(grade_json)
        experience_numeric_grade = float(experience_grade.get("grade_experience", 0))
        dependents_numeric_grade = float(experience_grade.get("grade_dependents", 0))

        logging.info(f'Grade based on previous experience: {experience_numeric_grade}/100')
        logging.info(f'Grade based on dependents: {dependents_numeric_grade}/100')
    except json.JSONDecodeError:
        logging.error(f"[update_data] Failed to parse assistant response: {grade_json}")
        return

    travel_time_grade = travel_time_score(candidate_data.get("travel_time_minutes"))
    logging.info(f'Grade based on travel time: {travel_time_grade}/100')

    total_grade = int(50 + 0.20 * travel_time_grade + 0.25 * experience_numeric_grade + 0.00 * dependents_numeric_grade)
    save_candidate_grade(candidate_data["candidate_id"], total_grade)

def handle_document_upload(candidate_data, flow_data, client, wa_id_user, whatsapp_msg_id):
    """
    Handle document/image uploads from WhatsApp Flow.
    Immediately acknowledges receipt and processes documents in background.
    
    Args:
        candidate_data (dict): Candidate information
        flow_data (dict): Flow response containing images/documents
        client: OpenAI client
        wa_id_user (str): WhatsApp user ID
        whatsapp_msg_id (str): WhatsApp message ID
        
    Returns:
        tuple: (wa_formatted_msg, message_id, candidate_data, sent_by, response)
    """
    try:
        logging.info(f"Processing document upload for candidate {candidate_data['candidate_id']}")
        
        # Count documents received
        image_count = len(flow_data.get('images', []))
        doc_count = len(flow_data.get('documents', []))
        total_count = image_count + doc_count
        
        # Send immediate processing message
        processing_msg = f"📄 Recibí {total_count} documento(s). Los estoy verificando, esto puede tomar unos segundos..."
        
        # Start background processing (don't wait for it)
        # Don't store screening answer here - let normal flow handle it
        threading.Thread(
            target=process_documents_background, 
            args=(candidate_data.copy(), flow_data, current_app.app_context())
        ).start()
        
        # Return processing message that will be treated as user response by classifier
        response = processing_msg
        
        logging.info(f"Document upload acknowledged for candidate {candidate_data['candidate_id']}, processing in background")
        return response, None, candidate_data, "user", response
        
    except Exception as e:
        logging.error(f"Error handling document upload for candidate {candidate_data['candidate_id']}: {e}")
        error_response = "❌ Hubo un problema al recibir tus documentos. Por favor contacta al equipo de soporte."
        return error_response, None, candidate_data, "user", error_response

def process_documents_background(candidate_data, flow_data, app_context):
    """
    Legacy function for processing documents in screening flow (non-verification flow).
    Only handles regular document upload without verification.
    """
    with app_context:
        try:
            logging.info(f"Starting background document processing for candidate {candidate_data['candidate_id']} (legacy flow)")
            
            # Small delay to ensure the normal flow has stored the initial answer
            import time
            time.sleep(2)
            
            # Process the media files
            media_handler = ScreeningMediaHandler()
            results = media_handler.process_flow_media(candidate_data, flow_data)
            
            flow_token = flow_data.get('flow_token', 'request_documents')
            
            if results['processed_count'] > 0:
                # No verification for legacy flow - just upload to S3
                answer_text = f"Documentos procesados: {results['processed_count']} archivo(s) subidos exitosamente a S3"
                json_data = {
                    "media_count": results['processed_count'],
                    "media_ids": results['media_ids'],
                    "flow_token": flow_token,
                    "processing_status": "completed",
                    "failed_count": results.get('failed_count', 0),
                    "s3_processed": True
                }
                
                if results.get('failed_count', 0) > 0:
                    answer_text += f" ({results['failed_count']} fallaron)"
                    json_data["errors"] = results.get('errors', [])
                    
            else:
                answer_text = f"Error procesando documentos: todos los archivos fallaron"
                json_data = {
                    "media_count": 0,
                    "flow_token": flow_token,
                    "processing_status": "failed",
                    "errors": results.get('errors', []),
                    "s3_processed": False
                }
            
            # Update the existing screening answer
            store_screening_answer(candidate_data, answer_text, json_data, "document_upload")
            
            logging.info(f"✅ Background document processing completed for candidate {candidate_data['candidate_id']}: "
                        f"{results['processed_count']} successful, {results.get('failed_count', 0)} failed")
            
        except Exception as e:
            logging.error(f"❌ Error in background document processing for candidate {candidate_data['candidate_id']}: {e}")
            
            # Update with error status
            error_answer = f"Error procesando documentos: {str(e)}"
            error_json = {
                "processing_status": "error",
                "error_message": str(e),
                "flow_token": flow_data.get('flow_token', 'request_documents'),
                "s3_processed": False
            }
            store_screening_answer(candidate_data, error_answer, error_json, "document_upload")

def travel_time_score(m):
    try:
        m = float(m)
    except (TypeError, ValueError):
        return 0  # Fallback: assign 0 points if missing or invalid

    if m <= 30:
        return 100
    if m >= 180:
        return 0
    return 100 * (1 - (m - 30) / 150)

#Function to check if there is a keyword wrapped in <>, function is used after ai agent generates a response
def is_keyword_in_brackets(message_body):
    """Return the text inside < > brackets if present."""
    logging.debug(f'Checking for keywords in brackets, this is the message body. {message_body}')
    match = re.search(r'<([^>]+)>', message_body)
    return match.group(1) if match else None
    
