from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from baltra_sdk.domain.screening.entities import CandidateSnapshot, ScreeningResult, OutboundMessage
from baltra_sdk.infra.screening.repositories.sqlalchemy_candidate_repository import SqlAlchemyCandidateRepository
from baltra_sdk.infra.screening.services.candidate_state_service import CandidateStateService
from baltra_sdk.infra.screening.services.location_data_service import LocationDataService
from baltra_sdk.infra.screening.services.location_transit_service import LocationTransitService
from baltra_sdk.infra.screening.services.role_lookup_service import RoleLookupService
from baltra_sdk.shared.utils.screening.whatsapp_messages import get_text_message_input

_logger = logging.getLogger(__name__)


@dataclass
class LocationHandlingResult:
    handled: bool
    stop_processing: bool = False
    snapshot: Optional[CandidateSnapshot] = None
    result: Optional[ScreeningResult] = None


class LocationAnswerHandler:
    """Processes location-based answers for the SOLID flow."""

    def __init__(
        self,
        candidate_repo: SqlAlchemyCandidateRepository,
        candidate_state: Optional[CandidateStateService] = None,
        location_data: Optional[LocationDataService] = None,
        transit_service: Optional[LocationTransitService] = None,
        role_lookup: Optional[RoleLookupService] = None,
    ) -> None:
        self.candidates = candidate_repo
        self.candidate_state = candidate_state or CandidateStateService()
        self.location_data = location_data or LocationDataService()
        self.transit_service = transit_service or LocationTransitService()
        self.role_lookup = role_lookup or RoleLookupService()

    def handle(
        self,
        snapshot: CandidateSnapshot,
        message: Dict[str, Any],
        message_body: str,
        message_type: Optional[str],
    ) -> LocationHandlingResult:
        response_type = snapshot.raw_payload.get("current_response_type")
        if response_type not in {"location", "location_critical", "location_critical_company"}:
            return LocationHandlingResult(handled=False)
        _logger.debug(
            "[SOLID 5.1] LocationAnswerHandler.handle candidate=%s response_type=%s message_type=%s",
            snapshot.candidate_id,
            response_type,
            message_type,
        )

        json_body = self.location_data.build_location_payload(
            snapshot.raw_payload, message, message_body, message_type
        )
        if json_body and json_body.get("error"):
            return self._error_response(snapshot, json_body.get("error"))

        if not self.candidate_state.store_location_answer(snapshot.raw_payload, message_body, json_body):
            _logger.warning("[SOLID 5.1] Failed to persist location answer for candidate %s", snapshot.candidate_id)

        if json_body:
            processor = (
                self._process_company_locations
                if response_type == "location_critical"
                else self._process_group_locations
            )
            outcome = processor(snapshot, json_body)
            if outcome:
                return outcome

        refreshed = self.candidates.get_or_create(snapshot.wa_id_user, snapshot.wa_id_system)
        conversation_id = snapshot.raw_payload.get("conversation_id")
        conversation_priority = snapshot.raw_payload.get("conversation_priority")
        if conversation_id:
            refreshed.raw_payload["conversation_id"] = conversation_id
        if conversation_priority:
            refreshed.raw_payload["conversation_priority"] = conversation_priority
        return LocationHandlingResult(handled=True, snapshot=refreshed)

    # ------------------------------------------------------------------
    def _error_response(self, snapshot: CandidateSnapshot, error_code: str) -> LocationHandlingResult:
        messages = {
            "address_not_found": "No pude encontrar esa dirección. ¿Podrías intentar con una dirección más específica?",
            "geocoding_failed": "Hubo un problema al procesar tu dirección. ¿Podrías intentar de nuevo con una dirección más detallada?",
            "no_location_data": "No recibí información de ubicación. Por favor comparte tu ubicación o escribe tu dirección completa.",
        }
        response = messages.get(error_code, "Hubo un problema al procesar tu ubicación. ¿Podrías intentar de nuevo?")
        payload = get_text_message_input(snapshot.wa_id_user, response)
        return LocationHandlingResult(
            handled=True,
            stop_processing=True,
            snapshot=snapshot,
            result=self._result_from_payload(snapshot, payload, response),
        )

    def _process_company_locations(
        self,
        snapshot: CandidateSnapshot,
        json_body: Dict[str, Any],
    ) -> Optional[LocationHandlingResult]:
        coords = self._extract_coords(json_body)
        company_id = snapshot.raw_payload.get("company_id")
        if not coords or not company_id:
            return None

        top5 = self.transit_service.top_locations_for_company(coords[0], coords[1], company_id) or []
        if top5 and len(top5) == 1 and top5[0].get("rejection_reason") == "all_locations_too_far":
            return self._reject_candidate(snapshot, top5[0].get("message"))

        location_ids = [int(row["location_id"]) for row in top5]
        loc_roles = self.role_lookup.get_roles_for_locations(company_id, location_ids)
        nearest_roles = []
        for entry in top5:
            role_info = loc_roles.get(int(entry["location_id"]))
            if role_info:
                nearest_roles.append(
                    {
                        "role_id": role_info["role_id"],
                        "role_name": role_info["role_name"],
                        "eta_seconds": entry.get("eta_seconds"),
                    }
                )

        if nearest_roles:
            snapshot.raw_payload["nearest_roles"] = nearest_roles
            self.candidate_state.update_eligible_roles(
                snapshot.candidate_id,
                [role["role_id"] for role in nearest_roles][:5],
            )
        return None

    def _process_group_locations(
        self,
        snapshot: CandidateSnapshot,
        json_body: Dict[str, Any],
    ) -> Optional[LocationHandlingResult]:
        coords = self._extract_coords(json_body)
        group_id = snapshot.raw_payload.get("company_group_id")
        if not coords or not group_id:
            return None
        top5 = self.transit_service.top_companies_for_group(coords[0], coords[1], group_id) or []
        if top5 and len(top5) == 1 and top5[0].get("rejection_reason") == "all_companies_too_far":
            return self._reject_candidate(snapshot, top5[0].get("message"))

        snapshot.raw_payload["nearest_companies"] = top5
        self.candidate_state.update_eligible_companies(
            snapshot.candidate_id,
            [entry.get("company_id") for entry in top5][:5],
        )
        return None

    def _reject_candidate(self, snapshot: CandidateSnapshot, message: Optional[str]) -> LocationHandlingResult:
        rejection_message = message or "No contamos con vacantes a menos de 3 horas de tu ubicacion"
        if snapshot.candidate_id:
            self.candidate_state.mark_flow_rejected(snapshot.candidate_id, "Muy lejos de vacante")
            snapshot.raw_payload["funnel_state"] = "rejected"
        payload = get_text_message_input(snapshot.wa_id_user, rejection_message)
        return LocationHandlingResult(
            handled=True,
            stop_processing=True,
            snapshot=snapshot,
            result=self._result_from_payload(snapshot, payload, rejection_message),
        )

    @staticmethod
    def _extract_coords(json_body: Dict[str, Any]) -> Optional[tuple[float, float]]:
        employee = json_body.get("employee_coordinates") or {}
        if employee and employee.get("latitude") is not None and employee.get("longitude") is not None:
            return float(employee["latitude"]), float(employee["longitude"])
        position = json_body.get("position") or {}
        if position and position.get("lat") is not None and position.get("lng") is not None:
            return float(position["lat"]), float(position["lng"])
        return None

    def _result_from_payload(
        self,
        snapshot: CandidateSnapshot,
        payload: dict | str,
        text_response: str,
    ) -> ScreeningResult:
        return ScreeningResult(
            outbound_messages=[OutboundMessage(payload=payload)],
            candidate_data=snapshot.raw_payload,
            sent_by="assistant",
            raw_response_text=text_response,
        )
