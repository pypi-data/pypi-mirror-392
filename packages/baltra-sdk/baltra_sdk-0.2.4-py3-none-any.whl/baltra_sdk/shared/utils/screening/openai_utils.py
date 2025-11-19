from openai import OpenAI, APITimeoutError, AssistantEventHandler
from datetime import datetime, timedelta
import openai
import time
from flask import current_app
import logging
import json
import tempfile
from typing import Optional
from typing_extensions import override
from .sql_utils import log_response_time, get_active_roles_for_company, get_message_text_by_keyword, insert_openai_run_status, get_run_status, log_eligibility_evaluation
from baltra_sdk.infra.screening.services.conversation_run_state import (
    set_active_run,
    clear_active_run,
    is_cancel_requested,
    reset_conversation_state,
)
import threading

#get openai client with API key
def get_openai_client():
    """
    Initialize and return an OpenAI client using the API key from the app config.
    """
    client = OpenAI(api_key = current_app.config["OPENAI_KEY_SCREENING"]) #set client with API key
    return client

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
        except openai.APITimeoutError:
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

        except openai.APITimeoutError:
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

#Run openai assistant with streaming
def run_assistant_stream(client, candidate_data, assistant_id, additional_instructions = ""):
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
    thread_id = candidate_data["thread_id"]
    conversation_id = candidate_data.get("conversation_id")
    temp_message_ids = candidate_data.get("_temp_message_ids") or []
    conversation_priority = candidate_data.get("conversation_priority")

    def _mark_cancelled() -> None:
        if isinstance(candidate_data, dict):
            candidate_data["_cancelled_run"] = True

    if isinstance(candidate_data, dict):
        candidate_data["_cancelled_run"] = False

    # If there's a pending cancellation, skip before doing any work
    if conversation_id and is_cancel_requested(conversation_id):
        logging.info(
            "[run_assistant_stream] Cancel requested for conversation %s before starting run (assistant=%s).",
            conversation_id,
            assistant_id,
        )
        reset_conversation_state(conversation_id, temp_message_ids=temp_message_ids)
        _mark_cancelled()
        return "", "cancelled", "assistant"

    # Ensure the thread has no active runs before proceeding
    if not wait_for_free_run(client, thread_id):
        logging.error(
            "[run_assistant_stream] Unable to acquire free run for conversation %s thread=%s; resetting state.",
            conversation_id,
            thread_id,
        )
        if conversation_id:
            reset_conversation_state(conversation_id, temp_message_ids=temp_message_ids)
            _mark_cancelled()
            return "", "cancelled", "assistant"
        return current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "error", "assistant"

    max_attempts = 5
    cancelled_after_stream = False
    for attempt in range(max_attempts):
        try:
            start_time = datetime.now()
            handler = EventHandler()
            run_id = None
            try:
                if conversation_id and is_cancel_requested(conversation_id):
                    logging.info(
                        "[run_assistant_stream] Cancel requested for conversation %s before streaming run (assistant=%s).",
                        conversation_id,
                        assistant_id,
                    )
                    logging.info(
                        "[run_assistant_stream] Cancel requested mid-stream for conversation %s; resetting before run.",
                        conversation_id,
                    )
                    reset_conversation_state(conversation_id, temp_message_ids=temp_message_ids)
                    _mark_cancelled()
                    return "", "cancelled", "assistant"
                with client.beta.threads.runs.stream(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    additional_instructions=additional_instructions,
                    event_handler=handler,
                ) as stream:
                    run_id = _extract_run_id_from_stream(stream)
                    if run_id is None:
                        run_id = _lookup_active_run_id(client, thread_id)
                    if conversation_id and run_id:
                        logging.debug(
                            "[run_assistant_stream] Registering run %s for conversation %s (priority=%s)",
                            run_id,
                            conversation_id,
                            conversation_priority,
                        )
                        set_active_run(conversation_id, thread_id, run_id, conversation_priority)
                    elif conversation_id:
                        logging.warning(
                            "[run_assistant_stream] Failed to capture run_id for conversation %s; cancellation disabled.",
                            conversation_id,
                        )
                    stream.until_done()

                    # After streaming finishes, fetch the latest assistant message metadata
                    messages = client.beta.threads.messages.list(thread_id=thread_id, timeout=30)
                    assistant_messages = [m for m in messages.data if m.role == "assistant"]
                    if not assistant_messages:
                        raise Exception("No assistant messages found after streaming.")
                    last_message = assistant_messages[0]

                    if conversation_id and is_cancel_requested(conversation_id):
                        logging.info(
                            "[run_assistant_stream] Cancel requested after streaming run %s for conversation %s; rewinding context.",
                            run_id,
                            conversation_id,
                        )
                        reset_conversation_state(
                            conversation_id,
                            temp_message_ids=temp_message_ids,
                            extra_openai_ids=[last_message.id],
                        )
                        _mark_cancelled()
                        cancelled_after_stream = True
                        return "", "cancelled", "assistant"

                    end_time = datetime.now()
                    time_delta = (end_time - start_time).total_seconds()
                    usage = stream.current_run.usage
                    model = stream.current_run.model or "unknown"
                    prompt_tokens = usage.prompt_tokens if usage and hasattr(usage, "prompt_tokens") else 0
                    completion_tokens = usage.completion_tokens if usage and hasattr(usage, "completion_tokens") else 0
                    total_tokens = usage.total_tokens if usage and hasattr(usage, "total_tokens") else 0

                    log_response_time(
                        candidate_data,
                        start_time,
                        end_time,
                        time_delta,
                        assistant_id,
                        model,
                        prompt_tokens,
                        completion_tokens,
                        total_tokens,
                    )

                    if isinstance(candidate_data, dict):
                        candidate_data["_cancelled_run"] = False
                    return last_message.content[0].text.value, last_message.id, last_message.role
            finally:
                if conversation_id and run_id and not cancelled_after_stream:
                    clear_active_run(conversation_id, run_id)

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
                f"[run_assistant_stream] Critical error encountered: {critical_error} - Employee ID: {candidate_data['candidate_id']} - Thread ID: {thread_id}"
            )
            break

    # Fallback response if all attempts fail
    return current_app.config["RESPONSE_TO_WHATSAPP_ISSUE"], "error", "assistant"


def _extract_run_id_from_stream(stream) -> Optional[str]:
    for attr in ("response", "_response", "current_run"):
        obj = getattr(stream, attr, None)
        if obj is None:
            continue
        run_id = getattr(obj, "id", None)
        if run_id:
            return run_id
    return None


def _lookup_active_run_id(client, thread_id: str) -> Optional[str]:
    try:
        runs = client.beta.threads.runs.list(thread_id=thread_id, limit=5)
    except Exception:  # noqa: BLE001
        logging.exception("[run_assistant_stream] Failed to fetch runs for thread %s", thread_id)
        return None
    logging.debug(
        "[run_assistant_stream] Lookup run_id thread=%s results=%s",
        thread_id,
        [getattr(run, "id", None) for run in runs.data],
    )
    for run in runs.data:
        if getattr(run, "status", None) in {"queued", "in_progress"}:
            return getattr(run, "id", None)
    return runs.data[0].id if runs.data else None

def transcribe_audio(audio_bytes: bytes, suffix=".mp3") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as audio_file:
            openai = get_openai_client()
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
    return transcription.text

#Function to copy last messages to a new thread to analyze for data
def copy_last_messages_to_new_thread(client, original_thread_id, max_messages=5):
    """
    Create a new thread containing the last N messages from the original thread.

    Args:
        client: OpenAI client instance
        original_thread_id: ID of the thread to copy messages from
        max_messages: number of most recent messages to include

    Returns:
        new_thread_id (str): ID of the new thread containing copied messages
    """
    try:
        # 1. Fetch all messages from the original thread
        messages = client.beta.threads.messages.list(thread_id=original_thread_id, limit=100)
        sorted_messages = sorted(messages.data, key=lambda m: m.created_at)

        # 2. Get last N messages (or fewer if not enough)
        last_messages = sorted_messages[-max_messages:]

        # 3. Create a new thread
        new_thread = client.beta.threads.create()
        new_thread_id = new_thread.id

        # 4. Re-add messages to new thread in original order
        for msg in last_messages:
            for block in msg.content:
                if block.type == "text":
                    client.beta.threads.messages.create(
                        thread_id=new_thread_id,
                        role=msg.role,
                        content=block.text.value
                    )

        return new_thread_id

    except Exception as e:
        logging.error(f"[copy_last_messages_to_new_thread] Failed: {e}")
        return None
    
def build_additional_instructions(instruction_type, candidate_data):
    """
    Builds the additional_instructions string based on the assistant's purpose.

    Args:
        instruction_type (str): One of "candidate", "update_database", "classifier", "post_screening"
        candidate_data (dict): Info about the candidate, including current_question, company_context, etc.
        roles_list (list[dict], optional): Required for "update_database" type, 
                                           should include role_id and role_name.

    Returns:
        str: A formatted string to pass as additional_instructions.
    """

    if instruction_type == "candidate":
        # Parse the JSON string from candidate_data
        company_ctx = candidate_data.get("company_context", "{}")
        try:
            company_ctx_json = json.loads(company_ctx)
        except json.JSONDecodeError:
            company_ctx_json = {}

        # Pick only the fields you need
        filtered_company_ctx = {
            "Descripción": company_ctx_json.get("Descripción", "No disponible"),
            "Beneficios": company_ctx_json.get("Beneficios", "No disponible"),
            "Preguntas_Frecuentes": company_ctx_json.get("Preguntas_Frecuentes", "No disponible"),
            "Ubicación_Vacante": company_ctx_json.get("Ubicación_Vacante", "")
        }

        return f"""
        Pregunta actual: {candidate_data.get("current_question", "No se encontró la pregunta actual")}
        Contexto de la empresa: {filtered_company_ctx}
        Contexto del rol: {candidate_data.get("role_context", "No se encontró el contexto del rol")}
        """.strip()

    elif instruction_type == "update_database":
        roles_list = get_active_roles_for_company(candidate_data['company_id'])
        if not roles_list:
            return "No se proporcionó información de los roles disponibles."
        # Remove 'shift' key from each role dict
        roles_list_no_shift = [
            {k: v for k, v in role.items() if k != "shift"} for role in roles_list
        ]

        return f"""
        Lista de roles activos. Usa esta información para identificar el puesto que menciona el candidato:
        roles_list: {json.dumps(roles_list_no_shift, ensure_ascii=False)}
        """.strip()
    
    elif instruction_type == "classifier":
        pregunta_actual = candidate_data.get("current_question", "No se encontró la pregunta actual")
        if candidate_data.get("current_response_type", "text") == "interactive":
            pregunta_actual = get_message_text_by_keyword(pregunta_actual)

        return f"""
        pregunta_actual: {pregunta_actual}
        tipo_respuesta: {candidate_data.get("current_response_type", "text")}
        respuestas_rechazar_candidato: {candidate_data.get("end_interview_answer", "")}
        ejemplo_respuestas_validas: {candidate_data.get("example_answer", "")}
        """.strip()

    elif instruction_type == "post_screening":

        interview_address = candidate_data.get("interview_address", "")

        company_context = json.loads(candidate_data.get("company_context", "{}"))
        company_description = company_context.get("Descripción", "")
        company_address = company_context.get("Ubicación_Vacante", "")
        company_benefits = company_context.get("Beneficios", "")
        company_general_faq = company_context.get("Preguntas_Frecuentes", "")
        interview_days = company_context.get("Dias_Entrevista", "")
        interview_hours = company_context.get("Horarios_Entrevista", "")
        hr_contact = company_context.get("hr_contact", "")
        hr_contact_line = f"- Contacto de RH en caso de que el candidato este expresando problemas con la entrevista: {hr_contact}" if hr_contact else ""
        
        return f"""
        El candidato {candidate_data.get("first_name", "")} completó la aplicación y tiene una entrevista programada.
        
        Información de la empresa:
        - Nombre: {candidate_data.get("company_name", "No disponible")}
        - Descripción: {company_description}
        - Beneficios: {company_benefits}
        - Preguntas Frecuentes: {company_general_faq}
        
        Información del puesto:
        - Rol: {candidate_data.get("role", "No especificado")}
        - {candidate_data.get("role_context", "No se encontró información del rol")}
        
        Información de la entrevista:
        - Fecha y hora: {candidate_data.get("interview_date", "No programada")}
        - Dirección: {interview_address}

        Si el candidato menciona que llegará tarde, recuérdale que no hay problema, pero debe considerar los siguientes días y horarios disponibles::
        - Días de Entrevista: {interview_days}
        - Horarios de Entrevista: {interview_hours} 
        - Fecha y Hora Actual: {({ 'Monday':'Lunes','Tuesday':'Martes','Wednesday':'Miércoles','Thursday':'Jueves','Friday':'Viernes','Saturday':'Sábado','Sunday':'Domingo' })[(datetime.now() - timedelta(hours=6)).strftime('%A')]}, {(datetime.now() - timedelta(hours=6)).strftime('%d/%m/%Y %I:%M %p')}

        Información adicional:
        - Tiempo de viaje estimado: {candidate_data.get("travel_time_minutes", "No calculado")} minutos
        {hr_contact_line}
        """.strip()

    elif instruction_type == "post_screening_rejected":

        company_context = json.loads(candidate_data.get("company_context", "{}"))
        company_description = company_context.get("Descripción", "")
        company_benefits = company_context.get("Beneficios", "")
        company_general_faq = company_context.get("Preguntas_Frecuentes", "")
        
        return f"""
        El candidato {candidate_data.get("first_name", "")} ha completado el proceso de screening y la compañía esta evaluando si hay una vacante disponible.
        
        Información de la empresa:
        - Nombre: {candidate_data.get("company_name", "No disponible")}
        - Descripción: {company_description}
        - Beneficios: {company_benefits}
        - Preguntas Frecuentes: {company_general_faq}
        
        Información del puesto:
        - Rol: {candidate_data.get("role", "No especificado")}
        - Contexto del rol: {candidate_data.get("role_context", "No se encontró información del rol")}        
        """.strip()

    elif instruction_type == "reference_context":
        phone = candidate_data.get("company_phone", "No disponible")
        if phone.startswith("521") and len(phone) == 13:
            phone = "52" + phone[3:]

        return f"""
        Información de la empresa que solicita la referencia:
        - Nombre de la empresa: {candidate_data.get("company_name", "Desconocido")}
        - Teléfono para aplicar: {phone}
        - Descripción: {candidate_data.get("company_context", "Sin descripción")}
        - Beneficios ofrecidos: {candidate_data.get("company_benefits", "No especificados")}
        - Dirección de entrevista: {candidate_data.get("interview_address_json", "No proporcionada")}
        """.strip()

    else:
        return ""

def evaluate_role_eligibility(client, role_data: dict, questions_and_answers: dict, candidate_id: int, company_id: int):
    """
    Uses OpenAI assistant to evaluate if a candidate is eligible for a specific role
    based on their answers to eligibility questions.
    
    Args:
        client: OpenAI client instance
        role_data (dict): Dictionary containing role_id, role_name, and eligibility_criteria
        questions_and_answers (dict): Dictionary of eligibility questions and candidate answers
        candidate_id (int): The candidate's ID for logging
        
    Returns:
        bool: True if candidate is eligible for the role, False otherwise
    """
    try:
        # Create a new thread for this evaluation
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Get role criteria
        eligibility_criteria = role_data.get('eligibility_criteria', {})
        
        # Build clear criteria analysis section
        criteria_analysis = ""
        criteria_count = 0
        
        for question_id, criteria_requirement in eligibility_criteria.items():
            criteria_count += 1
            question_data = questions_and_answers.get(str(question_id), {})
            
            question_text = question_data.get('question_text', 'Pregunta no encontrada')
            answer_text = question_data.get('answer_text', 'No respondido')
            
            criteria_analysis += f"""
CRITERIO {criteria_count}:
• REQUISITO: {criteria_requirement}
• PREGUNTA: {question_text}
• RESPUESTA DEL CANDIDATO: {answer_text}
• EVALUACIÓN: [Pendiente]

"""

        # Build comprehensive evaluation prompt with mathematical examples
        evaluation_prompt = f"""
Evalúa siguiendo las reglas de elegibilidad ya definidas.

=== INFORMACIÓN DEL PUESTO ===
Nombre del puesto: {role_data['role_name']}
ID del puesto: {role_data['role_id']}

=== CRITERIOS DE ELEGIBILIDAD ===
{criteria_analysis}
        """
        
        # Add the evaluation prompt to the thread
        message_id, sent_by = add_msg_to_thread(thread_id, evaluation_prompt, "user", client)
        
        if message_id == "error":
            logging.error(f"Failed to add evaluation prompt to thread for candidate {candidate_id}, role {role_data['role_id']}")
            return False
        
        # Use the dedicated eligibility assistant
        eligibility_assistant_id = current_app.config["ELEGIBILITY_ASSISTANT_ID"]  
        
        try:
            # Run the assistant to get the evaluation
            json_response, response_message_id, response_sent_by = run_assistant_stream(
                client, 
                {"thread_id": thread_id, "candidate_id": candidate_id}, 
                eligibility_assistant_id
            )
            
            # Parse the JSON response
            evaluation_result = json.loads(json_response)
            is_eligible = evaluation_result.get("eligible", "No se pudo evaluar la elegibilidad")
            reasoning = evaluation_result.get("reasoning", "No reasoning provided")
            
            # Log detailed results
            detailed_log = f"Candidate {candidate_id} eligibility for role {role_data['role_name']} ({role_data['role_id']}): {is_eligible}"
            detailed_log += f"\nOverall reasoning: {reasoning}"
            logging.info(detailed_log)
            
            # Log to database for quality control tracking
            try:
                log_eligibility_evaluation(
                    candidate_id=candidate_id,
                    company_id=company_id,
                    role_data=role_data,
                    questions_and_answers=questions_and_answers,
                    evaluation_result=evaluation_result,
                    assistant_id=eligibility_assistant_id,
                    thread_id=thread_id
                )
            except Exception as log_error:
                logging.error(f"Failed to log eligibility evaluation for candidate {candidate_id}, role {role_data['role_id']}: {log_error}")
                # Don't fail the evaluation if logging fails
            
            return is_eligible
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse eligibility evaluation JSON for candidate {candidate_id}, role {role_data['role_id']}. Response: {json_response}. Error: {e}")
            return False
        except Exception as e:
            logging.error(f"Error during assistant evaluation for candidate {candidate_id}, role {role_data['role_id']}: {e}")
            return False
            
    except Exception as e:
        logging.error(f"Error in role eligibility evaluation for candidate {candidate_id}, role {role_data['role_id']}: {e}")
        return False

