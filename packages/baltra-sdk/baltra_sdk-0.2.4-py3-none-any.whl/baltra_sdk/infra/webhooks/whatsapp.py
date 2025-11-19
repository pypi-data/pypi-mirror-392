"""Servicios reutilizables para manejar el webhook de WhatsApp.

Este módulo persiste el objeto entrante y encola el mensaje en la tabla temporal.
La lógica de lag, prioridad y encolamiento para procesamiento es responsabilidad del worker.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional


DEFAULT_STAGING_PHONE_NUMBER_ID = "309958495536131a"


@dataclass(frozen=True)
class WebhookResponse:
    """Representa la respuesta normalizada del servicio."""

    body: Any
    status_code: int
    as_json: bool = True


@dataclass(frozen=True)
class WhatsAppWebhookDependencies:
    """Dependencias externas requeridas por el servicio de webhook."""

    store_wa_object: Callable[[Mapping[str, Any]], None]
    is_valid_whatsapp_message: Callable[[Mapping[str, Any]], bool]
    store_temporary_message: Callable[[Mapping[str, Any]], None]


@dataclass(frozen=True)
class _WebhookDecision:
    proceed: bool
    response: Optional[WebhookResponse] = None


@dataclass(frozen=True)
class _WebhookParseResult:
    raw_body: Mapping[str, Any]
    phone_number_id: Optional[str]
    message: Optional[Mapping[str, Any]]
    message_type: Optional[str]
    interactive_type: Optional[str]
    statuses: Optional[Iterable[Mapping[str, Any]]]


# Nota: No se requieren threads; el worker manejará procesamiento posterior.


class WebhookBodyParser:
    """Extrae los datos relevantes del payload."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)

    def parse(self, body: Optional[Mapping[str, Any]]) -> Optional[_WebhookParseResult]:
        if body is None:
            self._logger.warning("Received empty webhook payload")
            return None

        if isinstance(body, (str, bytes)):
            try:
                payload_str = body.decode("utf-8") if isinstance(body, bytes) else body
                body = json.loads(payload_str)
            except json.JSONDecodeError:
                self._logger.exception("Failed to decode webhook payload as JSON")
                return None

        if not isinstance(body, Mapping):
            self._logger.warning("Webhook payload is not a JSON object")
            return None

        try:
            entry = (body.get("entry") or [{}])[0]
            change = (entry.get("changes") or [{}])[0]
            value = change.get("value") or {}
            metadata = value.get("metadata") or {}
            phone_number_id = metadata.get("phone_number_id")
            statuses = value.get("statuses")
            messages = value.get("messages")
            message = messages[0] if isinstance(messages, list) and messages else None
            message_type = message.get("type") if isinstance(message, Mapping) else None
            interactive_type = None
            if message_type == "interactive" and isinstance(message, Mapping):
                interactive = message.get("interactive") or {}
                if isinstance(interactive, Mapping):
                    interactive_type = interactive.get("type")
        except (AttributeError, IndexError, KeyError, TypeError):
            self._logger.exception("Failed to parse webhook payload")
            return None

        return _WebhookParseResult(
            raw_body=body,
            phone_number_id=phone_number_id,
            message=message,
            message_type=message_type,
            interactive_type=interactive_type,
            statuses=statuses,
        )


class PhoneNumberEnvironmentGuard:
    """Aplica reglas de entorno con base en el phone_number_id."""

    def __init__(
        self,
        *,
        staging_phone_number_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self._staging_phone_number_id = staging_phone_number_id or DEFAULT_STAGING_PHONE_NUMBER_ID
        self._logger = logger or logging.getLogger(__name__)

    def evaluate(self, phone_number_id: Optional[str], flask_env: str) -> _WebhookDecision:
        if not phone_number_id:
            self._logger.warning("Missing phone_number_id in webhook payload")
            return _WebhookDecision(
                proceed=False,
                response=WebhookResponse({"status": "error", "message": "Missing phone_number_id"}, 400),
            )

        if phone_number_id == self._staging_phone_number_id:
            if flask_env != "staging":
                self._logger.info("Ignored staging webhook in production")
                return _WebhookDecision(
                    proceed=False,
                    response=WebhookResponse({"status": "ignored staging webhook in production"}, 200),
                )
        else:
            if flask_env == "staging":
                self._logger.info("Ignored production webhook in staging")
                return _WebhookDecision(
                    proceed=False,
                    response=WebhookResponse({"status": "ignored production webhook in staging"}, 200),
                )

        return _WebhookDecision(proceed=True)


# Eliminado: lógica de lag; el worker se encarga de agrupar y priorizar.


class WebhookVerifier:
    """Lógica de verificación para la suscripción del webhook."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)

    def verify(
        self,
        params: Mapping[str, Any],
        *,
        verify_token: str,
        version: Optional[str] = None,
    ) -> WebhookResponse:
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == verify_token:
                self._logger.info("[Account: PRIMARY] WEBHOOK_VERIFIED (version=%s)", version)
                return WebhookResponse(challenge or "", 200, as_json=False)

            self._logger.info("[Account: PRIMARY] VERIFICATION_FAILED - invalid mode or token")
            return WebhookResponse({"status": "error", "message": "Verification failed"}, 403)

        self._logger.info("[Account: PRIMARY] MISSING_PARAMETER")
        return WebhookResponse({"status": "error", "message": "Missing parameters"}, 400)


class WhatsAppWebhookService:
    """Servicio principal que coordina verificación y manejo de mensajes."""

    def __init__(
        self,
        dependencies: Optional[WhatsAppWebhookDependencies] = None,
        *,
        staging_phone_number_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        use_case: Optional[object] = None,
    ):
        self._deps = dependencies
        self._logger = logger or logging.getLogger(__name__)
        self._parser = WebhookBodyParser(logger=self._logger)
        self._environment_guard = PhoneNumberEnvironmentGuard(
            staging_phone_number_id=staging_phone_number_id,
            logger=self._logger,
        )
        self._verifier = WebhookVerifier(logger=self._logger)
        self._use_case = use_case

    def verify(self, params: Mapping[str, Any], *, config: Mapping[str, Any]) -> WebhookResponse:
        verify_token = config.get("VERIFY_TOKEN")
        if not verify_token:
            self._logger.error("VERIFY_TOKEN is not configured")
            return WebhookResponse(
                {"status": "error", "message": "Verification token not configured"},
                500,
            )

        return self._verifier.verify(
            params,
            verify_token=verify_token,
            version=config.get("VERSION"),
        )

    def handle_message(
        self,
        body: Optional[Mapping[str, Any]],
        *,
        config: Mapping[str, Any],
        flask_env: str,
        context_factory: Callable[[], Any],
    ) -> WebhookResponse:
        parse_result = self._parser.parse(body)
        if not parse_result:
            return WebhookResponse(
                {"status": "error", "message": "Invalid webhook payload"},
                400,
            )

        decision = self._environment_guard.evaluate(parse_result.phone_number_id, flask_env)
        if not decision.proceed:
            assert decision.response is not None
            return decision.response

        # If an application use-case is provided, delegate to it (SOLID approach)
        if self._use_case is not None:
            try:
                self._use_case.execute(parse_result.raw_body, context_factory=context_factory)
            except Exception:
                self._logger.exception("Failed to handle incoming message via use-case")
                return WebhookResponse({"status": "error", "message": "Failed to persist"}, 500)
            return WebhookResponse({"status": "ok"}, 200)

        # Legacy/minimal path: persist raw and store temp message directly
        try:
            assert self._deps is not None
            self._deps.store_wa_object(parse_result.raw_body)
        except Exception:  # noqa: BLE001
            self._logger.exception("Failed to persist WhatsApp object")
            return WebhookResponse(
                {"status": "error", "message": "Failed to persist webhook payload"},
                500,
            )

        if parse_result.statuses:
            self._logger.info("Received a WhatsApp status update.")
            return WebhookResponse({"status": "ok"}, 200)

        if not self._deps.is_valid_whatsapp_message(parse_result.raw_body):
            self._logger.warning("Invalid WhatsApp message structure")
            return WebhookResponse(
                {"status": "error", "message": "Not a WhatsApp API event"},
                404,
            )

        # Persist the message only; worker will handle batching/priority later.
        try:
            with context_factory():
                assert self._deps is not None
                self._deps.store_temporary_message(parse_result.raw_body)
        except Exception:
            self._logger.exception("Failed to persist temp message")
            return WebhookResponse(
                {"status": "error", "message": "Failed to persist temp message"},
                500,
            )

        return WebhookResponse({"status": "ok"}, 200)
