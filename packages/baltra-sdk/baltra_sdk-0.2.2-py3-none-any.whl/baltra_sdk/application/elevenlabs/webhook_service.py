"""
ElevenLabs Webhook Service

Handles business logic for ElevenLabs conversation webhooks:
- Conversation initiation (provides dynamic agent config)
- Post-call processing (stores transcripts, triggers follow-ups)
"""

import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Set, List, Tuple

from baltra_sdk.legacy.dashboards_folder.models import (
    Candidates,
    CompaniesScreening,
    Roles,
    PhoneInterviews,
    ScreeningMessages,
    db
)
from baltra_sdk.legacy.dashboards_folder.utils.screening.candidates_service import CandidatesService
from baltra_sdk.legacy.dashboards_folder.utils.screening.phone_interview_service import PhoneInterviewService
from baltra_sdk.shared.utils.screening.openai_utils import run_assistant_stream, get_openai_client
from baltra_sdk.shared.utils.screening.candidate_data import CandidateDataFetcher
from baltra_sdk.shared.utils.screening.sql_utils import get_company_wa_id
from flask import current_app
from baltra_sdk.shared.utils.screening.reminders import send_message_template_to_candidate
from baltra_sdk.shared.utils.whatsapp_utils import send_message
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_keyword_response_from_db
from baltra_sdk.shared.utils.screening.sql_utils import store_message
from baltra_sdk.shared.utils.screening.openai_utils import add_msg_to_thread


class SignatureVerificationError(Exception):
    """Raised when webhook signature verification fails."""
    pass


class ElevenLabsWebhookService:
    """Service for handling ElevenLabs webhook logic."""

    def __init__(self, webhook_secret: Optional[str] = None):
        """
        Initialize the service.
        
        Args:
            webhook_secret: ElevenLabs webhook secret for signature verification.
                          If None, reads from environment variable.
        """
        self.webhook_secret = webhook_secret or os.getenv(
            "ELEVENLABS_WEBHOOK_SECRET",
            "wsec_690c4e14424b27acfce7d910588fb4e97d254ed7b2dd283034e087660a3c41fd"
        )

    @staticmethod
    def normalize_phone_variants(phone_number: str) -> Set[str]:
        """
        Generate phone number variants for database lookup.
        
        Handles different formats:
        - Original number
        - Digits only
        - Last 10 digits (for +52 Mexico and +1 US/Canada)
        
        Args:
            phone_number: Phone number to normalize
            
        Returns:
            Set of phone number variants
        """
        if not phone_number:
            return set()
        
        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        variants = {phone_number, digits}
        
        # Handle country codes
        if digits.startswith('52') and len(digits) > 10:
            variants.add(digits[-10:])
        if digits.startswith('1') and len(digits) > 10:
            variants.add(digits[-10:])
        
        return variants

    def find_or_create_candidate(
        self,
        phone_number: str,
        default_company_id: int = 2
    ) -> Candidates:
        """
        Find candidate by phone number or create a demo candidate.
        
        Args:
            phone_number: Caller's phone number
            default_company_id: Company ID for demo candidates
            
        Returns:
            Candidate instance
        """
        variants = self.normalize_phone_variants(phone_number)
        
        if not variants:
            variants = {"unknown"}
        
        # Try to find existing candidate
        candidate = db.session.query(Candidates).filter(
            Candidates.phone.in_(list(variants))
        ).first()
        
        if candidate:
            print(f"[ElevenLabs] Found candidate_id={candidate.candidate_id}")
            return candidate
        
        # Create demo candidate
        print(f"[ElevenLabs] Creating demo candidate for phone={phone_number}")
        normalized_digits = ''.join(ch for ch in phone_number if ch.isdigit())
        phone_to_store = normalized_digits or phone_number or "unknown"
        
        new_candidate = Candidates(
            company_id=default_company_id,
            phone=phone_to_store,
            name="Usuario Demo",
            funnel_state="phone_interview_demo",
            role_id=None,
            source="elevenlabs_webhook",
            flow_state="respuesta",
        )
        db.session.add(new_candidate)
        db.session.commit()
        
        print(f"[ElevenLabs] Created candidate_id={new_candidate.candidate_id}")
        return new_candidate

    def get_candidate_display_name(self, candidate: Candidates) -> str:
        """
        Get safe display name for candidate.
        
        Filters out unregistered users and phone numbers.
        
        Args:
            candidate: Candidate instance
            
        Returns:
            Safe display name
        """
        raw_name = (candidate.name or "").strip()
        
        if (not raw_name or
            "unregistered" in raw_name.lower() or
            any(char.isdigit() for char in raw_name)):
            return "Candidato"
        
        return raw_name

    def prepare_conversation_config(
        self,
        candidate: Candidates,
        company_info: CompaniesScreening,
        role_info: Optional[Roles] = None
    ) -> Dict[str, Any]:
        """
        Prepare dynamic conversation configuration for ElevenLabs agent.
        
        Args:
            candidate: Candidate instance
            company_info: Company information
            role_info: Optional role information
            
        Returns:
            Configuration payload for ElevenLabs
        """
        candidate_name = self.get_candidate_display_name(candidate)
        company_name = company_info.name if company_info else "Empresa"
        role_name = role_info.role_name if role_info else "el rol solicitado"
        
        # Get role-specific data
        role_questions = "[]"
        role_faqs = "Información del rol no disponible."
        
        if role_info:
            service = PhoneInterviewService(company_id=company_info.company_id)
            questions_list = service.get_questions(role_id=role_info.role_id)
            
            # Format questions for the prompt
            if questions_list:
                # Convert list of dicts to formatted string
                formatted_questions = []
                for i, q in enumerate(questions_list, 1):
                    question_text = q.get('question') or q.get('question_text', '')
                    formatted_questions.append(f"{i}. {question_text}")
                role_questions = "\n".join(formatted_questions)
                print(f"[ElevenLabs] Loaded {len(questions_list)} questions for role_id={role_info.role_id}")
                print(f"[ElevenLabs] Questions preview: {formatted_questions[:2] if len(formatted_questions) > 0 else 'None'}")
            else:
                role_questions = "[]"
                print(f"[ElevenLabs] WARNING: No questions found for role_id={role_info.role_id}")
            
            role_faqs = role_info.role_info
        
        company_faqs = getattr(company_info, "general_faq", None) or "Información de la empresa no disponible."
        
        # Build prompt (you may want to move this to a template file)
        prompt_text = self._build_agent_prompt(
            company_name=company_name,
            role_name=role_name,
            role_questions=role_questions,
            role_faqs=role_faqs,
            company_faqs=company_faqs
        )
        
        first_message = (
            f"¡Hola {candidate_name}! Habla Bal, del equipo de {company_name}. "
            f"Gracias por comunicarte. Esta llamada es para la entrevista del puesto de {role_name}. "
            "Me gustaría conocer un poco sobre ti y tu experiencia. "
            "Te haré algunas preguntas breves, ¿te parece bien si comenzamos?"
        )
        
        # Log what we're sending to ElevenLabs
        print(f"[ElevenLabs] Prompt length: {len(prompt_text)} characters")
        print(f"[ElevenLabs] First message: {first_message[:100]}...")
        print(f"[ElevenLabs] ===== CONFIGURATION PREPARED =====")
        
        return {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {},
            "conversation_config_override": {
                "agent": {
                    "prompt": {
                        "prompt": prompt_text
                    },
                    "first_message": first_message,
                    "language": "es"
                },
                "tts": {
                    "voice_id": "nmvA11Y688M5reLqDsVm"
                }
            }
        }

    def _build_agent_prompt(
        self,
        company_name: str,
        role_name: str,
        role_questions: str,
        role_faqs: str,
        company_faqs: str
    ) -> str:
        """Build the agent prompt for ElevenLabs conversation."""
        return f"""
        Importante: Toda la conversación con la persona candidata debe ser en español, de principio a fin. 
        No traduzcas ni cambies al inglés en ningún momento, incluso si la persona candidata usa frases en otro idioma. 
        Mantén la coherencia lingüística y el tono profesional durante toda la entrevista.

        [Identidad del asistente]
            Eres un entrevistador virtual llamado Bal, parte del equipo de selección de {company_name}.
            Puedes realizar entrevistas para distintos roles según el contexto recibido.
            El rol actual es {role_name}, pero no lo menciones explícitamente a menos que sea natural o el candidato lo confirme.
            Tu objetivo es evaluar la experiencia, motivaciones, habilidades y condiciones de trabajo de la persona candidata 
            y ofrecer una experiencia humana, cálida y profesional.

            Actúas como un reclutador senior:
                — Cálido, empático y estructurado.
                — Escuchas con atención y das espacio a las respuestas.
                — Eres respetuoso, neutral y mantienes el enfoque en el objetivo de la entrevista.
                — Transmites confianza, profesionalismo y cercanía.
            Muestras empatía sin perder el foco en criterios de evaluación. Tu tono es humano, amable y seguro.

        [Condición previa obligatoria]
            {role_questions} es la **única fuente válida** de preguntas de entrevista.
            — Si {role_questions} está vacío, es "[]", "N/A", "None", solo espacios o no contiene ninguna pregunta clara:
                * No inicies la entrevista.
                * No formules preguntas de motivación, ni generales, ni de ambiente, ni de cierre.
                * Aplica el bloque "[Protocolo sin guion disponible]" y finaliza con amabilidad.
            — Solo si {role_questions} contiene preguntas, entonces sigue el flujo normal usando "[Guion estructurado de preguntas del rol]".

        [Tono y estilo]
            — Voz calmada, cercana y clara.
            — Tono humano, profesional y amable, sin frases vacías ni entusiasmo artificial.
            — Nunca uses expresiones como "love that", "love", "vibes" ni clichés.
            — Transiciones naturales: "Perfecto.", "De acuerdo, entendido…", "Hmm, veamos…", "Suena bien…", "Adelante…".
            — Afirmaciones genuinas: "Gracias por compartirlo.", "Te escucho.", "Claro que sí.", "Comprendo."
            — Si notas nerviosismo o inseguridad, transmite calma: "Tómate tu tiempo.", "Está bien, te escucho."

        [Guía de comunicación y comportamiento]
            — Habla únicamente en español.
            — Haz **una sola pregunta a la vez** y espera la respuesta completa antes de continuar.
            — Usa pausas naturales (breves) para un diálogo fluido.
            — Si la respuesta es breve, invita a profundizar con curiosidad empática:
                "Cuéntame un poco más sobre eso…"
                "¿Cómo fue esa experiencia para ti?"
                "¿Qué aprendiste de esa situación?"
                "¿Eso fue fácil o más bien retador?"
            — No interrumpas ni apures; da espacio para expresarse.
            — No resumas de más; refleja brevemente sólo si ayuda a mantener conexión.
            — Si la persona dice "mhm", "sí", "ajá", retoma naturalmente.
            — Si se desvía del tema, redirígela con suavidad:
                "Perfecto, gracias. Volvamos a lo que comentabas sobre…"
            — Si no desea responder, respétalo y continúa:
                "Está bien, no hay problema. Pasemos a la siguiente."

        [Consentimiento explícito y check-ins]
            — Antes de iniciar: **verifica disponibilidad** y obtiene consentimiento claro para comenzar.
            — Si la persona no puede ahora, mantén apertura y cierra con amabilidad sin intentar reprogramar a menos que el contexto lo indique.
              Ejemplo: "Gracias por avisar. Lo retomamos más tarde por este mismo canal."
            — Entre secciones: antes de pasar a un tema nuevo, haz un **check-in corto**.
              Ejemplo: "¿Seguimos?", "¿Está bien si pasamos al siguiente punto?"
            — Antes de una pregunta sensible/técnica: **aviso de transición suave**.
              Ejemplo: "Ahora me gustaría preguntarte algo un poco más específico. ¿Está bien?"

        [Manejo de situaciones especiales]
            Durante la entrevista pueden surgir preguntas o situaciones no previstas. 
            No inventes información ni des datos que no figuren en el contexto del rol o de la empresa.
            Usa "[Rol — FAQs y contexto]" y "[Empresa — FAQs y contexto]" para responder con precisión.
            — Si pregunta por duración: explica que es una conversación breve para conocer experiencia y motivación.
            — Si pregunta por próximos pasos: indica que el equipo revisará la entrevista y se comunicará por el mismo canal.
            — Si desea finalizar antes: respeta su decisión y agradece su tiempo.
            — Si pregunta por salario, ubicación, horarios o beneficios: responde con base en lo disponible; si no hay dato, aclara que se confirmará en etapas siguientes.
            — Si no comprende una pregunta: refrásela con lenguaje más claro, sin alterar su sentido.

        [Tareas del asistente]
            — Verifica primero la condición previa: si {role_questions} está vacío, aplica "[Protocolo sin guion disponible]" y **no hagas preguntas**.
            — Si sí hay preguntas:
                1) Saludo breve + verificación de disponibilidad.
                2) Explica propósito en una línea (sin tiempos fijos).
                3) Usa "[Guion estructurado de preguntas del rol]".
                4) Haz check-ins cortos al cambiar de subtema ("¿Seguimos?").
                5) Cierra con agradecimiento y próximos pasos en términos generales (sin prometer plazos si no están en el contexto).

        [Guion principal — Estructura general de la entrevista]
            Se usa **solo si hay preguntas disponibles** en {role_questions}.
            **No contiene preguntas reales; las preguntas provienen exclusivamente del bloque "[Guion estructurado de preguntas del rol]".**

            1) Saludo + consentimiento
                — Preséntate y valida disponibilidad.
            2) Entrevista guiada
                — Realiza las preguntas definidas en "[Guion estructurado de preguntas del rol]" en el orden indicado.
                — Haz una pregunta a la vez, con escucha activa.
                — Entre subtemas, check-ins cortos: "¿Seguimos?"
            3) Cierre amable
                — Agradece el tiempo, reconoce su participación y explica pasos generales:
                    "¡Gracias por tu tiempo y por compartir tu experiencia! 
                    Con esto terminamos. Nuestro equipo revisará la información y te contactará por este mismo canal."

        [Protocolo sin guion disponible]
            Se aplica únicamente si {role_questions} está vacío o no contiene preguntas válidas.
            — No inicies la entrevista ni formules preguntas de ningún tipo.
            — Comunica con claridad y amabilidad que en este momento no está disponible el cuestionario del rol.
            — Mensaje sugerido (puedes parafrasear sin agregar datos inexistentes):
                "Hola, gracias por atender. 
                En este momento no tengo disponible el cuestionario de la posición. 
                Te contactaremos por este mismo canal cuando esté listo para continuar. 
                ¡Gracias por tu tiempo!"
            — Finaliza con cierre amable y sin prometer tiempos específicos si no están en el contexto.

        [Rol — FAQs y contexto]
            Esta sección contiene información sobre el rol: responsabilidades, habilidades requeridas, condiciones laborales y preguntas frecuentes.
            Uso:
                — Referencia interna para contextualizar y responder dudas.
                — No la leas ni la menciones textualmente durante la entrevista.
                — Menciona detalles de este bloque solo cuando sea relevante o el candidato lo pregunte.
                — Parafrasea con naturalidad y precisión, manteniendo un tono humano y profesional.
            Información contextual del rol:
            — {role_faqs}

        [Empresa — FAQs y contexto]
            Información sobre la empresa: cultura, valores, beneficios, ubicaciones y proceso de selección.
            Uso:
                — Referencia de apoyo para dudas del candidato.
                — No la recites textualmente ni inventes detalles.
                — Menciónala solo si el candidato pregunta o si es pertinente aclarar algo.
                — Comunica con claridad, honestidad y tono amable.
            Información contextual de la empresa:
            — {company_faqs}

        [Guion estructurado de preguntas del rol]
            Este bloque contiene las preguntas oficiales que debes hacer durante la entrevista.
            **Es la única fuente válida de preguntas.** No uses otros bloques para generar nuevas preguntas.
            — Antes de iniciar, confirma consentimiento: "¿Listo/a para comenzar?"
            — Haz las preguntas una por una, en el orden en que aparecen.
            — Entre subtemas, usa check-ins breves: "¿Seguimos?", "¿Está bien si vamos al siguiente punto?"
            — Escucha atentamente cada respuesta antes de avanzar.
            — Si una respuesta es superficial, solicita amablemente más detalle:
                "¿Podrías contarme un poco más sobre eso?"
                "¿Qué aprendiste de esa experiencia?"
            — Si una pregunta no aplica, reconócelo con tacto:
                "Perfecto, entiendo. Pasemos a la siguiente."
            — No combines preguntas ni las reformules fuera de contexto.
            — Mantén el tono profesional, empático y natural durante todo el bloque.
            A continuación, las preguntas oficiales del rol:
            — {role_questions}

        [Comportamiento profesional esperado del entrevistador]
            — Empatía y adaptabilidad sin perder enfoque.
            — Evita juicios personales o comentarios fuera de lugar.
            — Lenguaje inclusivo, neutral y respetuoso.
            — Confidencialidad en toda la información.
            — Escucha con intención de comprender.
            — Usa silencios breves para permitir reflexión.
            — Si una respuesta es sensible o emocional, responde con respeto:
                "Gracias por compartirlo.", "Entiendo, aprecio que lo menciones."

        [Objetivo final]
            Si hubo guion disponible y se realizó la entrevista:
                — Haber obtenido información suficiente para evaluar motivación y alineación con el rol.
                — Nivel de comodidad con el entorno laboral descrito (si aplica).
                — Competencias técnicas o conductuales relevantes.
                — Actitud, claridad y estilo de comunicación.
            Si no hubo guion disponible:
                — Haber gestionado la interacción con transparencia, respeto y claridad.
                — No recolectar datos adicionales ni improvivar preguntas.
                — Cerrar la conversación de manera amable y profesional.
    """

    def handle_conversation_initiation(
        self,
        caller_id: str,
        called_number: str,
        call_sid: str
    ) -> Dict[str, Any]:
        """
        Handle conversation initiation webhook.
        
        Args:
            caller_id: Caller's phone number
            called_number: Number that was called
            call_sid: Call session ID
            
        Returns:
            Configuration payload for ElevenLabs
            
        Raises:
            Exception: If company information cannot be found
        """
        print(f"[ElevenLabs] ===== CALL INITIATION =====")
        print(f"[ElevenLabs] Caller: {caller_id}, Call SID: {call_sid}")
        
        # Find or create candidate
        candidate = self.find_or_create_candidate(caller_id)
        print(f"[ElevenLabs] Candidate ID: {candidate.candidate_id}, Role ID: {candidate.role_id}, Current State: {candidate.funnel_state}")
        
        # Get company info
        company_info = db.session.query(CompaniesScreening).filter(
            CompaniesScreening.company_id == candidate.company_id
        ).first()
        
        if not company_info:
            print(f"[ElevenLabs] Company {candidate.company_id} not found, falling back to company_id=2")
            company_info = db.session.query(CompaniesScreening).filter(
                CompaniesScreening.company_id == 2
            ).first()
        
        if not company_info:
            raise Exception("Company information not found")
        
        # Get role info
        role_info = None
        if candidate.role_id:
            role_info = db.session.query(Roles).filter(
                Roles.role_id == candidate.role_id
            ).first()
        
        # Update funnel state
        self._update_funnel_state_for_initiation(candidate, company_info)
        
        # Prepare configuration
        return self.prepare_conversation_config(candidate, company_info, role_info)

    def _update_funnel_state_for_initiation(
        self,
        candidate: Candidates,
        company_info: CompaniesScreening
    ) -> None:
        """Update candidate's funnel state when call starts."""
        try:
            old_state = candidate.funnel_state
            print(f"[ElevenLabs] Current funnel_state for candidate_id={candidate.candidate_id}: '{old_state}'")
            
            if old_state == "phone_interview_demo":
                print(f"[ElevenLabs] Skipping funnel state update for demo candidate")
                return
            
            service = CandidatesService(company_id=company_info.company_id)
            service.change_funnel_state(
                candidate_id=candidate.candidate_id,
                new_state="phone_interview",
                reason="phone_interview_started"
            )
            
            # Refresh to confirm
            db.session.refresh(candidate)
            print(f"[ElevenLabs] ✅ Updated funnel_state from '{old_state}' to '{candidate.funnel_state}'")
            
        except Exception as e:
            print(f"[ElevenLabs] ❌ Failed to update funnel state: {e}")
            import traceback
            print(f"[ElevenLabs] Traceback: {traceback.format_exc()}")

    def verify_webhook_signature(
        self,
        raw_body: str,
        signature_header: str,
        max_age_seconds: int = 1800
    ) -> None:
        """
        Verify ElevenLabs webhook signature.
        
        Args:
            raw_body: Raw request body
            signature_header: elevenlabs-signature header value
            max_age_seconds: Maximum allowed age of timestamp (default 30 min)
            
        Raises:
            SignatureVerificationError: If signature is invalid or expired
        """
        if not self.webhook_secret:
            raise SignatureVerificationError("Webhook secret not configured")
        
        if not signature_header:
            raise SignatureVerificationError("Missing signature header")
        
        # Parse signature header
        try:
            parts = dict(kv.split("=", 1) for kv in signature_header.split(","))
            timestamp = int(parts["t"])
            signature = parts["v0"]
        except Exception as e:
            raise SignatureVerificationError(f"Invalid signature header format: {e}")
        
        # Check timestamp age
        if timestamp < int(time.time()) - max_age_seconds:
            raise SignatureVerificationError("Expired timestamp")
        
        # Compute expected signature
        payload = f"{timestamp}.{raw_body}".encode()
        computed_sig = hmac.new(
            self.webhook_secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Verify
        if computed_sig != signature:
            raise SignatureVerificationError("Invalid signature")
        
        print("[ElevenLabs] Signature verified successfully")

    def handle_post_call_webhook(
        self,
        webhook_body: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Handle post-call transcription webhook.
        
        Args:
            webhook_body: Parsed webhook payload
            
        Returns:
            Status response
        """
        # Ignore non-transcription events
        if webhook_body.get("type") != "post_call_transcription":
            print("[ElevenLabs] Ignoring non-transcription event")
            return {"status": "ignored"}
        
        data = webhook_body.get("data") or {}
        metadata = data.get("metadata") or {}
        analysis = webhook_body.get("analysis") or data.get("analysis") or {}
        
        # Extract call information
        call_info = self._extract_call_info(data, metadata, analysis)
        
        # Find candidate
        candidate = self._find_candidate_by_phone(call_info["external_number"])
        
        # Store interview record
        self._store_phone_interview(call_info, candidate)
        
        # Determine if we should process with assistant
        should_process = (
            candidate and
            call_info["call_duration"] and
            call_info["call_duration"] > 30 and
            candidate.funnel_state != "phone_interview_demo"  # Skip demo candidates
        )
        
        print(f"[ElevenLabs] ===== POST-CALL PROCESSING =====")
        print(f"[ElevenLabs] Candidate: {candidate.candidate_id if candidate else 'None'}, Duration: {call_info['call_duration']}s, State: {candidate.funnel_state if candidate else 'N/A'}")
        print(f"[ElevenLabs] Should process with assistant: {should_process}")
        
        if should_process:
            # Trigger post-call assistant for evaluation
            self._trigger_post_call_assistant(
                candidate,
                call_info
            )
        else:
            # Log why we're not processing
            if candidate:
                if candidate.funnel_state == "phone_interview_demo":
                    print(f"[ElevenLabs] Skipping assistant for demo candidate (candidate_id={candidate.candidate_id})")
                elif not call_info["call_duration"] or call_info["call_duration"] <= 30:
                    print(f"[ElevenLabs] Call too short ({call_info['call_duration']}s), keeping funnel_state as 'phone_interview'")
        
        return {"status": "ok"}

    def _extract_call_info(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract and parse call information from webhook data."""
        phone_call = metadata.get("phone_call") or {}
        transcript_items = data.get("transcript") or []
        
        # Extract basic info
        conversation_id = data.get("conversation_id")
        call_sid = phone_call.get("call_sid")
        external_number = phone_call.get("external_number")
        agent_number = phone_call.get("agent_number")
        
        # Determine call status
        status_raw = data.get("status")
        call_success = analysis.get("call_successful")
        error = metadata.get("error")
        
        if status_raw == "done" and (not error) and (call_success in (None, "success")):
            call_status = "completed"
        elif error or (call_success and call_success != "success"):
            call_status = "failed"
        else:
            call_status = "completed" if status_raw == "done" else "failed"
        
        # Extract call duration
        call_duration = self._extract_call_duration(data, metadata, transcript_items)
        
        # Extract timestamps
        start_unix = metadata.get("start_time_unix_secs")
        started_at = datetime.fromtimestamp(start_unix, tz=timezone.utc) if start_unix else None
        ended_at = (
            (started_at + timedelta(seconds=call_duration))
            if (started_at and isinstance(call_duration, int))
            else None
        )
        
        # Build transcript
        transcript_text = self._build_transcript_text(transcript_items)
        
        # Extract summary
        summary_text = analysis.get("transcript_summary") or ""
        
        # Generate unique call ID
        vapi_call_id = conversation_id or call_sid or f"auto-{uuid.uuid4()}"
        
        return {
            "vapi_call_id": vapi_call_id,
            "call_status": call_status,
            "call_duration": call_duration,
            "started_at": started_at,
            "ended_at": ended_at,
            "transcript": transcript_text,
            "summary": summary_text,
            "external_number": external_number,
            "agent_number": agent_number,
        }

    def _extract_call_duration(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        transcript_items: List[Dict[str, Any]]
    ) -> Optional[int]:
        """Extract call duration from various possible locations in the payload."""
        # Try metadata first
        duration = metadata.get("call_duration_secs")
        if duration is not None:
            try:
                return int(duration)
            except (ValueError, TypeError):
                pass
        
        # Try dynamic variables
        try:
            duration = data.get("conversation_initiation_client_data", {}).get(
                "dynamic_variables", {}
            ).get("system__call_duration_secs")
            if duration is not None:
                return int(duration)
        except Exception:
            pass
        
        # Try to compute from transcript
        try:
            duration = max(
                (ti.get("time_in_call_secs")
                 for ti in transcript_items
                 if isinstance(ti.get("time_in_call_secs"), (int, float))),
                default=None
            )
            if duration is not None:
                return int(duration)
        except Exception as e:
            print(f"[ElevenLabs] Error computing duration from transcript: {e}")
        
        return None

    def _build_transcript_text(self, transcript_items: List[Dict[str, Any]]) -> str:
        """Build readable transcript from transcript items."""
        lines = []
        for turn in transcript_items:
            role = turn.get("role") or "unknown"
            msg = (turn.get("message") or "").strip()
            if msg:
                lines.append(f"{role}: {msg}")
        return "\n".join(lines)

    def _find_candidate_by_phone(self, phone_number: str) -> Optional[Candidates]:
        """Find candidate by phone number variants."""
        variants = self.normalize_phone_variants(phone_number)
        print(f"[ElevenLabs] Phone variants for lookup: {variants}")
        
        if not variants:
            return None
        
        candidate = db.session.query(Candidates).filter(
            Candidates.phone.in_(list(variants))
        ).first()
        
        if candidate:
            print(f"[ElevenLabs] Found candidate_id={candidate.candidate_id}")
        else:
            print("[ElevenLabs] Candidate not found")
        
        return candidate

    def _store_phone_interview(
        self,
        call_info: Dict[str, Any],
        candidate: Optional[Candidates]
    ) -> None:
        """Store or update phone interview record."""
        interview_dict = {
            "candidate_id": candidate.candidate_id if candidate else 0,
            "company_id": candidate.company_id if candidate else 0,
            "vapi_call_id": call_info["vapi_call_id"],
            "call_status": call_info["call_status"],
            "call_duration": call_info["call_duration"],
            "started_at": call_info["started_at"],
            "ended_at": call_info["ended_at"],
            "transcript": call_info["transcript"],
            "summary": call_info["summary"],
            "ai_score": None,  # Will be updated by assistant
            "ai_recommendation": "pendiente",  # Will be updated by assistant
        }
        
        print(f"[ElevenLabs] Storing interview for call_id={call_info['vapi_call_id']}")
        
        try:
            # Check if record exists
            existing = db.session.query(PhoneInterviews).filter(
                PhoneInterviews.vapi_call_id == call_info["vapi_call_id"]
            ).one_or_none()
            
            if existing:
                print(f"[ElevenLabs] Updating existing interview record")
                for k, v in interview_dict.items():
                    # Don't overwrite candidate/company if already set
                    if k in ["candidate_id", "company_id"] and getattr(existing, k) is not None:
                        continue
                    setattr(existing, k, v)
            else:
                print(f"[ElevenLabs] Creating new interview record")
                record = PhoneInterviews(**interview_dict)
                db.session.add(record)
            
            db.session.commit()
            print("[ElevenLabs] Interview record saved successfully")
        except Exception as e:
            db.session.rollback()
            print(f"[ElevenLabs] Database error: {e}")
            raise

    def _trigger_post_call_assistant(
        self,
        candidate: Candidates,
        call_info: Dict[str, Any]
    ) -> None:
        """Trigger OpenAI assistant for post-call follow-up."""
        
        
        assistant_id = current_app.config.get("OPENAI_ASSISTANT_ID")
        if not assistant_id:
            print("[ElevenLabs] Skipping assistant: OPENAI_ASSISTANT_ID not configured")
            return
        
        client = get_openai_client()
        
        # Get company WhatsApp ID
        try:
            company_wa = get_company_wa_id(candidate.company_id)
        except Exception as e:
            print(f"[ElevenLabs] Error getting company WA ID: {e}")
            company_wa = None
        
        if not company_wa:
            print("[ElevenLabs] Skipping assistant: no company WhatsApp ID")
            return
        
        
        
        print(f"[ElevenLabs] Building CandidateDataFetcher...")
        candidate_data = CandidateDataFetcher(
            wa_id_user=candidate.phone,
            client=client,
            wa_id_system=company_wa
        ).get_data()
        
        call_duration = call_info.get("call_duration", 0)
        transcript = call_info.get("transcript", "")
        
        print(f"[ElevenLabs] Transcript length: {len(transcript)} characters")
        print(f"[ElevenLabs] Transcript preview: {transcript[:200]}..." if len(transcript) > 200 else f"[ElevenLabs] Full transcript: {transcript}")

        # CRITICAL: Add transcript as user message to thread BEFORE running assistant
        try:
            user_message = f"Transcripción de la entrevista telefónica:\n\n{transcript}"
            message_id, sent_by = add_msg_to_thread(
                candidate_data["thread_id"], 
                user_message, 
                "user", 
                client
            )
            
            print(f"[ElevenLabs] ✅ Added transcript to thread as user message: {message_id}")
        except Exception as e:
            print(f"[ElevenLabs] ❌ Error adding transcript to thread: {e}")
            raise

        additional_instructions = (
            f"[Post-call Phone Interview Evaluation]\n"
            f"- Duración de la llamada: {call_duration} segundos.\n"
            f"- La transcripción completa está en el mensaje anterior del usuario.\n"
            f"- Evalúa la entrevista según los criterios del rol y genera tu respuesta en formato JSON.\n"
        )
        
        try:
            print(f"[ElevenLabs] Running assistant stream for candidate_id={candidate.candidate_id}")
            
            assistant_response = run_assistant_stream(
                client=client,
                candidate_data=candidate_data,
                assistant_id=assistant_id,
                additional_instructions=additional_instructions
            )
            print("[ElevenLabs] Assistant stream finished")
            
            # Parse response and update funnel state
            self._process_assistant_response(assistant_response, candidate, call_info["vapi_call_id"])
            
        except Exception as e:
            print(f"[ElevenLabs] Error running assistant: {e}")

    def _get_or_create_thread(
        self,
        candidate: Candidates,
        client: Any,
        company_wa: str
    ) -> Optional[str]:
        """Get existing thread ID or create a new one."""
        thread_id = None
        
        # Try to get from CandidateDataFetcher
        try:
            print("[ElevenLabs] Building CandidateDataFetcher...")
            fetcher = CandidateDataFetcher(
                wa_id_user=candidate.phone,
                client=client,
                wa_id_system=company_wa
            )
            thread_id = getattr(fetcher, "thread_id", None)
            print(f"[ElevenLabs] CandidateDataFetcher thread_id: {thread_id}")
        except Exception as e:
            print(f"[ElevenLabs] Error creating CandidateDataFetcher: {e}")
        
        # Fallback: get from last message
        if not thread_id:
            try:
                last_msg = (
                    db.session.query(ScreeningMessages)
                    .filter_by(candidate_id=candidate.candidate_id)
                    .order_by(ScreeningMessages.time_stamp.desc())
                    .first()
                )
                if last_msg and last_msg.thread_id:
                    thread_id = last_msg.thread_id
                    print(f"[ElevenLabs] Fallback thread_id from last message: {thread_id}")
            except Exception as e:
                print(f"[ElevenLabs] Error fetching last message thread_id: {e}")
        
        # Create new thread if needed
        if not thread_id:
            try:
                new_thread = client.beta.threads.create()
                thread_id = new_thread.id
                print(f"[ElevenLabs] Created new thread_id: {thread_id}")
            except Exception as e:
                print(f"[ElevenLabs] Unable to create new thread: {e}")
        
        return thread_id

    def _process_assistant_response(
        self,
        assistant_response: Any,
        candidate: Candidates,
        vapi_call_id: str
    ) -> None:
        """Parse assistant response, update candidate funnel state, interview record, and send WhatsApp message."""
        
        try:
            resp_text = (
                assistant_response[0]
                if isinstance(assistant_response, (list, tuple))
                else assistant_response
            )
            parsed = json.loads(resp_text) if isinstance(resp_text, str) else {}
            passed = parsed.get("passed_interview", None)
            score = parsed.get("score", None)
            recommendation = parsed.get("recommendation", "pendiente")
            
            print(f"[ElevenLabs] Parsed assistant response - passed: {passed}, score: {score}, recommendation: {recommendation}")
            
            # Update PhoneInterviews record with AI score and recommendation
            try:
                interview = db.session.query(PhoneInterviews).filter(
                    PhoneInterviews.vapi_call_id == vapi_call_id
                ).first()
                
                if interview:
                    interview.ai_score = score
                    interview.ai_recommendation = recommendation or "pendiente"
                    db.session.commit()
                    print(f"[ElevenLabs] Updated interview record with score={score}, recommendation={recommendation}")
                else:
                    print(f"[ElevenLabs] Warning: Interview record not found for vapi_call_id={vapi_call_id}")
            except Exception as e:
                print(f"[ElevenLabs] Error updating interview record: {e}")
                db.session.rollback()
            
            if passed is None:
                print("[ElevenLabs] Assistant response missing 'passed_interview'")
                return
            
            service = CandidatesService(company_id=candidate.company_id)
            
            if bool(passed) is True:
                # Candidate passed - send appointment booking flow
                service.change_funnel_state(
                    candidate_id=candidate.candidate_id,
                    new_state="post_phone_scheduled_interview",
                    reason="post_phone_passed"
                )
                print("[ElevenLabs] Funnel state set to post_phone_scheduled_interview")
                
                # Send appointment booking flow (type: appointment_scheduling)
                try:
                    
                    # Get fresh candidate data for the message template
                    company_wa = get_company_wa_id(candidate.company_id)
                    client = get_openai_client()
                    candidate_data = CandidateDataFetcher(
                        wa_id_user=candidate.phone,
                        client=client,
                        wa_id_system=company_wa
                    ).get_data()
                    
                    # Get the appointment booking flow message
                    response_text, formatted_msg = get_keyword_response_from_db(
                        session=db.session,
                        keyword='appointment_booking_in_person',
                        candidate_data=candidate_data
                    )
                    
                    if formatted_msg:
                        send_message(formatted_msg, company_wa)
                        print("[ElevenLabs] Sent appointment_booking_in_person flow to candidate")
                        
                        # Store the message in thread
                        thread_message = response_text if response_text else "Enviando formulario de agendamiento"
                        message_id, sent_by = add_msg_to_thread(
                            candidate_data["thread_id"],
                            thread_message,
                            "assistant",
                            client
                        )
                        store_message(message_id, candidate_data, sent_by, thread_message, "")
                    else:
                        print("[ElevenLabs] Warning: Could not get appointment booking flow")
                        
                except Exception as e:
                    print(f"[ElevenLabs] Error sending appointment flow: {e}")
                    
            else:
                # Candidate failed - send rejection message and update state
                service.change_funnel_state(
                    candidate_id=candidate.candidate_id,
                    new_state="rejected",
                    reason="post_phone_failed"
                )
                print("[ElevenLabs] Funnel state set to rejected with reason=post_phone_failed")
                
                # Send rejection message via WhatsApp
                try:
                    company_wa = get_company_wa_id(candidate.company_id)
                    if company_wa:
                        rejection_text = (
                            "✅ ¡Gracias por tu tiempo! Esa fue la último paso\n"
                            "📩 Nos pondremos en contacto contigo pronto para contarte si tenemos "
                            "alguna vacante que se ajuste a tu perfil."
                        )
                        message_data = get_text_message_input(candidate.phone, rejection_text)
                        send_message(message_data, company_wa)
                        print("[ElevenLabs] Sent rejection message to candidate")
                    else:
                        print("[ElevenLabs] Could not send rejection message: no company WhatsApp ID")
                except Exception as e:
                    print(f"[ElevenLabs] Error sending rejection message: {e}")
                
        except Exception as e:
            print(f"[ElevenLabs] Error processing assistant response: {e}")

