from typing import Optional, Dict, Any

SCREENING_SPECS: Dict[str, Dict[str, Any]] = {
    # To be created
    "welcome": {
        "response_type": "interactive",
        "template": "welcome_{company_name}",
        "example_answer": "Sí, Si, Continuar, Adelante, Acepto Empezar",
        "end_interview_answer": "No",
        "message_template":{
            "type": "interactive",
            "interactive_type": "button",
            "button_keys": [["yes-button", "Sí"], ["no-button", "No"]],
            "text": (
                "Hola! Soy Bal de {company_name}, {company_description}.\n\n"
                "Estamos contratando {roles}.\n\n"
                "Ofrecemos:\n{beneficios_lista}\n\n"
                "¿Quieres conocer más sobre las vacantes?\n"
                "Responde SÍ para continuar y recibir los detalles."
            ),
            "footer_text": "Aviso de Privacidad: https://www.baltra.ai/privacidad",
            "company_name": "{company_id}"
        }
    },
    "name": {
        "response_type": "text",
        "template": "Perfecto! Haremos algunas preguntas para conocerte mejor.\n\nPrimero, cuál es tu nombre completo?",
        "example_answer": "Juan Perez; Me llamo Juan Perez;",
    },
    "age": {
        "response_type": "text",
        "template": "Cuál es tu edad?",
        "example_answer": "25 años, 30, 35 años, tengo 30 años",
        "end_interview_answer": "Menos de {edad_min} o Mayor a {edad_max} años",
    },
    "education": {
        "response_type": "interactive",
        "template": "nivel_educacion",
        "example_answer": "Licenciatura, Ninguno, Primaria, Preparatoria Técnica, Secundaria, Preparatoria",
        "end_interview_answer": "{dependiendo de la selección del usuario}"
    },
    "shifts": {
        "response_type": "text",
        "template": "Tienes disponibilidad para {si turnos son rotativos: Rotar Turnos X a X/Si turnos fon fijos: Para trabajar turno fijo de X a X}. Lo pregunto porque es necesario para las vacantes disponibles",
        "example_answer": "Si, Zi, Simón, Claro, Sin problema, Sip, Si puedo",
        "end_interview_answer": "No, No puedo trabajar ese turno, No puedo {turno fijo/turno rotativo}",
    },
    "certifications_general": {
        "response_type": "text",
        "template": "Cuentas con la certificación de {certName}?",
        "interactive_type": "button",
        "example_answer": "Si, No, Si la tengo, No la tengo",
        "end_interview_answer": "{dependiendo de la selección del usuario}",
    },
    "select_role": {
        "response_type": "interactive",
        "template": "select_role",
        "interactive_type": "button",
        "example_answer": "{lista de roles disponibles separada con ,}",
    },
    "location": {
        "response_type": "interactive",
        "template": "ask_location",
        "example_answer": "Av Patito 123, Miguel Hidalgo, Ciudad de México; colonia juarez; Latitud 20, Longitud 20",
    },
    "experience": {
        "response_type": "text",
        "template": "Cuéntanos sobre tu experiencia relacionada con esta vacante: cuántos años has trabajado y en qué roles? \n\nPuedes responder por texto o nota de voz",
        "example_answer": "No tengo experiencia previa; Trabajé en Mcdonald's por 3 años como cajero y en la empresa Brinco por dos años como ayudante",
    },
    "references": {
        "response_type": "phone_reference",
        "template": "Si lo tienes a la mano, me puedes compartir el teléfono de alguien con quien hayas trabajado (exjefe o compañero)? Es solo para una referencia sencilla sobre tu experiencia laboral",
        "example_answer": "5543235678; no; no quiero dar una referencia; no tengo referencia;Juan Pérez 555-123-4567; Ana López 555-987-6543.",
    },
    "last12months": {
        "response_type": "text",
        "template": "Cuántos trabajos has tenido en los últimos 12 meses?",
        "example_answer": "1, 2, 3 trabajos, Ninguno, uno",
        "end_interview_answer": "Más de {max_trabajos_permitidos} trabajos"
    },
    "documents": {
        "response_type": "text",
        "template": "Tienes disponible la siguiente papelería? Se requiere solo en caso de ingreso. \n1️⃣ Si\n2️⃣ No\n\n {docsList}?",
        "example_answer": " Si; Claro; Sin problema; Si los tengo; 1; 1️⃣; Simon; Sip; Sipi; Claro; Cualquier variacion de si o una afirmación; Tengo copias; Si los tengo en la casa; Ahorita no los tengo a la mano;",
        "end_interview_answer": "{dependiendo de la selección del usuario}"
    },
    "bank": {
        "response_type": "text",
        "template": "Pagamos la nómina únicamente por {banco}. Si aún no tienes cuenta, no te preocupes, nosotros te ayudamos a abrirla para que recibas tu salario sin problema. Estás de acuerdo?\n1️⃣ Sí\n2️⃣ No puedo recibir mi nómina en {banco} por otro motivo",
        "interactive_type": "button",
        "example_answer": "1️⃣;2️⃣;1;2;Sí;No;No puedo recibirla ahí;Sí puedo recibir la nómina en ese banco;Sin problemas;Si me ayudan sí puedo;",
        "end_interview_answer": "2;2️⃣ ; No; No puedo recibir la nomina en esos bancos; ",
    },
    "interview": {
        "response_type": "interactive",
        "template": "appointment_booking_limited_slots",
        "example_answer": "{'fecha':'2025-07-24','hora':'10:00','flow_token':'{'flow_type': 'appointment_booking', 'expiration_date': '2025-07-25T00:28:08.243936'}'}",
    },
    # To be created
    "rehiring": {
        "response_type": "interactive",
        "template": "rehire_{company_name}",
        "example_answer": "Si, No, Nunca, Quisiera trabajar ahi, Sip, Nop",
        "message_template":{
            "type": "rehire_list",
            "text": "Has trabajado en {company_name} anteriormente?",
            "company_name": "{company_id}"
        }
    },
}