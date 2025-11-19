from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional

from baltra_sdk.domain.models.screening_flow import MessageTemplate
from baltra_sdk.infra.repositories.sqlalchemy_repositories import SqlAlchemyMessageTemplateRepository
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.shared.utils.screening.sql_utils import get_active_roles_text
from baltra_sdk.shared.utils.screening.whatsapp_messages import (
    get_text_message_input,
    get_button_message_input,
    get_ctaurl_message_input,
    get_location_message,
    get_list_message_input,
)

_logger = logging.getLogger(__name__)


@dataclass
class RenderedTemplate:
    text: Optional[str]
    payload: Optional[dict | str]


class SolidTemplateRenderer:
    """Fetches and renders WhatsApp templates without calling the legacy helper directly."""

    def __init__(self, repository: Optional[SqlAlchemyMessageTemplateRepository] = None) -> None:
        self.repository = repository or SqlAlchemyMessageTemplateRepository(db.session)

    def render(self, keyword: str, candidate_data: dict) -> RenderedTemplate:
        template = self._find_template(keyword, candidate_data)
        _logger.debug(
            "[SOLID 4.2] SolidTemplateRenderer.render candidate=%s company=%s keyword=%s template_found=%s",
            candidate_data.get("candidate_id"),
            candidate_data.get("company_id"),
            keyword,
            bool(template),
        )
        if not template:
            _logger.warning("[SOLID 4.2] No template found for keyword=%s", keyword)
            return RenderedTemplate(None, None)

        text = self._format_text(template, candidate_data)
        payload = self._build_payload(template, text, candidate_data)
        return RenderedTemplate(text=text, payload=payload)

    def _find_template(self, keyword: str, candidate_data: dict) -> MessageTemplate | None:
        company_id = candidate_data.get("company_id")
        template: MessageTemplate | None = None
        if company_id:
            try:
                template = self.repository.find_by_keyword(company_id, keyword)
            except TypeError:
                template = None
            if template:
                return template
            _logger.debug(
                "[SOLID 4.2] Template not found for company-specific keyword=%s company_id=%s; checking global fallback",
                keyword,
                company_id,
            )
        if template:
            return template
        if hasattr(self.repository, "find_by_keyword_or_trigger"):
            return self.repository.find_by_keyword_or_trigger(keyword)
        return None

    def _format_text(self, template: MessageTemplate, candidate_data: dict) -> str:
        text = template.text or ""
        if "{roles}" in text:
            roles = get_active_roles_text(candidate_data.get("company_id"))
        else:
            roles = ""

        role_value = candidate_data.get("role") or "trabajo"
        name_value = candidate_data.get("first_name") or ""

        formatted = text.format(
            name=name_value,
            company_name=candidate_data.get("company_name", ""),
            roles=roles,
            role=role_value,
            interview_date=candidate_data.get("interview_date", ""),
            interview_address=candidate_data.get("interview_address", ""),
        )
        return formatted.replace("\\n", "\n")

    def _build_payload(
        self,
        template: MessageTemplate,
        text: str,
        candidate_data: dict,
    ) -> dict | str | None:
        message_type = template.type
        payload: dict | str | None = None
        if message_type == "text":
            payload = get_text_message_input(candidate_data["wa_id"], text)
        elif message_type == "interactive":
            interactive_type = template.interactive_type
            if interactive_type == "button":
                payload = get_button_message_input(
                    candidate_data,
                    text,
                    template.button_keys or [],
                    template.footer_text,
                    template.header_type,
                    template.header_content,
                )
            elif interactive_type == "cta_url":
                payload = get_ctaurl_message_input(
                    candidate_data,
                    text,
                    template.parameters,
                    template.footer_text,
                    template.header_type,
                    template.header_content,
                )
            elif interactive_type == "location_request_message":
                payload = get_location_message(candidate_data, text)
            elif interactive_type == "list":
                payload = get_list_message_input(
                    candidate_data,
                    text,
                    template.flow_cta,
                    template.list_section_title,
                    template.list_options,
                    template.footer_text,
                    template.header_type,
                    template.header_content,
                )

        if payload:
            return self._deserialize_payload(payload)

        _logger.warning(
            "Unsupported template type=%s interactive_type=%s", message_type, template.interactive_type
        )
        return None

    @staticmethod
    def _deserialize_payload(payload: dict | str) -> dict | str | None:
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                _logger.exception("Failed to deserialize WhatsApp payload")
                return None
        return payload
