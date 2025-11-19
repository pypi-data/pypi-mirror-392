from __future__ import annotations

import logging
from typing import Any, Dict, Mapping

from baltra_sdk.domain.screening.ports import FunnelAnalytics
from baltra_sdk.infra.screening.services.analytics import MixpanelFunnelAnalytics
from baltra_sdk.legacy.dashboards_folder.models import CandidateFunnelLog, Candidates, db

_logger = logging.getLogger(__name__)


class FunnelStateService:
    """Tracks funnel transitions and analytics outside the legacy helpers."""

    def __init__(
        self,
        session=None,
        analytics: FunnelAnalytics | None = None,
    ) -> None:
        self.session = session or db.session
        self.analytics = analytics or MixpanelFunnelAnalytics()

    # ------------------------------------------------------------------
    def log_state_change(self, candidate_id: int, previous_state: str, new_state: str) -> None:
        entry = CandidateFunnelLog(
            candidate_id=candidate_id,
            previous_funnel_state=previous_state,
            new_funnel_state=new_state,
        )
        self.session.add(entry)
        try:
            self.session.flush()
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("Failed to log funnel transition for candidate %s", candidate_id)
            raise

    def update_flow_state(
        self,
        candidate_payload: Mapping[str, Any],
        new_state: str,
        *,
        reason: str | None = None,
    ) -> bool:
        candidate_id = candidate_payload.get("candidate_id")
        if not candidate_id:
            _logger.warning("update_flow_state: missing candidate_id in payload")
            return False

        candidate = (
            self.session.query(Candidates)
            .filter_by(candidate_id=candidate_id)
            .first()
        )
        if not candidate:
            _logger.warning("update_flow_state: candidate %s not found", candidate_id)
            return False

        previous_state = candidate.funnel_state or ""
        if previous_state == new_state:
            return True

        try:
            self.log_state_change(candidate_id, previous_state, new_state)
            candidate.funnel_state = new_state
            if isinstance(candidate_payload, dict):
                candidate_payload["funnel_state"] = new_state
            self.session.commit()
        except Exception:  # noqa: BLE001
            self.session.rollback()
            _logger.exception("update_flow_state failed for candidate %s", candidate_id)
            return False

        self.track_state(candidate_id, candidate.company_id, new_state, reason=reason)
        return True

    def track_state(
        self,
        candidate_id: int | None,
        company_id: int | None,
        new_state: str,
        *,
        reason: str | None = None,
    ) -> None:
        if not self.analytics or not candidate_id or not company_id:
            return
        try:
            self.analytics.track(new_state, candidate_id, company_id, reason=reason)
        except Exception:  # noqa: BLE001
            _logger.exception(
                "Failed to track funnel transition candidate=%s state=%s",
                candidate_id,
                new_state,
            )
