import logging
import json
import threading
import time
from flask import current_app
from baltra_sdk.legacy.dashboards_folder.models import db, CandidateMedia, ScreeningAnswers, Candidates
from baltra_sdk.shared.utils.document_verification.tu_identidad_api import TuIdentidadAPI
from baltra_sdk.shared.utils.screening.media_handler import ScreeningMediaHandler
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input, get_keyword_response_from_db
from baltra_sdk.shared.utils.screening.whatsapp_utils import send_message
from baltra_sdk.shared.utils.screening.openai_utils import get_openai_client, add_msg_to_thread, run_assistant_stream, build_additional_instructions
from baltra_sdk.shared.utils.screening.sql_utils import store_message, update_funnel_state

def handle_document_verification_flow(candidate_data, flow_data, wa_id_user, wa_id_system, whatsapp_msg_id, client):
    """
    Main handler for document verification flow when candidate is in 'document_verification' funnel state.
    Processes RFC string and INE images, performs verification, and updates candidate status.
    
    Args:
        candidate_data (dict): Candidate information
        flow_data (dict): Flow response containing RFC string and INE images
        wa_id_user (str): WhatsApp user ID
        wa_id_system (str): WhatsApp system sender ID
        whatsapp_msg_id (str): WhatsApp message ID
        client: OpenAI client
        
    Returns:
        tuple: (wa_formatted_msg, message_id, candidate_data, sent_by, response)
    """
    try:
        logging.info(f"Starting document verification flow for candidate {candidate_data['candidate_id']}")
        
        # Send immediate acknowledgment message
        processing_msg = "Gracias! Estamos procesando tus documentos, te mandaremos un respuesta en 30 segundos"
        wa_formatted_msg = get_text_message_input(wa_id_user, processing_msg)
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], processing_msg, "assistant", client)
        store_message(message_id, candidate_data, sent_by, processing_msg, "")
        
        # Send the immediate response
        send_message(wa_formatted_msg, wa_id_system)
        
        # Start background verification process
        threading.Thread(
            target=process_document_verification_background,
            args=(candidate_data.copy(), flow_data, wa_id_system, current_app.app_context())
        ).start()
        
        logging.info(f"Document verification process started for candidate {candidate_data['candidate_id']}")
        return None, None, None, None, None  # Return None since we already sent the message
        
    except Exception as e:
        logging.error(f"Error handling document verification flow for candidate {candidate_data['candidate_id']}: {e}")
        error_response = "❌ Hubo un problema al recibir tus documentos. Por favor contacta al equipo de soporte."
        wa_formatted_msg = get_text_message_input(wa_id_user, error_response)
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_response, "assistant", client)
        return wa_formatted_msg, message_id, candidate_data, sent_by, error_response

def process_document_verification_background(candidate_data, flow_data, wa_id_system, app_context):
    """
    Background process for document verification.
    Processes RFC string and INE images, performs verification via Tu Identidad API.
    """
    with app_context:
        try:
            logging.info(f"Starting background document verification for candidate {candidate_data['candidate_id']}")
            
            # Small delay to ensure message delivery
            time.sleep(2)
            
            candidate_id = candidate_data['candidate_id']
            wa_id_user = candidate_data['wa_id']
            client = get_openai_client()
            
            # Extract RFC and images from flow data
            rfc_string = flow_data.get('RFC', '').strip()
            images = flow_data.get('images', [])
            
            # Validate input data
            if not rfc_string or len(rfc_string) != 13:
                _send_verification_failure_message(
                    candidate_data, wa_id_system, client,
                    f"RFC inválido: debe tener exactamente 13 caracteres. RFC recibido: '{rfc_string}'"
                )
                return
            
            if len(images) < 2:
                _send_verification_failure_message(
                    candidate_data, wa_id_system, client,
                    f"Se requieren 2 imágenes del INE (frente y reverso). Recibidas: {len(images)}"
                )
                return
            
            # Process INE images to S3
            ine_results = _process_ine_images(candidate_data, images)
            if not ine_results['success']:
                _send_verification_failure_message(
                    candidate_data, wa_id_system, client,
                    f"Error procesando imágenes del INE: {ine_results['error']}"
                )
                return
            
            # Store RFC string in database
            rfc_media_id = _store_rfc_string(candidate_id, rfc_string)
            if not rfc_media_id:
                _send_verification_failure_message(
                    candidate_data, wa_id_system, client,
                    "Error almacenando RFC en base de datos"
                )
                return
            
            # Perform RFC and INE verifications
            verification_results = _perform_verifications(
                rfc_string, 
                ine_results['front_url'], 
                ine_results['back_url']
            )
            
            # Extract CURP from successful INE verification and verify CURP+NSS
            curp_string = None
            curp_media_id = None
            nss_media_id = None
            
            if verification_results['ine']['verified']:
                # Extract CURP from INE verification result
                ine_data = verification_results['ine']['result'].get('data', {})
                curp_string = ine_data.get('curp', '').strip()
                
                if curp_string and len(curp_string) == 18:
                    logging.info(f"Extracted CURP from INE: {curp_string}")
                    
                    # Store CURP in database
                    curp_media_id = _store_curp_string(candidate_id, curp_string)
                    
                    # Perform CURP+NSS verification
                    curp_nss_results = _perform_curp_nss_verification(curp_string)
                    verification_results['curp'] = curp_nss_results['curp']
                    verification_results['nss'] = curp_nss_results['nss']
                    
                    # Store NSS tracking info
                    nss_verification_id = curp_nss_results['nss']['verification_id']
                    if nss_verification_id:
                        nss_media_id = _store_nss_tracking(candidate_id, nss_verification_id)
                else:
                    logging.warning(f"Invalid or missing CURP from INE verification: '{curp_string}'")
                    verification_results['curp'] = {
                        'verified': False,
                        'result': {'error': 'No CURP válido extraído del INE'},
                        'message': '❌ CURP no extraído del INE'
                    }
                    verification_results['nss'] = {
                        'verified': False,
                        'result': {'error': 'No se pudo verificar NSS sin CURP válido'},
                        'message': '❌ NSS no verificado (sin CURP)',
                        'verification_id': None
                    }
            else:
                # INE failed, so we can't get CURP
                verification_results['curp'] = {
                    'verified': False,
                    'result': {'error': 'INE verification failed'},
                    'message': '❌ CURP no disponible (INE falló)'
                }
                verification_results['nss'] = {
                    'verified': False,
                    'result': {'error': 'INE verification failed'},
                    'message': '❌ NSS no disponible (INE falló)',
                    'verification_id': None
                }
            
            # Update database with verification results (including CURP and NSS if available)
            _update_verification_results(
                rfc_media_id,
                ine_results['media_ids'],
                verification_results,
                curp_media_id,
                nss_media_id
            )
            
            # Check if critical verifications passed (RFC, INE, CURP)
            # NSS is not critical since it's asynchronous
            rfc_verified = verification_results['rfc']['verified']
            ine_verified = verification_results['ine']['verified']
            curp_verified = verification_results.get('curp', {}).get('verified', False)
            
            if rfc_verified and ine_verified and curp_verified:
                # Critical verifications successful (NSS status doesn't matter for user flow)
                success_message = "¡Verificamos tus documentos exitosamente!"
                _send_verification_success_message(candidate_data, wa_id_system, client, success_message)
                
                # Update candidate funnel state to verified
                update_funnel_state(candidate_id, "verified")
                logging.info(f"✅ Document verification successful for candidate {candidate_id} (RFC+INE+CURP), funnel state updated to 'verified'")
                
                # Log NSS status for HR review
                nss_status = verification_results.get('nss', {})
                nss_verification_id = nss_status.get('verification_id')
                if nss_verification_id:
                    logging.info(f"📋 NSS verification initiated for candidate {candidate_id}, verification_id: {nss_verification_id}")
                else:
                    logging.warning(f"⚠️ NSS verification not initiated for candidate {candidate_id}")
                
            else:
                # One or more critical verifications failed
                error_details = []
                if not rfc_verified:
                    error_details.append(f"RFC: {verification_results['rfc']['message']}")
                if not ine_verified:
                    error_details.append(f"INE: {verification_results['ine']['message']}")
                if not curp_verified:
                    error_details.append(f"CURP: {verification_results['curp']['message']}")
                
                error_message = "❌ " + " | ".join(error_details)
                logging.error(f"Document verification failed for candidate {candidate_id}: {error_message}")
                
                _send_verification_failure_message(candidate_data, wa_id_system, client, error_message)
            
        except Exception as e:
            logging.error(f"❌ Error in background document verification for candidate {candidate_data['candidate_id']}: {e}")
            _send_verification_failure_message(
                candidate_data, wa_id_system, client,
                f"Error interno en verificación: {str(e)}"
            )

def _process_ine_images(candidate_data, images):
    """
    Process INE images and upload to S3.
    
    Args:
        candidate_data (dict): Candidate information
        images (list): List of image objects from WhatsApp flow
        
    Returns:
        dict: Processing results with S3 URLs and media IDs
    """
    try:
        # Create fake flow data for media handler
        fake_flow_data = {
            'images': images,
            'documents': [],
            'flow_token': 'documents_INE_verification'
        }
        
        media_handler = ScreeningMediaHandler()
        results = media_handler.process_flow_media(candidate_data, fake_flow_data)
        
        if results['processed_count'] < 2:
            return {
                'success': False,
                'error': f"Solo se procesaron {results['processed_count']} de 2 imágenes requeridas"
            }
        
        # Get the uploaded media details
        media_files = _get_candidate_media_by_ids(candidate_data['candidate_id'], results['media_ids'])
        
        if len(media_files) < 2:
            return {
                'success': False,
                'error': "No se pudieron obtener las URLs de S3 de las imágenes"
            }
        
        return {
            'success': True,
            'front_url': media_files[0]['s3_url'],
            'back_url': media_files[1]['s3_url'],
            'media_ids': results['media_ids']
        }
        
    except Exception as e:
        logging.error(f"Error processing INE images: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _store_rfc_string(candidate_id, rfc_string):
    """
    Store RFC string in candidate_media table.
    
    Args:
        candidate_id (int): Candidate ID
        rfc_string (str): RFC string (13 characters)
        
    Returns:
        int or None: Media ID if successful, None if failed
    """
    try:
        new_media = CandidateMedia(
            candidate_id=candidate_id,
            media_type='text',
            media_subtype='RFC',
            string_submission=rfc_string,
            verified=False
        )
        
        db.session.add(new_media)
        db.session.commit()
        
        logging.info(f"RFC string stored for candidate {candidate_id}: {rfc_string}")
        return new_media.media_id
        
    except Exception as e:
        logging.error(f"Error storing RFC string for candidate {candidate_id}: {e}")
        db.session.rollback()
        return None

def _store_curp_string(candidate_id, curp_string):
    """
    Store CURP string in candidate_media table.
    
    Args:
        candidate_id (int): Candidate ID
        curp_string (str): CURP string (18 characters)
        
    Returns:
        int or None: Media ID if successful, None if failed
    """
    try:
        new_media = CandidateMedia(
            candidate_id=candidate_id,
            media_type='text',
            media_subtype='CURP',
            string_submission=curp_string,
            verified=False
        )
        
        db.session.add(new_media)
        db.session.commit()
        
        logging.info(f"CURP string stored for candidate {candidate_id}: {curp_string}")
        return new_media.media_id
        
    except Exception as e:
        logging.error(f"Error storing CURP string for candidate {candidate_id}: {e}")
        db.session.rollback()
        return None

def _store_nss_tracking(candidate_id, verification_id):
    """
    Store NSS verification tracking info in candidate_media table.
    
    Args:
        candidate_id (int): Candidate ID
        verification_id (str): NSS verification ID from API
        
    Returns:
        int or None: Media ID if successful, None if failed
    """
    try:
        new_media = CandidateMedia(
            candidate_id=candidate_id,
            media_type='text',
            media_subtype='NSS',
            string_submission=verification_id,  # Store verification ID for tracking
            verified=False  # Will be updated via webhook
        )
        
        db.session.add(new_media)
        db.session.commit()
        
        logging.info(f"NSS tracking stored for candidate {candidate_id}: verification_id={verification_id}")
        return new_media.media_id
        
    except Exception as e:
        logging.error(f"Error storing NSS tracking for candidate {candidate_id}: {e}")
        db.session.rollback()
        return None

def _perform_curp_nss_verification(curp_string):
    """
    Perform CURP+NSS verification using Tu Identidad API.
    
    Args:
        curp_string (str): CURP string to verify
        
    Returns:
        dict: Verification results for both CURP and NSS tracking
    """
    try:
        api = TuIdentidadAPI()
        
        # Perform CURP+NSS verification
        curp_nss_verified, curp_nss_result = api.verify_curp_nss(curp_string)
        
        # Extract CURP data and NSS verification ID
        curp_data = curp_nss_result.get('curpData', {})
        nss_data = curp_nss_result.get('nssData', {})
        verification_id = nss_data.get('verificationId')
        
        # Generate CURP validation message
        curp_message = api.get_validation_message(curp_nss_result, "CURP")
        
        return {
            'curp': {
                'verified': curp_nss_verified and curp_data.get('valid', False),
                'result': curp_data,
                'message': curp_message
            },
            'nss': {
                'verified': False,  # Always False initially (async process)
                'result': nss_data,
                'message': f"📋 NSS verification initiated: {verification_id}" if verification_id else "❌ NSS verification not initiated",
                'verification_id': verification_id
            }
        }
        
    except Exception as e:
        logging.error(f"Error performing CURP+NSS verification: {e}")
        return {
            'curp': {
                'verified': False,
                'result': {'error': str(e)},
                'message': f"Error en verificación CURP: {str(e)}"
            },
            'nss': {
                'verified': False,
                'result': {'error': str(e)},
                'message': f"Error en verificación NSS: {str(e)}",
                'verification_id': None
            }
        }

def _perform_verifications(rfc_string, front_image_url, back_image_url):
    """
    Perform both RFC and INE verifications using Tu Identidad API.
    
    Args:
        rfc_string (str): RFC string to verify
        front_image_url (str): S3 URL of INE front image
        back_image_url (str): S3 URL of INE back image
        
    Returns:
        dict: Verification results for both RFC and INE
    """
    try:
        api = TuIdentidadAPI()
        
        # Perform RFC verification with string
        rfc_verified, rfc_result = api.verify_rfc_string(rfc_string)
        rfc_message = api.get_validation_message(rfc_result, "RFC")
        
        # Perform INE verification with images
        ine_verified, ine_result = api.verify_ine_documents(front_image_url, back_image_url)
        ine_message = api.get_validation_message(ine_result, "INE")
        
        return {
            'rfc': {
                'verified': rfc_verified,
                'result': rfc_result,
                'message': rfc_message
            },
            'ine': {
                'verified': ine_verified,
                'result': ine_result,
                'message': ine_message
            }
        }
        
    except Exception as e:
        logging.error(f"Error performing verifications: {e}")
        return {
            'rfc': {
                'verified': False,
                'result': {'error': str(e)},
                'message': f"Error en verificación RFC: {str(e)}"
            },
            'ine': {
                'verified': False,
                'result': {'error': str(e)},
                'message': f"Error en verificación INE: {str(e)}"
            }
        }

def _update_verification_results(rfc_media_id, ine_media_ids, verification_results, curp_media_id=None, nss_media_id=None):
    """
    Update candidate_media records with verification results.
    
    Args:
        rfc_media_id (int): Media ID for RFC record
        ine_media_ids (list): Media IDs for INE images
        verification_results (dict): Verification results from API
        curp_media_id (int, optional): Media ID for CURP record
        nss_media_id (int, optional): Media ID for NSS tracking record
    """
    try:
        # Update RFC record
        rfc_media = db.session.query(CandidateMedia).filter_by(media_id=rfc_media_id).first()
        if rfc_media:
            rfc_media.verified = verification_results['rfc']['verified']
            rfc_media.verification_result = verification_results['rfc']['result']
        
        # Update INE records
        for media_id in ine_media_ids:
            ine_media = db.session.query(CandidateMedia).filter_by(media_id=media_id).first()
            if ine_media:
                ine_media.verified = verification_results['ine']['verified']
                ine_media.verification_result = verification_results['ine']['result']
                ine_media.media_subtype = 'INE'  # Ensure INE images are properly tagged
        
        # Update CURP record if available
        if curp_media_id and 'curp' in verification_results:
            curp_media = db.session.query(CandidateMedia).filter_by(media_id=curp_media_id).first()
            if curp_media:
                curp_media.verified = verification_results['curp']['verified']
                curp_media.verification_result = verification_results['curp']['result']
        
        # Update NSS tracking record if available
        if nss_media_id and 'nss' in verification_results:
            nss_media = db.session.query(CandidateMedia).filter_by(media_id=nss_media_id).first()
            if nss_media:
                # NSS is always False initially (async process)
                nss_media.verified = False
                nss_media.verification_result = verification_results['nss']['result']
        
        db.session.commit()
        
        update_info = f"RFC media_id {rfc_media_id}, INE media_ids {ine_media_ids}"
        if curp_media_id:
            update_info += f", CURP media_id {curp_media_id}"
        if nss_media_id:
            update_info += f", NSS media_id {nss_media_id}"
        
        logging.info(f"Updated verification results for {update_info}")
        
    except Exception as e:
        logging.error(f"Error updating verification results: {e}")
        db.session.rollback()

def _send_verification_success_message(candidate_data, wa_id_system, client, message):
    """
    Send verification success message to candidate.
    """
    try:
        wa_id_user = candidate_data['wa_id']
        wa_formatted_msg = get_text_message_input(wa_id_user, message)
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], message, "assistant", client)
        store_message(message_id, candidate_data, sent_by, message, "")
        send_message(wa_formatted_msg, wa_id_system)
        
        logging.info(f"Sent verification success message to candidate {candidate_data['candidate_id']}")
        
    except Exception as e:
        logging.error(f"Error sending verification success message: {e}")

def _send_verification_failure_message(candidate_data, wa_id_system, client, error_message):
    """
    Send verification failure message and resend documents_INE template.
    """
    try:
        wa_id_user = candidate_data['wa_id']
        candidate_id = candidate_data['candidate_id']
        
        # Send error message
        wa_formatted_msg = get_text_message_input(wa_id_user, error_message)
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_message, "assistant", client)
        store_message(message_id, candidate_data, sent_by, error_message, "")
        send_message(wa_formatted_msg, wa_id_system)
        
        # Wait a moment before sending the template again
        time.sleep(3)
        
        # Resend documents_INE template
        response, wa_formatted_msg = get_keyword_response_from_db(
            session=db.session, 
            keyword="documents_INE", 
            candidate_data=candidate_data
        )
        
        if response and wa_formatted_msg:
            message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], response, "assistant", client)
            store_message(message_id, candidate_data, sent_by, response, "")
            send_message(wa_formatted_msg, wa_id_system)
            
            logging.info(f"Resent documents_INE template to candidate {candidate_id} after verification failure")
        else:
            logging.error(f"Failed to get documents_INE template for candidate {candidate_id}")
        
    except Exception as e:
        logging.error(f"Error sending verification failure message: {e}")

def _get_candidate_media_by_ids(candidate_id, media_ids):
    """
    Get candidate media records by IDs.
    
    Args:
        candidate_id (int): Candidate ID
        media_ids (list): List of media IDs
        
    Returns:
        list: List of media records with S3 URLs
    """
    try:
        media_records = db.session.query(CandidateMedia).filter(
            CandidateMedia.candidate_id == candidate_id,
            CandidateMedia.media_id.in_(media_ids)
        ).all()
        
        return [
            {
                'media_id': record.media_id,
                's3_url': record.s3_url,
                'media_type': record.media_type,
                'media_subtype': record.media_subtype
            }
            for record in media_records
        ]
        
    except Exception as e:
        logging.error(f"Error getting candidate media by IDs: {e}")
        return []

def handle_document_verification_message(candidate_data, message_body, client, wa_id_user, wa_id_system):
    """
    Handle regular text messages when candidate is in document_verification funnel state.
    Uses after_flow_assistant instead of classifier/general_purpose assistant.
    
    Args:
        candidate_data (dict): Candidate information
        message_body (str): Message content
        client: OpenAI client
        wa_id_user (str): WhatsApp user ID
        wa_id_system (str): WhatsApp system sender ID
        
    Returns:
        tuple: (wa_formatted_msg, message_id, candidate_data, sent_by, response)
    """
    try:
        # Use after_flow_assistant for document verification state
        response, message_id, sent_by = run_assistant_stream(
            client, 
            candidate_data, 
            current_app.config["POST_SCREENING_ASSISTANT_ID"], 
            build_additional_instructions("after_flow", candidate_data)
        )
        
        wa_formatted_msg = get_text_message_input(wa_id_user, response)
        
        # Check if AI response contains a keyword in brackets that needs template override
        from baltra_sdk.shared.utils.screening.screening_flow import is_keyword_in_brackets
        ai_keyword = is_keyword_in_brackets(response)
        if ai_keyword and ai_keyword != 'end conversation':
            response, wa_formatted_msg = get_keyword_response_from_db(
                session=db.session, 
                keyword=ai_keyword, 
                candidate_data=candidate_data
            )
        
        logging.info(f"Handled document verification message with after_flow_assistant for candidate {candidate_data['candidate_id']}")
        return wa_formatted_msg, message_id, candidate_data, sent_by, response
        
    except Exception as e:
        logging.error(f"Error handling document verification message for candidate {candidate_data['candidate_id']}: {e}")
        error_response = "❌ Hubo un problema procesando tu mensaje. Por favor intenta de nuevo."
        wa_formatted_msg = get_text_message_input(wa_id_user, error_response)
        message_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], error_response, "assistant", client)
        return wa_formatted_msg, message_id, candidate_data, sent_by, error_response
