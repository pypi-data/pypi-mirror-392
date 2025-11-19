from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from flask import current_app

from baltra_sdk.shared.utils.screening.google_maps import LocationService
from baltra_sdk.shared.utils.screening.company_data import get_company_location

_logger = logging.getLogger(__name__)


class LocationDataService:
    """SOLID-friendly wrapper around location parsing and travel calculations."""

    def __init__(self, location_service: Optional[LocationService] = None) -> None:
        self._location_service = location_service

    def build_location_payload(
        self,
        candidate_payload: Dict[str, Any],
        message: Dict[str, Any],
        message_body: str,
        message_type: Optional[str],
    ) -> Dict[str, Any] | None:
        employee_coords, source = self._extract_employee_coords(message, message_body, message_type)
        if employee_coords is None:
            return {
                "employee_coordinates": {"latitude": None, "longitude": None},
                "company_coordinates": {"latitude": None, "longitude": None},
                "location_source": source,
                "input_data": message_body if message_body else "WhatsApp Location",
            }

        company_location = get_company_location(candidate_payload.get("company_id"))
        if not company_location:
            _logger.warning("Missing company location for company %s", candidate_payload.get("company_id"))
            return {
                "employee_coordinates": employee_coords,
                "company_coordinates": {"latitude": None, "longitude": None},
                "location_source": source,
                "input_data": message_body if message_body else "WhatsApp Location",
            }

        travel_data = self._compute_travel_time(employee_coords, company_location)
        if travel_data:
            travel_data.update(
                {
                    "candidate_id": candidate_payload.get("candidate_id"),
                    "company_id": candidate_payload.get("company_id"),
                    "employee_coordinates": employee_coords,
                    "company_coordinates": company_location,
                    "location_source": source,
                    "input_data": message_body if source == "text_address" else "WhatsApp Location",
                }
            )
            return travel_data

        return {
            "employee_coordinates": employee_coords,
            "company_coordinates": company_location,
            "location_source": source,
            "input_data": message_body if message_body else "WhatsApp Location",
            "duration_text": None,
            "distance_text": None,
        }

    def _extract_employee_coords(
        self,
        message: Dict[str, Any],
        message_body: str,
        message_type: Optional[str],
    ) -> tuple[Optional[Dict[str, float]], str]:
        if message_type == "location" and message.get("location"):
            loc = message["location"]
            if "latitude" in loc and "longitude" in loc:
                return {"latitude": loc["latitude"], "longitude": loc["longitude"]}, "whatsapp_coordinates"
            _logger.error("Invalid WhatsApp location payload: %s", loc)
            return {"latitude": None, "longitude": None}, "whatsapp_coordinates"

        if message_body and message_body.strip():
            try:
                geodata = self._svc().get_geolocation(message_body.strip(), "address")
            except Exception:
                _logger.exception("Failed to geocode address %s", message_body)
                geodata = None
            if geodata and geodata.get("position"):
                pos = geodata["position"]
                return {"latitude": pos["lat"], "longitude": pos["lng"]}, "text_address"
            return {"latitude": None, "longitude": None}, "text_address"

        return {"latitude": None, "longitude": None}, "unknown"

    def _compute_travel_time(self, employee_coords: Dict[str, float], company_coords: Dict[str, float]) -> Dict[str, Any] | None:
        for mode in ("transit", "driving"):
            try:
                data = self._svc().get_travel_time_by_coords(employee_coords, company_coords, mode)
            except Exception:
                _logger.exception("Travel time API failed for mode %s", mode)
                continue
            if not data:
                continue
            if mode == "transit" and data.get("duration_minutes", 0) > 200:
                continue
            return data
        return None

    def _svc(self) -> LocationService:
        if self._location_service is None:
            self._location_service = LocationService()
        return self._location_service
