from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict

from baltra_sdk.domain.screening.entities import ReminderJob
from baltra_sdk.domain.screening.ports import CandidateRepository, FunnelAnalytics, ReminderNotifier
from baltra_sdk.shared.utils.screening.openai_utils import add_msg_to_thread, get_openai_client
from baltra_sdk.infra.screening.services.message_store import store_message
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_keyword_response_from_db
from baltra_sdk.shared.utils.screening.whatsapp_utils import send_message
from baltra_sdk.legacy.dashboards_folder.models import db


_logger = logging.getLogger(__name__)


@dataclass
class WhatsAppReminderNotifier(ReminderNotifier):
    """Sends reminder templates through the WhatsApp Graph API."""

    candidates: CandidateRepository
    analytics: FunnelAnalytics | None = None
    keyword_map: Dict[str, str] = field(
        default_factory=lambda: {
            "application": "application_reminder",
            "interview": "interview_reminder",
        }
    )
    client_factory: Callable[[], object] = get_openai_client

    def send(self, job: ReminderJob) -> None:
        keyword = self.keyword_map.get(job.kind)
        if keyword is None:
            _logger.warning("No template configured for reminder kind=%s", job.kind)
            return

        snapshot = self.candidates.get_or_create(job.wa_id_user, job.wa_id_system)
        candidate_data = dict(snapshot.raw_payload)

        session = db.session
        text, payload = get_keyword_response_from_db(
            session=session,
            keyword=keyword,
            candidate_data=candidate_data,
        )
        if payload is None:
            _logger.warning("Template %s returned no payload for candidate %s", keyword, snapshot.candidate_id)
            return

        text = text or ""

        payload_to_send = payload
        if isinstance(payload_to_send, dict):
            try:
                payload_to_send = json.dumps(payload_to_send, ensure_ascii=False)
            except Exception:
                _logger.exception("Failed to serialize reminder payload to JSON; aborting send")
                return
        response = send_message(payload_to_send, job.wa_id_system, keyword)
        if not response or response.status_code != 200:
            _logger.error("Failed to send reminder (%s) for candidate %s", keyword, snapshot.candidate_id)
            return

        try:
            response_json = json.loads(response.text)
            whatsapp_msg_id = response_json["messages"][0]["id"]
        except (json.JSONDecodeError, KeyError, IndexError) as exc:  # noqa: BLE001
            _logger.error("Failed parsing WhatsApp response for reminder: %s", exc)
            whatsapp_msg_id = ""

        client = self.client_factory()
        msg_id, sent_by = add_msg_to_thread(candidate_data["thread_id"], text, "assistant", client)
        store_message(msg_id, candidate_data, sent_by, text, whatsapp_msg_id)

        if self.analytics and snapshot.candidate_id and snapshot.wa_id_system:
            self.analytics.track(
                event_name=f"{job.kind}_reminder_sent",
                candidate_id=snapshot.candidate_id,
                company_id=candidate_data.get("company_id") or 0,
            )
