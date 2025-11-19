from __future__ import annotations

from dataclasses import dataclass

from baltra_sdk.domain.screening.ports import FunnelAnalytics
from baltra_sdk.shared.mixpanel.metrics_screening import send_funnel_state_mixpanel


@dataclass
class MixpanelFunnelAnalytics(FunnelAnalytics):
    """Adapter that proxies funnel events to Mixpanel."""

    def track(self, event_name: str, candidate_id: int, company_id: int, *, reason: str | None = None) -> None:
        send_funnel_state_mixpanel(candidate_id, event_name, company_id, reason)
