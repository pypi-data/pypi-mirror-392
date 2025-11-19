from __future__ import annotations

import logging
from typing import Dict, List, Optional

from baltra_sdk.legacy.dashboards_folder.models import Roles, db

_logger = logging.getLogger(__name__)


class RoleLookupService:
    def __init__(self, session=None) -> None:
        self.session = session or db.session

    def get_roles_for_locations(self, company_id: int, location_ids: List[int]) -> Dict[int, Dict[str, int | str]]:
        if not location_ids:
            return {}
        try:
            rows = (
                self.session.query(Roles.location_id, Roles.role_id, Roles.role_name)
                .filter(Roles.company_id == company_id)
                .filter(Roles.active.is_(True))
                .filter(Roles.location_id.in_(location_ids))
                .all()
            )
            mapping: Dict[int, Dict[str, int | str]] = {}
            for row in rows:
                if row.location_id is None or row.location_id in mapping:
                    continue
                mapping[int(row.location_id)] = {"role_id": int(row.role_id), "role_name": row.role_name}
            return mapping
        except Exception:  # noqa: BLE001
            _logger.exception("Failed to load roles for company %s", company_id)
            return {}
