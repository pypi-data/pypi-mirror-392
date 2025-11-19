from typing import Any, Dict, List

from sqlalchemy import func

from baltra_sdk.domain.ads_wizard.ports import CompanyRolesRepository
from baltra_sdk.legacy.dashboards_folder.models import Roles, Locations, db


class SqlAlchemyCompanyRolesRepository(CompanyRolesRepository):

    def list_roles_for_company(self, company_id: int) -> List[Dict[str, Any]]:
        roles = (
            db.session.query(Roles, Locations)
            .outerjoin(Locations, Locations.location_id == Roles.location_id)
            .filter(
                Roles.company_id == company_id,
                Roles.active.is_(True),
                Roles.is_deleted.is_(False),
            )
            .order_by(func.lower(Roles.role_name))
            .all()
        )

        result: List[Dict[str, Any]] = []
        for role, location in roles:
            result.append(
                {
                    "role_id": role.role_id,
                    "company_id": role.company_id,
                    "name": role.role_name,
                    "role_info": role.role_info or {},
                    "shift": role.shift,
                    "set_id": role.set_id,
                    "default_role": bool(role.default_role),
                    "location": {
                        "location_id": location.location_id if location else None,
                        "address": location.address if location else None,
                        "latitude": location.latitude if location else None,
                        "longitude": location.longitude if location else None,
                    }
                }
            )

        return result
