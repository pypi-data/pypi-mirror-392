from __future__ import annotations

import heapq
import logging
from math import cos, radians, sin, sqrt, atan2
from typing import Dict, List, Optional

from baltra_sdk.legacy.dashboards_folder.models import Locations, CompaniesScreening, db
from baltra_sdk.shared.utils.screening.google_maps import LocationService

_logger = logging.getLogger(__name__)


class LocationTransitService:
    def __init__(self, session=None, location_service: Optional[LocationService] = None) -> None:
        self.session = session or db.session
        self._location_service = location_service

    def top_locations_for_company(
        self,
        candidate_lat: float,
        candidate_lon: float,
        company_id: int,
    ) -> List[Dict]:
        locations = self._fetch_company_locations(company_id)
        if not locations:
            return []
        shortlist = self._shortlist_locations(candidate_lat, candidate_lon, locations)
        results = self._transit_filter(candidate_lat, candidate_lon, shortlist)
        if results:
            return results
        return self._fallback_locations(shortlist)

    def top_companies_for_group(
        self,
        candidate_lat: float,
        candidate_lon: float,
        group_id: int,
    ) -> List[Dict]:
        companies = (
            self.session.query(
                CompaniesScreening.company_id,
                CompaniesScreening.name,
                CompaniesScreening.latitude,
                CompaniesScreening.longitude,
            )
            .filter(
                CompaniesScreening.group_id == group_id,
                CompaniesScreening.latitude.isnot(None),
                CompaniesScreening.longitude.isnot(None),
            )
            .all()
        )
        results: List[Dict] = []
        for row in companies:
            lat = float(row.latitude)
            lon = float(row.longitude)
            distance = self._haversine(candidate_lat, candidate_lon, lat, lon)
            if distance <= 35.0:
                results.append(
                    {
                        "company_id": int(row.company_id),
                        "name": row.name,
                        "latitude": lat,
                        "longitude": lon,
                        "haversine_km": distance,
                    }
                )
        if not results:
            return [
                {
                    "rejection_reason": "all_companies_too_far",
                    "message": "Lamentablemente no contamos con vacantes a menos de 35km de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌",
                }
            ]
        return sorted(results, key=lambda x: x["haversine_km"])[:5]

    # ------------------------------------------------------------------
    def _fetch_company_locations(self, company_id: int) -> List[Dict]:
        rows = (
            self.session.query(Locations.location_id, Locations.latitude, Locations.longitude)
            .filter(Locations.company_id == company_id)
            .all()
        )
        return [
            {
                "location_id": int(row.location_id),
                "latitude": float(row.latitude),
                "longitude": float(row.longitude),
            }
            for row in rows
            if row.latitude is not None and row.longitude is not None
        ]

    def _shortlist_locations(
        self,
        candidate_lat: float,
        candidate_lon: float,
        locations: List[Dict],
    ) -> List[Dict]:
        heap: List[tuple[float, Dict]] = []
        for loc in locations:
            distance = self._haversine(candidate_lat, candidate_lon, loc["latitude"], loc["longitude"])
            item = (-distance, loc)
            if len(heap) < 8:
                heapq.heappush(heap, item)
            else:
                if distance < -heap[0][0]:
                    heapq.heapreplace(heap, item)
        shortlist = [loc for _, loc in sorted(heap, key=lambda x: -x[0])]
        for entry in shortlist:
            entry["_haversine_km"] = self._haversine(
                candidate_lat, candidate_lon, entry["latitude"], entry["longitude"]
            )
        return shortlist

    def _transit_filter(
        self,
        candidate_lat: float,
        candidate_lon: float,
        locations: List[Dict],
    ) -> List[Dict]:
        if not locations:
            return []
        destinations = [
            {"id": loc["location_id"], "lat": loc["latitude"], "lng": loc["longitude"]}
            for loc in locations
        ]
        try:
            elements = self._svc().compute_transit_route_matrix(
                {"lat": candidate_lat, "lng": candidate_lon},
                destinations,
            )
        except Exception:
            _logger.exception("Transit matrix call failed")
            elements = []
        if not elements:
            return []
        max_seconds = 200 * 60
        filtered = [
            el for el in elements if el.get("duration_seconds") is not None and el["duration_seconds"] <= max_seconds
        ]
        if not filtered:
            return [
                {
                    "rejection_reason": "all_locations_too_far",
                    "message": "Lamentablemente no contamos con vacantes a menos de 3 horas de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌",
                }
            ]
        by_id = {loc["location_id"]: loc for loc in locations}
        sorted_filtered = sorted(filtered, key=lambda x: x["duration_seconds"])[:5]
        results: List[Dict] = []
        for entry in sorted_filtered:
            loc = by_id.get(entry["id"])
            if not loc:
                continue
            results.append(
                {
                    **loc,
                    "eta_seconds": entry.get("duration_seconds"),
                    "distance_m": entry.get("distance_meters"),
                    "haversine_km": loc.get("_haversine_km"),
                }
            )
        return results

    def _fallback_locations(self, shortlist: List[Dict]) -> List[Dict]:
        fallback = [loc for loc in shortlist if loc.get("_haversine_km", 0) <= 50.0]
        if not fallback:
            return [
                {
                    "rejection_reason": "all_locations_too_far",
                    "message": "Lamentablemente no contamos con vacantes a menos de 50km de tu ubicacion. \n\n Nos comunicaremos contigo si esto cambia 🙌",
                }
            ]
        return fallback[:5]

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def _svc(self) -> LocationService:
        if self._location_service is None:
            self._location_service = LocationService()
        return self._location_service
