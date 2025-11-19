from .openai_utils import add_msg_to_thread, run_assistant_stream, build_additional_instructions
from .whatsapp_messages import get_text_message_input
from .sql_utils import store_message_reference, store_reference_assessment, save_answer_json, update_candidate_grade
import logging
import json

def reference_flow(reference_data, message_body, client, wa_id_user, whatsapp_msg_id):
    
    message_id, sent_by = add_msg_to_thread(reference_data["thread_id"], message_body, "user", client)
    store_message_reference(message_id, reference_data, sent_by, message_body, whatsapp_msg_id)
    
    if reference_data["candidate_id"] == 9999:
        fallback_msg = "✨ Gracias por escribirnos.\n📱 Este número es administrado por Baltra para ayudar a las empresas a hacer chequeos de referencias laborales de sus candidatos.\n❗ Parece que aún no estás vinculado como referencia.\n👉 Por favor, asegúrate que el candidato haya compartido tu número correctamente.\n💬 Si quieres conocer más sobre Baltra, escríbenos a info@baltra.ai.\n¡Gracias por tu tiempo! 🙌"
        wa_formatted_msg = get_text_message_input(wa_id_user, fallback_msg)
        message_id, sent_by = add_msg_to_thread(reference_data["thread_id"], fallback_msg, "assistant", client)
        return wa_formatted_msg, message_id, reference_data, sent_by, fallback_msg
    
    response, message_id, sent_by = run_assistant_stream(client, reference_data, reference_data['reference_assistant'],build_additional_instructions("reference_context", reference_data))
    wa_formatted_msg = get_text_message_input(wa_id_user, response)
    
    # Run classifier assistant to get recommendation if interaction is over
    json_response, message_id, sent_by = run_assistant_stream(client, reference_data, reference_data['reference_classifier'])
    
    try:
        classifier_data = json.loads(json_response)
        classifier = classifier_data.get("continue")
        logging.debug(f"Classifier assistant response: {json_response}")
        logging.info(f"Classifier intent: {classifier}")
    except Exception as e:
        logging.error(f"Error parsing classifier JSON: {e}")
        classifier = None

    if classifier is False:
        store_reference_assessment(reference_data["reference_id"], classifier_data)
        save_answer_json(reference_data["candidate_id"], reference_data["question_id"], classifier_data)
        update_candidate_grade(reference_data["candidate_id"], classifier_data.get("recommendation_score"))

    return wa_formatted_msg, message_id, reference_data, sent_by, response
